import test from 'node:test';
import assert from 'node:assert/strict';
import {
  readCommentLeaderboard,
  readContributorComments,
  readProfiles,
  invalidateCommentLeaderboard
} from './comment-leaderboard.mjs';
const entries = { a: { nodeId: 'D_a', number: 1 }, b: { nodeId: 'D_b', number: 2 } };
const page = (nodes, endCursor = null) => ({
  nodes,
  pageInfo: { hasNextPage: !!endCursor, endCursor }
});
const comment = (id, login, day, extra = {}) => ({
  id,
  url: 'https://github.com/hodge-computer/sextics/discussions/1#discussioncomment-' + id.slice(1),
  createdAt: `2026-10-${day}T00:00:00Z`,
  updatedAt: '2026-10-22T00:00:00Z',
  author: {
    login,
    name: login + ' Name',
    avatarUrl: 'https://avatars.githubusercontent.com/' + login,
    url: 'https://github.com/' + login
  },
  isMinimized: false,
  ...extra
});
function fixture() {
  let allowed = true,
    token = 'public',
    reads = 0,
    queries = 0,
    body = 'First wording',
    deleted = false,
    hidden = false;
  const c1 = comment('C1', 'alice', '01', { replies: { totalCount: 2 } }),
    c2 = comment('C2', 'bob', '02', { replies: { totalCount: 0 } }),
    c3 = comment('C3', 'bob', '03'),
    c4 = comment('C4', 'alice', '04');
  const github = {
    readToken: async () => {
      reads++;
      if (!allowed) throw Error('Denied');
      return token;
    },
    graphql: async (query, vars, used) => {
      queries++;
      assert.equal(used, token);
      if (query.includes(' body ')) {
        assert.deepEqual(vars.ids, ['C1', 'C4']);
        return {
          nodes: [
            { ...c1, body, discussion: { id: 'D_a' } },
            deleted
              ? null
              : { ...c4, body: 'Reply', isMinimized: hidden, discussion: { id: 'D_a' } }
          ]
        };
      }
      assert(!/\bbody\b/.test(query));
      if (vars.ids?.includes('D_a'))
        return {
          nodes: [
            { id: 'D_a', comments: page([c1], 'p2') },
            { id: 'D_b', comments: page([]) },
            { id: 'D_unmapped', comments: page([comment('C9', 'intruder', '01')]) }
          ]
        };
      if (vars.after === 'p2') return { node: { id: 'D_a', comments: page([c2]) } };
      if (vars.ids?.[0] === 'C1') return { nodes: [{ id: 'C1', replies: page([c3], 'r2') }] };
      if (vars.after === 'r2')
        return {
          node: { id: 'C1', replies: page(deleted ? [] : [{ ...c4, isMinimized: hidden }]) }
        };
      throw Error('Unexpected query');
    }
  };
  return {
    github,
    get reads() {
      return reads;
    },
    get queries() {
      return queries;
    },
    set denied(v) {
      allowed = !v;
    },
    set token(v) {
      token = v;
    },
    set body(v) {
      body = v;
    },
    set deleted(v) {
      deleted = v;
    },
    set hidden(v) {
      hidden = v;
    }
  };
}
test('counts every parent and reply page, breaks ties by seniority, and never requests bodies', async () => {
  const f = fixture(),
    data = await readCommentLeaderboard(f.github, entries, null);
  assert.deepEqual(
    data.rows.map((r) => [r.githubLogin, r.score, r.rank]),
    [
      ['bob', 2, 1],
      ['alice', 2, 2]
    ]
  );
  assert.equal(data.rows[0].reachedCountAt, '2026-10-03T00:00:00Z');
  assert(!JSON.stringify(data).includes('comments'));
  assert(!JSON.stringify(data).includes('body'));
  const calls = f.queries;
  await readCommentLeaderboard(f.github, entries, null);
  assert.equal(f.queries, calls);
  assert.equal(f.reads, 2);
  f.token = 'different-user';
  await readCommentLeaderboard(f.github, entries, {});
  assert(f.queries > calls);
  f.denied = true;
  await assert.rejects(readCommentLeaderboard(f.github, entries, null), /Denied/);
});
test('selected bodies are fresh, deleted and minimized comments vanish, counts follow invalidation', async () => {
  const f = fixture();
  assert.equal(
    (await readContributorComments(f.github, entries, 'ALICE', null)).comments[1].body,
    'First wording'
  );
  f.body = 'Edited wording';
  assert.equal(
    (await readContributorComments(f.github, entries, 'alice', null)).comments[1].body,
    'Edited wording'
  );
  f.hidden = true;
  assert.equal(
    (await readContributorComments(f.github, entries, 'alice', null)).comments.length,
    1
  );
  assert.deepEqual(
    (await readCommentLeaderboard(f.github, entries, null)).rows.map((r) => r.score),
    [2, 1]
  );
  f.hidden = false;
  f.deleted = true;
  invalidateCommentLeaderboard(f.github);
  assert.deepEqual(
    (await readCommentLeaderboard(f.github, entries, null)).rows.map((r) => r.score),
    [2, 1]
  );
  await assert.rejects(
    readContributorComments(f.github, entries, '../secret', null),
    (e) => e.status === 400
  );
});
test('expired metadata refreshes automatically without a deploy or invalidation', async (t) => {
  t.mock.timers.enable({ apis: ['Date'], now: 10000 });
  const f = fixture();
  assert.equal((await readCommentLeaderboard(f.github, entries, null)).rows[1].score, 2);
  f.deleted = true;
  t.mock.timers.tick(15001);
  assert.equal((await readCommentLeaderboard(f.github, entries, null)).rows[1].score, 1);
});
test('concurrent readers share collection, malformed pagination fails without caching partial counts', async () => {
  const f = fixture();
  await Promise.all([
    readCommentLeaderboard(f.github, entries, null),
    readCommentLeaderboard(f.github, entries, null)
  ]);
  assert.equal(f.queries, 4);
  let calls = 0;
  const github = {
    readToken: async () => 'token',
    graphql: async () => {
      calls++;
      return {
        nodes: [
          { id: 'D_a', comments: { nodes: [], pageInfo: { hasNextPage: true, endCursor: null } } }
        ]
      };
    }
  };
  for (let i = 0; i < 2; i++)
    await assert.rejects(readCommentLeaderboard(github, entries, null), (e) => e.status === 502);
  assert.equal(calls, 2);
});
test('profiles are uniformly fetched from GitHub and cache never bypasses access checks', async () => {
  let reads = 0,
    calls = 0,
    allowed = true;
  const github = {
    readToken: async () => {
      reads++;
      if (!allowed) throw Error('Denied');
      return 'token';
    },
    call: async (path) => {
      calls++;
      assert.equal(path, '/users/alice');
      return {
        login: 'alice',
        name: 'Alice',
        avatar_url: 'https://avatars.githubusercontent.com/u/1',
        html_url: 'https://github.com/alice'
      };
    }
  };
  const value = await readProfiles(github, ['alice'], null, new Set(['alice']));
  assert.equal(value.accounts[0].name, 'Alice');
  await readProfiles(github, ['alice'], null, new Set(['alice']));
  assert.equal(calls, 1);
  assert.equal(reads, 2);
  allowed = false;
  await assert.rejects(readProfiles(github, ['alice'], null, new Set(['alice'])), /Denied/);
  await assert.rejects(
    readProfiles(github, ['a/b'], null, new Set(['alice'])),
    (e) => e.status === 400
  );
});

test('different readers retain independent cached metadata within one TTL', async () => {
  const f = fixture();
  await readCommentLeaderboard(f.github, entries, null);
  f.token = 'second-reader';
  await readCommentLeaderboard(f.github, entries, {});
  const queries = f.queries;
  f.token = 'public';
  await readCommentLeaderboard(f.github, entries, null);
  assert.equal(f.queries, queries);
});
test('profile requests reject unrelated accounts and coalesce overlapping batches by account', async () => {
  const calls = [];
  const github = {
    readToken: async () => 'token',
    call: async (path) => {
      calls.push(path);
      return { login: path.split('/').pop() };
    }
  };
  const allowed = new Set(['alice', 'bob']);
  await assert.rejects(readProfiles(github, ['stranger'], null, allowed), (e) => e.status === 400);
  await Promise.all([
    readProfiles(github, ['ALICE', 'bob'], null, allowed),
    readProfiles(github, ['alice'], null, allowed)
  ]);
  assert.deepEqual(calls.sort(), ['/users/alice', '/users/bob']);
});
