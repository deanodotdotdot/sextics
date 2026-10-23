import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, mkdir, writeFile, rm, symlink } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
import {
  GitHub,
  readDiscussion,
  readDiscussionCounts,
  readReplies,
  postComment
} from './github.mjs';
import { createService } from './server.mjs';
const entry = { number: 7, nodeId: 'D_target' },
  session = { token: 'user-token' },
  repository = 'hodge-computer/sextics';
const leaf = {
  id: 'C_one',
  body: '$x^2$',
  url: 'https://github.com/hodge-computer/sextics/discussions/7#discussioncomment-1',
  isMinimized: false
};
const page = (nodes) => ({
  totalCount: nodes.length,
  nodes,
  pageInfo: { hasNextPage: false, endCursor: null }
});
const totals = (counts) =>
  page(counts.map((count, i) => ({ id: 'C' + i, replies: { totalCount: count } })));
test('anonymous reads never expose a private repository; authenticated reads use the user token', async () => {
  const github = new GitHub({ repository });
  github.installationToken = async () => 'read-only-app';
  let privateRepo = true;
  github.call = async (p, { token }) => {
    assert.equal(p, '/repos/' + repository);
    assert.equal(token, 'read-only-app');
    return { private: privateRepo };
  };
  await assert.rejects(github.readToken(null), (e) => e.status === 401);
  assert.equal(await github.readToken(session), 'user-token');
  privateRepo = false;
  assert.equal(await github.readToken(null), 'read-only-app');
});
test('reads bind the discussion ID, paginate and suppress minimized content at both levels', async () => {
  const github = {
    config: { repository },
    readToken: async () => session.token,
    graphql: async (query, variables, token) => {
      assert(!query.includes('viewerCanComment'));
      assert(query.includes('replies(first:20)'));
      assert.equal(variables.after, 'cursor');
      assert.equal(token, session.token);
      return {
        repository: {
          discussion: {
            id: entry.nodeId,
            locked: false,
            commentTotals: totals([35]),
            comments: {
              ...page([
                {
                  ...leaf,
                  isMinimized: true,
                  replies: page([{ ...leaf, id: 'R', isMinimized: true }])
                }
              ]),
              pageInfo: { hasNextPage: true, endCursor: 'next' }
            }
          }
        }
      };
    }
  };
  const d = await readDiscussion(github, entry, 'cursor', session);
  assert.equal(d.viewerCanComment, true);
  assert.equal(d.totalCommentCount, 36);
  assert.equal(d.commentTotals, undefined);
  assert.equal(d.comments.pageInfo.endCursor, 'next');
  assert.equal(d.comments.nodes[0].body, '');
  assert.equal(d.comments.nodes[0].replies.nodes[0].body, '');
  assert.equal((await readDiscussion(github, entry, 'cursor', null)).viewerCanComment, false);
  await assert.rejects(
    readDiscussion(github, { ...entry, nodeId: 'wrong' }, 'cursor', session),
    (e) => e.status === 404
  );
});
test('atlas counts use mapped discussions, omit unavailable threads and recheck access before cached reads', async () => {
  let calls = 0,
    reads = 0,
    token = 'reader-one',
    allowed = true;
  const github = {
    readToken: async () => {
      reads++;
      if (!allowed) throw new Error('Access denied');
      return token;
    },
    graphql: async (query, variables, usedToken) => {
      calls++;
      assert.equal(usedToken, token);
      assert(!query.includes('body'));
      assert.deepEqual(variables.ids, ['D_target', 'D_missing']);
      return {
        nodes: [
          { id: 'D_target', comments: totals([2, 3]) },
          null,
          { id: 'D_unmapped', comments: { totalCount: 999 } }
        ]
      };
    }
  };
  const entries = { holdout: entry, missing: { number: 8, nodeId: 'D_missing' } };
  assert.deepEqual(await readDiscussionCounts(github, entries, null), { counts: { holdout: 7 } });
  assert.deepEqual(await readDiscussionCounts(github, entries, null), { counts: { holdout: 7 } });
  assert.equal(calls, 1);
  assert.equal(reads, 2);
  token = 'reader-two';
  await readDiscussionCounts(github, entries, session);
  assert.equal(calls, 2);
  allowed = false;
  await assert.rejects(readDiscussionCounts(github, entries, session), /Access denied/);
});
test('reply pagination is restricted to a top-level comment of this instance', async () => {
  let discussionId = entry.nodeId,
    replyTo = null;
  const github = {
    readToken: async () => session.token,
    graphql: async (query, vars, token) => {
      assert.equal(vars.id, 'C_one');
      assert.equal(vars.after, 'next');
      assert.equal(token, session.token);
      return {
        node: {
          discussion: { id: discussionId },
          replyTo,
          replies: page([{ ...leaf, isMinimized: true }])
        }
      };
    }
  };
  assert.equal((await readReplies(github, entry, 'C_one', 'next', session)).nodes[0].body, '');
  discussionId = 'D_other';
  await assert.rejects(
    readReplies(github, entry, 'C_one', 'next', session),
    (e) => e.status === 404
  );
  discussionId = entry.nodeId;
  replyTo = { id: 'C_parent' };
  await assert.rejects(
    readReplies(github, entry, 'C_one', 'next', session),
    (e) => e.status === 404
  );
});
test('totals include replies to parents beyond the first hundred, even when bodies are not loaded', async () => {
  const entries = { holdout: entry },
    first = totals(Array(100).fill(2));
  first.totalCount = 101;
  first.pageInfo = { hasNextPage: true, endCursor: 'next' };
  let calls = 0;
  const github = {
    readToken: async () => session.token,
    graphql: async (query, vars, token) => {
      calls++;
      assert.equal(token, session.token);
      assert(!query.includes('body'));
      assert(query.includes('replies { totalCount }'));
      if (vars.ids) return { nodes: [{ id: entry.nodeId, comments: first }] };
      assert.equal(vars.id, entry.nodeId);
      assert.equal(vars.after, 'next');
      return {
        node: { id: entry.nodeId, comments: page([{ id: 'C100', replies: { totalCount: 7 } }]) }
      };
    }
  };
  assert.deepEqual(await readDiscussionCounts(github, entries, session), {
    counts: { holdout: 308 }
  });
  assert.equal(calls, 2);
});
test('incomplete totals fail rather than silently showing a partial count', async () => {
  for (const malformed of [null, { totalCount: 1 }, totals([-1])]) {
    const github = {
      readToken: async () => session.token,
      graphql: async () => ({ nodes: [{ id: entry.nodeId, comments: malformed }] })
    };
    await assert.rejects(
      readDiscussionCounts(github, { holdout: entry }, session),
      (e) => e.status === 502
    );
  }
});
test('posting a reply invalidates cached inclusive totals', async () => {
  let replies = 1,
    queries = 0;
  const github = {
    readToken: async () => session.token,
    graphql: async (query, vars) => {
      if (vars.ids) {
        queries++;
        return { nodes: [{ id: entry.nodeId, comments: totals([replies]) }] };
      }
      if (query.startsWith('mutation')) {
        replies++;
        return { addDiscussionComment: { comment: leaf } };
      }
      return { node: { discussion: { id: entry.nodeId }, replyTo: null } };
    }
  };
  assert.deepEqual(await readDiscussionCounts(github, { holdout: entry }, session), {
    counts: { holdout: 2 }
  });
  await postComment(github, entry, 'A reply', 'C_one', session);
  assert.deepEqual(await readDiscussionCounts(github, { holdout: entry }, session), {
    counts: { holdout: 3 }
  });
  assert.equal(queries, 2);
});
test('posts use the authenticated user and reject cross-instance or nested reply targets', async () => {
  let discussionId = entry.nodeId,
    replyTo = null;
  const mutations = [];
  const github = {
    graphql: async (query, vars, token) => {
      assert.equal(token, session.token);
      if (query.startsWith('mutation')) {
        mutations.push(vars);
        return { addDiscussionComment: { comment: leaf } };
      }
      return { node: { discussion: { id: discussionId }, replyTo } };
    }
  };
  await assert.rejects(postComment(github, entry, 'body', null, null), (e) => e.status === 401);
  await postComment(github, entry, 'body', undefined, session);
  assert.deepEqual(mutations[0], { input: { discussionId: entry.nodeId, body: 'body' } });
  await postComment(github, entry, 'reply', 'C_one', session);
  assert.equal(mutations[1].input.replyToId, 'C_one');
  discussionId = 'D_other';
  await assert.rejects(
    postComment(github, entry, 'reply', 'C_one', session),
    (e) => e.status === 400
  );
  discussionId = entry.nodeId;
  replyTo = { id: 'parent' };
  await assert.rejects(
    postComment(github, entry, 'reply', 'C_one', session),
    (e) => e.status === 400
  );
  assert.equal(mutations.length, 2);
});
test('HTTP boundary enforces target mapping, CSRF, body schema, pagination and rate limits', async () => {
  const root = await mkdtemp(path.join(tmpdir(), 'hodge-discussion-test-')),
    origin = 'https://test.example';
  let writes = 0;
  await mkdir(path.join(root, 'data'));
  await mkdir(path.join(root, 'discussions'));
  await writeFile(
    path.join(root, 'data/catalogue.json'),
    JSON.stringify({ instanceIds: ['holdout', 'unmapped'] })
  );
  await writeFile(
    path.join(root, 'discussions/index.json'),
    JSON.stringify({ repository, instances: { holdout: entry } })
  );
  const github = {
    config: { repository },
    readToken: async (s) => s?.token || 'public-token',
    graphql: async (query, vars, token) => {
      if (vars.ids) {
        assert.deepEqual(vars.ids, [entry.nodeId]);
        return { nodes: [{ id: entry.nodeId, comments: totals([1, 2, 0]) }] };
      }
      if (query.startsWith('mutation')) {
        writes++;
        assert.equal(token, 'user-token');
        return { addDiscussionComment: { comment: leaf } };
      }
      if (vars.id)
        return { node: { discussion: { id: entry.nodeId }, replyTo: null, replies: page([leaf]) } };
      return {
        repository: {
          discussion: {
            id: entry.nodeId,
            url: 'https://github.com/' + repository + '/discussions/7',
            locked: false,
            commentTotals: totals([1, 2, 0]),
            comments: page([leaf])
          }
        }
      };
    }
  };
  const service = await createService({ root, origin, github });
  await new Promise((r) => service.server.listen(0, '127.0.0.1', r));
  const base = 'http://127.0.0.1:' + service.server.address().port;
  const created = await service.auth.create({ access_token: 'user-token' }, { login: 'tester' }),
    cookie = created.cookies[0].split(';')[0],
    signed = await service.auth.get(cookie);
  const headers = {
    cookie,
    origin,
    'Content-Type': 'application/json',
    'X-CSRF-Token': signed.csrf
  };
  const post = (body, h = headers) =>
    fetch(base + '/api/discussions/holdout', {
      method: 'POST',
      headers: h,
      body: JSON.stringify(body)
    });
  try {
    await mkdir(path.join(root, 'server'));
    await writeFile(path.join(root, 'server/private.json'), 'private');
    await symlink(path.join(root, 'server/private.json'), path.join(root, 'data/leak.json'));
    assert.equal((await fetch(base + '/data/leak.json')).status, 404);
    assert.equal((await fetch(base + '/server/private.json')).status, 404);
    assert.equal((await fetch(base + '/data/catalogue.json')).status, 200);
    const counts = await fetch(base + '/api/discussion-counts');
    assert.equal(counts.headers.get('cache-control'), 'no-store');
    assert.deepEqual(await counts.json(), { counts: { holdout: 6 } });
    assert.equal((await fetch(base + '/api/discussions/missing')).status, 404);
    assert.equal((await fetch(base + '/api/discussions/unmapped')).status, 503);
    assert.equal((await post({ body: 'hello' }, {})).status, 401);
    assert.equal(
      (await post({ body: 'hello' }, { ...headers, origin: 'https://evil.test' })).status,
      403
    );
    for (const body of [
      { body: '' },
      { body: 'a'.repeat(30001) },
      { body: 'hello', author: 'someone-else' },
      { body: 'hello', replyToId: 5 }
    ])
      assert.equal((await post(body)).status, 400);
    const read = await fetch(base + '/api/discussions/holdout');
    assert.equal(read.headers.get('cache-control'), 'no-store');
    assert.equal((await read.json()).viewerCanComment, false);
    assert.equal(
      (await fetch(base + '/api/discussions/holdout/replies?commentId=C_one')).status,
      200
    );
    assert.equal((await fetch(base + '/api/discussions/holdout/replies')).status, 400);
    assert.equal((await post({ body: 'hello' })).status, 201);
    assert.equal((await post({ body: 'again' })).status, 429);
    assert.equal(writes, 1);
  } finally {
    await new Promise((r) => service.server.close(r));
    await rm(root, { recursive: true, force: true });
  }
});
