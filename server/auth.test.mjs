import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, writeFile, mkdir, symlink, rm, readFile, stat } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { Auth, returnPath } from './auth.mjs';
import { createService } from './server.mjs';
const origin = 'https://preview.example.test';
test('OAuth flow binds browser cookie, expires, and cannot be replayed', async () => {
  const auth = new Auth(origin),
    flow = await auth.start('/#case/holdout');
  assert.equal(flow.challenge.length, 43);
  assert.match(flow.cookie, /HttpOnly; SameSite=Lax/);
  assert.match(flow.cookie, /Secure/);
  await assert.rejects(() => auth.finish(flow.state, ''));
  const next = await auth.start('/#case/holdout'),
    verified = await auth.finish(next.state, next.cookie);
  assert.equal(verified.returnTo, '/#case/holdout');
  assert.equal(verified.verifier.length, 43);
  await assert.rejects(() => auth.finish(next.state, next.cookie));
  const expired = await auth.start('/#home');
  for (const row of auth.store.rows.values()) row.expires = Date.now() - 1;
  await assert.rejects(() => auth.finish(expired.state, expired.cookie));
});
test('app registration is gated, browser-bound, and stores credentials outside the site once', async () => {
  const root = await mkdtemp(path.join(tmpdir(), 'hodge-setup-test-'));
  const outside = await mkdtemp(path.join(tmpdir(), 'hodge-setup-config-'));
  await mkdir(path.join(root, 'data'));
  await writeFile(
    path.join(root, 'data/catalogue.json'),
    JSON.stringify({ instanceIds: ['holdout'] })
  );
  const configFile = path.join(outside, 'app.json');
  let conversions = 0;
  const service = await createService({
    root,
    origin,
    setupOrigin: 'http://127.0.0.1:8772',
    configFile,
    setupToken: 'local-test-key',
    request: async (url, options) => {
      assert.equal(url, 'https://api.github.com/app-manifests/test-code/conversions');
      assert.equal(options.method, 'POST');
      conversions++;
      return Response.json({
        id: 123,
        slug: 'test-discussion-app',
        client_id: 'test-client',
        client_secret: 'never-public-secret',
        pem: 'never-public-key'
      });
    }
  });
  await new Promise((resolve) => service.server.listen(0, '127.0.0.1', resolve));
  const base = 'http://127.0.0.1:' + service.server.address().port;
  try {
    for (const suffix of ['', '?key=wrong'])
      assert.equal((await fetch(base + '/auth/setup' + suffix)).status, 404);
    const start = await fetch(base + '/auth/setup?key=local-test-key'),
      html = await start.text();
    assert.equal(start.status, 200);
    assert(html.includes('github.com/organizations/hodge-computer/settings/apps/new'));
    assert(html.includes('http://127.0.0.1:8772/auth/setup/callback'));
    assert(html.includes(origin + '/auth/github/callback'));
    assert(!start.headers.get('set-cookie').includes('Secure'));
    const state = html.match(/apps\/new\?state=([A-Za-z0-9_-]+)/)[1];
    const cookie = start.headers.get('set-cookie').split(';')[0];
    const callback = await fetch(base + '/auth/setup/callback?code=test-code&state=' + state, {
        headers: { cookie }
      }),
      body = await callback.text();
    assert.equal(callback.status, 200);
    assert(body.includes('https://github.com/apps/test-discussion-app/installations/new'));
    assert(!body.includes('never-public'));
    const saved = JSON.parse(await readFile(configFile, 'utf8'));
    assert.equal(saved.repository, 'hodge-computer/sextics');
    assert.equal(saved.client_secret, 'never-public-secret');
    assert.equal((await stat(configFile)).mode & 0o777, 0o600);
    assert.equal((await fetch(base + '/auth/setup?key=local-test-key')).status, 404);
    assert.equal(
      (
        await fetch(base + '/auth/setup/callback?code=test-code&state=' + state, {
          headers: { cookie }
        })
      ).status,
      404
    );
    assert.equal(conversions, 1);
    const session = await (await fetch(base + '/api/session')).json();
    assert.equal(session.connected, true);
    assert.equal(session.user, null);
  } finally {
    await new Promise((resolve) => service.server.close(resolve));
    await rm(root, { recursive: true, force: true });
    await rm(outside, { recursive: true, force: true });
  }
});
test('return targets cannot redirect off site', () => {
  for (const value of ['https://evil.test', '//evil.test', '/#home?next=evil', '/auth/setup'])
    assert.equal(returnPath(value), '/#home');
  assert.equal(returnPath('/#case/family-block-cube'), '/#case/family-block-cube');
});
test('write requests require session, exact origin, CSRF token, and JSON', async () => {
  const auth = new Auth(origin),
    created = await auth.create({ access_token: 'test-only', expires_in: 60 }, { login: 'tester' }),
    session = await auth.get(created.cookies.join(';'));
  assert.throws(() => auth.requireWrite({ headers: {} }, null));
  for (const headers of [
    { origin },
    { origin, 'x-csrf-token': 'wrong' },
    {
      origin: 'https://evil.test',
      'x-csrf-token': session.csrf,
      'content-type': 'application/json'
    }
  ])
    assert.throws(() => auth.requireWrite({ headers }, session));
  auth.requireWrite(
    { headers: { origin, 'x-csrf-token': session.csrf, 'content-type': 'application/json' } },
    session
  );
  await auth.remove(created.cookies.join(';'));
  assert.equal(await auth.get(created.cookies.join(';')), null);
});
test('real HTTP OAuth callback, session, sign out, static boundaries, and catalogue schema', async () => {
  const root = await mkdtemp(path.join(tmpdir(), 'hodge-auth-test-'));
  const outside = await mkdtemp(path.join(tmpdir(), 'hodge-auth-config-'));
  await mkdir(path.join(root, 'data'));
  await mkdir(path.join(root, 'assets'));
  await mkdir(path.join(root, 'docs'));
  await writeFile(path.join(root, 'docs/index.json'), JSON.stringify({ pages: [] }));
  await writeFile(path.join(root, 'docs/overview.html'), '<p>The mathematical book.</p>');
  await writeFile(path.join(root, 'MAINTAINING.md'), 'Repository operations');
  await writeFile(
    path.join(root, 'data/catalogue.json'),
    JSON.stringify({ schemaVersion: 2, instanceIds: ['holdout'] })
  );
  await writeFile(path.join(root, 'index.html'), '<h1>Test</h1>');
  await writeFile(path.join(outside, 'secret.txt'), 'not public');
  await symlink(path.join(outside, 'secret.txt'), path.join(root, 'assets/leak.md'));
  const configFile = path.join(outside, 'app.json');
  await writeFile(
    configFile,
    JSON.stringify({
      repository: 'hodge-computer/sextics',
      client_id: 'test-client',
      client_secret: 'test-secret'
    })
  );
  const github = {
    exchange: async (code, verifier, redirect) => {
      assert.equal(code, 'test-code');
      assert.equal(verifier.length, 43);
      assert.equal(redirect, origin + '/auth/github/callback');
      return { access_token: 'must-stay-on-server', expires_in: 60 };
    },
    viewer: async (token) => {
      assert.equal(token, 'must-stay-on-server');
      return {
        login: 'tester',
        name: 'Test User',
        avatar: 'https://avatars.githubusercontent.com/u/1',
        url: 'https://github.com/tester'
      };
    }
  };
  const service = await createService({ root, origin, configFile, github });
  await new Promise((resolve) => service.server.listen(0, '127.0.0.1', resolve));
  const base = 'http://127.0.0.1:' + service.server.address().port;
  try {
    const start = await fetch(
      base + '/auth/github?returnTo=' + encodeURIComponent('/#case/holdout'),
      { redirect: 'manual' }
    );
    assert.equal(start.status, 303);
    const target = new URL(start.headers.get('location'));
    assert.equal(target.origin, 'https://github.com');
    assert.equal(target.searchParams.get('code_challenge_method'), 'S256');
    const cookie = start.headers.get('set-cookie').split(';')[0];
    const callback = await fetch(
      base + '/auth/github/callback?code=test-code&state=' + target.searchParams.get('state'),
      { headers: { cookie }, redirect: 'manual' }
    );
    assert.equal(callback.status, 303);
    assert.equal(callback.headers.get('location'), '/#case/holdout');
    const sessionCookie = callback.headers.getSetCookie()[0].split(';')[0];
    const response = await fetch(base + '/api/session', { headers: { cookie: sessionCookie } }),
      body = await response.text();
    assert(!body.includes('must-stay-on-server'));
    const data = JSON.parse(body);
    assert.equal(data.user.login, 'tester');
    assert.equal(
      (
        await fetch(base + '/api/sign-out', {
          method: 'POST',
          headers: { cookie: sessionCookie, 'Content-Type': 'application/json' },
          body: '{}'
        })
      ).status,
      403
    );
    assert.equal(
      (
        await fetch(base + '/api/sign-out', {
          method: 'POST',
          headers: {
            cookie: sessionCookie,
            Origin: origin,
            'Content-Type': 'application/json',
            'X-CSRF-Token': data.csrf
          },
          body: '{}'
        })
      ).status,
      200
    );
    assert.equal(
      (await (await fetch(base + '/api/session', { headers: { cookie: sessionCookie } })).json())
        .user,
      null
    );
    assert.deepEqual(await (await fetch(base + '/docs/index.json')).json(), { pages: [] });
    assert.equal(
      await (await fetch(base + '/docs/overview.html')).text(),
      '<p>The mathematical book.</p>'
    );
    for (const url of [
      '/server/auth.mjs',
      '/.git/config',
      '/assets/leak.md',
      '/auth/setup',
      '/MAINTAINING.md'
    ])
      assert.equal((await fetch(base + url)).status, 404);
    assert.equal((await fetch(base + '/api/discussions/holdout')).status, 503);
    assert.equal((await fetch(base + '/api/discussions/unknown')).status, 404);
  } finally {
    await new Promise((resolve) => service.server.close(resolve));
    await rm(root, { recursive: true, force: true });
    await rm(outside, { recursive: true, force: true });
  }
});

test('sign-in preserves supported discussion, ranking and chapter destinations', () => {
  for (const route of [
    '/#case/holdout/discussion',
    '/#case/holdout/discussion/123',
    '/#leaderboard/fqlx/comments',
    '/#technical-information/computation/heading'
  ])
    assert.equal(returnPath(route), route);
});
test('session creation rejects missing tokens and expired token responses', async () => {
  const auth = new Auth(origin);
  for (const tokens of [{}, { access_token: '' }, { access_token: 'synthetic', expires_in: -1 }])
    await assert.rejects(auth.create(tokens, { login: 'tester' }), (e) => e.status === 401);
  assert.equal(auth.store.rows.size, 0);
});
