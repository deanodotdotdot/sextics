import test from 'node:test';
import assert from 'node:assert/strict';
import { RequestCache } from './cache.mjs';
import { GitHub } from './github.mjs';

test('cache separates keys, coalesces slow requests, and expires from completion', async (t) => {
  t.mock.timers.enable({ apis: ['Date'], now: 1000 });
  const cache = new RequestCache(100, 2);
  let complete,
    calls = 0;
  const load = () => {
    calls++;
    return new Promise((resolve) => {
      complete = resolve;
    });
  };
  const first = cache.get('reader-a', load);
  await Promise.resolve();
  t.mock.timers.tick(1000);
  assert.equal(cache.get('reader-a', load), first);
  assert.equal(await cache.get('reader-b', () => 'b'), 'b');
  complete('a');
  assert.equal(await first, 'a');
  assert.equal(await cache.get('reader-a', load), 'a');
  assert.equal(calls, 1);
  t.mock.timers.tick(101);
  assert.equal(await cache.get('reader-a', () => 'new'), 'new');
});

test('cache bounds pending work and retries failures without resurrecting invalidated entries', async () => {
  const cache = new RequestCache(100, 1);
  let complete;
  const old = cache.get(
    'a',
    () =>
      new Promise((resolve) => {
        complete = resolve;
      })
  );
  await Promise.resolve();
  await assert.rejects(
    cache.get('b', () => 'b'),
    /Too many/
  );
  cache.clear();
  assert.equal(await cache.get('a', () => 'current'), 'current');
  complete('old');
  await old;
  assert.equal(await cache.get('a', () => 'wrong'), 'current');
  await assert.rejects(
    cache.get('b', () => {
      throw Error('failed');
    }),
    /failed/
  );
  assert.equal(await cache.get('b', () => 'retry'), 'retry');
});

test('GitHub bounds upstream concurrency across callers and releases slots after failures', async () => {
  let active = 0,
    peak = 0;
  const pending = [];
  const github = new GitHub({}, async () => {
    active++;
    peak = Math.max(peak, active);
    await new Promise((resolve) => pending.push(resolve));
    active--;
    return Response.json({ ok: true });
  });
  const requests = Array.from({ length: 12 }, () => github.call('/test', { token: 'synthetic' }));
  while (github.activeRequests) {
    pending.splice(0).forEach((resolve) => resolve());
    await new Promise((resolve) => setImmediate(resolve));
  }
  await Promise.all(requests);
  assert.equal(peak, 4);
  github.request = async () => {
    throw Error('network');
  };
  await assert.rejects(github.call('/test'), /network/);
  assert.equal(github.activeRequests, 0);
});
