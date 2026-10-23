import test from 'node:test';
import assert from 'node:assert/strict';
import { createPreview } from './discussion-preview.mjs';

test('browser fixture exercises current discussion, ranking, reply, permalink and post APIs', async (t) => {
  const service = await createPreview();
  await new Promise((resolve) => service.server.listen(0, '127.0.0.1', resolve));
  t.after(() => new Promise((resolve) => service.server.close(resolve)));
  const base = `http://127.0.0.1:${service.server.address().port}`;
  async function get(url) {
    const response = await fetch(base + url);
    assert.equal(response.status, 200, url);
    return response.json();
  }
  const counts = await get('/api/discussion-counts');
  assert.equal(counts.counts.holdout, 5);
  const discussion = await get('/api/discussions/holdout');
  assert.equal(discussion.totalCommentCount, 5);
  assert.equal(discussion.comments.pageInfo.hasNextPage, true);
  const parent = discussion.comments.nodes[0];
  assert.match(parent.url, /#discussioncomment-\d+$/);
  const replies = await get(`/api/discussions/holdout/replies?commentId=${parent.id}&after=next`);
  assert.equal(replies.nodes.length, 1);
  const ranking = await get('/api/comment-leaderboard');
  assert.equal(ranking.rows[0].score, 4);
  const contributor = await get('/api/comment-leaderboard/local-tester');
  assert.equal(contributor.comments.length, 4);
  assert.ok(contributor.comments.every((c) => c.body && /^\d+$/.test(c.number)));
  const cookie = service.signed.cookies[0].split(';')[0];
  const session = await service.auth.get(cookie);
  const posted = await fetch(base + '/api/discussions/holdout', {
    method: 'POST',
    headers: {
      cookie,
      origin: 'http://127.0.0.1:8773',
      'content-type': 'application/json',
      'x-csrf-token': session.csrf
    },
    body: JSON.stringify({ body: 'A synthetic new comment.' })
  });
  assert.equal(posted.status, 201);
  assert.match((await posted.json()).url, /#discussioncomment-\d+$/);
  assert.equal((await get('/api/discussion-counts')).counts.holdout, 6);
});
