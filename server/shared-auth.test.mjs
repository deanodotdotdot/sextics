import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, mkdir, writeFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { Auth } from './auth.mjs';
import { createService } from './server.mjs';
import { bridge } from './lambda-bridge.mjs';

class Store {
  rows = new Map();
  async put(k, v) {
    assert(!this.rows.has(k));
    this.rows.set(k, structuredClone(v));
  }
  async get(k) {
    return structuredClone(this.rows.get(k) || null);
  }
  async consume(k) {
    const row = this.rows.get(k);
    this.rows.delete(k);
    return row?.expires > Date.now() ? structuredClone(row) : null;
  }
  async remove(k) {
    this.rows.delete(k);
  }
  async claimPost(k, now) {
    const row = this.rows.get(k);
    if (!row || row.expires <= now || row.lastPost > now - 5000) return false;
    row.lastPost = now;
    return true;
  }
}
const origin = 'https://hodge.example.test';
test('separate Lambda invocations share sessions; concurrent OAuth completion has one winner', async () => {
  const store = new Store(),
    a = new Auth(origin, store),
    b = new Auth(origin, store);
  const flow = await a.start('/#case/holdout');
  const finished = await Promise.allSettled([
    a.finish(flow.state, flow.cookie),
    b.finish(flow.state, flow.cookie)
  ]);
  assert.equal(finished.filter((r) => r.status === 'fulfilled').length, 1);
  const created = await a.create(
    { access_token: 'private-user-token', expires_in: 600 },
    { login: 'alice' }
  );
  const cookie = created.cookies[0],
    session = await b.get(cookie);
  assert.equal(session.user.login, 'alice');
  assert([...store.rows.keys()].every((k) => !k.includes(created.id)));
  const claimed = await Promise.allSettled([a.claimPost(session), b.claimPost(session)]);
  assert.equal(claimed.filter((r) => r.status === 'fulfilled').length, 1);
  await b.remove(cookie);
  assert.equal(await a.get(cookie), null);
});
test('expiry is enforced before TTL cleanup; wrong browser binding cannot log in', async () => {
  const store = new Store(),
    auth = new Auth(origin, store),
    flow = await auth.start('/#home');
  await assert.rejects(auth.finish(flow.state, ''), (e) => e.status === 400);
  const next = await auth.start('/#home');
  for (const row of store.rows.values()) row.expires = 0;
  await assert.rejects(auth.finish(next.state, next.cookie), (e) => e.status === 400);
  const c = await auth.create({ access_token: 'secret' }, { login: 'alice' });
  for (const row of store.rows.values()) row.expires = 0;
  assert.equal(await auth.get(c.cookies[0]), null);
  assert.equal(await auth.get('__Host-hodge_session=invalid'), null);
});
test('HTTP API events complete OAuth across cold services, preserve cookies, and reject replay and CSRF', async () => {
  const root = await mkdtemp(path.join(tmpdir(), 'hodge-lambda-test-'));
  await mkdir(path.join(root, 'data'));
  await writeFile(
    path.join(root, 'data/catalogue.json'),
    JSON.stringify({ instanceIds: ['holdout'] })
  );
  const store = new Store(),
    config = { client_id: 'test-client' },
    github = {
      exchange: async () => ({ access_token: 'never-public' }),
      viewer: async () => ({ login: 'alice' })
    };
  const invoke = async (
    method,
    rawPath,
    rawQueryString = '',
    cookie = '',
    headers = {},
    body = ''
  ) => {
    const svc = await createService({
      root,
      origin,
      appConfig: config,
      github,
      auth: new Auth(origin, store),
      apiOnly: true
    });
    return bridge(svc.handler)({
      version: '2.0',
      requestContext: { http: { method } },
      rawPath,
      rawQueryString,
      cookies: cookie ? [cookie] : [],
      headers,
      body
    });
  };
  try {
    const start = await invoke('GET', '/auth/github');
    assert.equal(start.statusCode, 303);
    const state = new URL(start.headers.Location).searchParams.get('state'),
      flowCookie = start.cookies[0].split(';')[0];
    const callback = await invoke(
      'GET',
      '/auth/github/callback',
      'code=test&state=' + state,
      flowCookie
    );
    assert.equal(callback.statusCode, 303);
    assert.equal(callback.cookies.length, 2);
    const cookie = callback.cookies[0].split(';')[0],
      session = await invoke('GET', '/api/session', '', cookie);
    assert(!session.body.includes('never-public'));
    const data = JSON.parse(session.body);
    assert.equal(data.user.login, 'alice');
    assert.equal(
      (await invoke('GET', '/auth/github/callback', 'code=test&state=' + state, flowCookie))
        .statusCode,
      400
    );
    assert.equal(
      (
        await invoke(
          'POST',
          '/api/sign-out',
          '',
          cookie,
          {
            origin: 'https://evil.test',
            'content-type': 'application/json',
            'x-csrf-token': data.csrf
          },
          '{}'
        )
      ).statusCode,
      403
    );
    assert.equal(
      (
        await invoke(
          'POST',
          '/api/sign-out',
          '',
          cookie,
          { origin: origin, 'content-type': 'application/json', 'x-csrf-token': data.csrf },
          '{}'
        )
      ).statusCode,
      200
    );
    assert.equal(JSON.parse((await invoke('GET', '/api/session', '', cookie)).body).user, null);
    assert.equal((await invoke('GET', '/auth/setup')).statusCode, 404);
    assert.equal((await invoke('GET', '/data/catalogue.json')).statusCode, 404);
  } finally {
    await rm(root, { recursive: true, force: true });
  }
});
