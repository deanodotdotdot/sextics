import { RequestCache } from './cache.mjs';
import { ServiceError } from './github.mjs';

// Cache metadata and bounded previews in the running service, never in public files.
// Read authorization is checked before every cache lookup, including anonymous requests.
const caches = new WeakMap(),
  profileCaches = new WeakMap();
const metadata = `id url createdAt updatedAt isMinimized author { login avatarUrl(size:96) url ... on User { name } }`;
const pageInfo = 'pageInfo { hasNextPage endCursor }';
const replies = `${pageInfo} nodes { ${metadata} }`;
const parents = `${pageInfo} nodes { ${metadata} replies(first:20) { ${replies} } }`;
const unavailable = () =>
  new ServiceError(502, 'Comment counts are unavailable. Please try again.');
const loginPattern = /^[A-Za-z0-9][A-Za-z0-9-]{0,38}$/;
const profile = (author) => ({
  githubLogin: author.login,
  name: author.name || author.login,
  avatar: author.avatarUrl,
  profileUrl: author.url
});

async function nodes(github, ids, fields, token) {
  const result = [];
  for (let offset = 0; offset < ids.length; offset += 100) {
    const data = await github.graphql(
      `query($ids:[ID!]!) { nodes(ids:$ids) { ${fields} } }`,
      { ids: ids.slice(offset, offset + 100) },
      token
    );
    if (!Array.isArray(data.nodes)) throw unavailable();
    result.push(...data.nodes.filter(Boolean));
  }
  return result;
}

async function pages(first, next, visit) {
  let page = first;
  const cursors = new Set();
  for (;;) {
    if (!Array.isArray(page?.nodes) || !page.pageInfo) throw unavailable();
    for (const item of page.nodes) if (item) await visit(item);
    if (!page.pageInfo.hasNextPage) return;
    const cursor = page.pageInfo.endCursor;
    if (!cursor || cursors.has(cursor)) throw unavailable();
    cursors.add(cursor);
    page = await next(cursor);
  }
}

async function collect(github, entries, token) {
  const byDiscussion = new Map(Object.entries(entries).map(([id, entry]) => [entry.nodeId, id]));
  const comments = new Map();
  function add(comment, instanceId, isReply) {
    if (!comment.id || !comment.createdAt || !Number.isFinite(Date.parse(comment.createdAt)))
      throw unavailable();
    // Deleted accounts have no attributable identity. Hidden posts are not promoted.
    if (!comment.author || comment.isMinimized) return;
    const number = /#discussioncomment-(\d+)$/.exec(comment.url || '')?.[1];
    if (!number) throw unavailable();
    comments.set(comment.id, {
      id: comment.id,
      number,
      instanceId,
      isReply,
      createdAt: comment.createdAt,
      updatedAt: comment.updatedAt,
      author: profile(comment.author)
    });
  }
  const discussions = await nodes(
    github,
    [...byDiscussion.keys()],
    `... on Discussion { id comments(first:100) { ${parents} } }`,
    token
  );
  for (const discussion of discussions) {
    const instanceId = byDiscussion.get(discussion.id);
    if (!instanceId) continue;
    await pages(
      discussion.comments,
      async (after) => {
        const data = await github.graphql(
          `query($id:ID!,$after:String!) { node(id:$id) { ... on Discussion { id comments(first:100,after:$after) { ${parents} } } } }`,
          { id: discussion.id, after },
          token
        );
        if (data.node?.id !== discussion.id) throw unavailable();
        return data.node.comments;
      },
      async (comment) => {
        add(comment, instanceId, false);
        await pages(
          comment.replies,
          async (after) => {
            const data = await github.graphql(
              `query($id:ID!,$after:String!) { node(id:$id) { ... on DiscussionComment { id replies(first:100,after:$after) { ${replies} } } } }`,
              { id: comment.id, after },
              token
            );
            if (data.node?.id !== comment.id) throw unavailable();
            return data.node.replies;
          },
          (reply) => add(reply, instanceId, true)
        );
      }
    );
  }
  return [...comments.values()];
}

async function index(github, entries, session) {
  const token = await github.readToken(session);
  let cache = caches.get(github);
  if (!cache) caches.set(github, (cache = new RequestCache(120000)));
  const comments = await cache.get(JSON.stringify([token, entries]), () =>
    collect(github, entries, token)
  );
  return { token, comments, cache };
}

export function invalidateCommentLeaderboard(github) {
  caches.delete(github);
}

export async function readCommentLeaderboard(github, entries, session) {
  const { comments } = await index(github, entries, session),
    accounts = new Map();
  for (const comment of comments) {
    const key = comment.author.githubLogin.toLowerCase();
    const row = accounts.get(key) || {
      ...comment.author,
      score: 0,
      reachedCountAt: comment.createdAt
    };
    row.score++;
    if (comment.createdAt > row.reachedCountAt) row.reachedCountAt = comment.createdAt;
    accounts.set(key, row);
  }
  const rows = [...accounts.values()].sort(
    (a, b) =>
      b.score - a.score ||
      Date.parse(a.reachedCountAt) - Date.parse(b.reachedCountAt) ||
      a.githubLogin.toLowerCase().localeCompare(b.githubLogin.toLowerCase())
  );
  return { rows: rows.map((row, i) => ({ ...row, rank: i + 1 })) };
}

export async function readContributorComments(github, entries, login, session) {
  if (!loginPattern.test(login)) throw new ServiceError(400, 'Invalid GitHub username.');
  const { token, comments, cache } = await index(github, entries, session);
  return cache.get(JSON.stringify([token, entries, login.toLowerCase()]), async () => {
    const selected = comments.filter(
      (c) => c.author.githubLogin.toLowerCase() === login.toLowerCase()
    );
    const byId = new Map(selected.map((c) => [c.id, c]));
    const fresh = await nodes(
      github,
      selected.map((c) => c.id),
      `... on DiscussionComment { id url createdAt updatedAt isMinimized author { login } body discussion { id } }`,
      token
    );
    const result = [];
    for (const comment of fresh) {
      const saved = byId.get(comment.id);
      if (
        !saved ||
        comment.isMinimized ||
        comment.author?.login.toLowerCase() !== login.toLowerCase() ||
        comment.discussion?.id !== entries[saved.instanceId]?.nodeId
      )
        continue;
      result.push({
        instanceId: saved.instanceId,
        number: saved.number,
        isReply: saved.isReply,
        createdAt: comment.createdAt,
        updatedAt: comment.updatedAt,
        body: comment.body.length > 1024 ? comment.body.slice(0, 1024) + '…' : comment.body,
        url: comment.url
      });
    }
    if (result.length !== selected.length) invalidateCommentLeaderboard(github);
    result.sort(
      (a, b) => Date.parse(b.createdAt) - Date.parse(a.createdAt) || b.number.localeCompare(a.number)
    );
    return { comments: result };
  });
}

export async function readProfiles(github, logins, session, contributors) {
  if (!logins.length || logins.length > 50 || logins.some((login) => !loginPattern.test(login)))
    throw new ServiceError(400, 'Invalid GitHub usernames.');
  const selected = [...new Set(logins.map((login) => login.toLowerCase()))];
  if (selected.some((login) => !contributors.has(login)))
    throw new ServiceError(400, 'Choose an atlas contributor.');
  const token = await github.readToken(session);
  let cache = profileCaches.get(github);
  if (!cache) profileCaches.set(github, (cache = new RequestCache(300000, 512)));
  const accounts = await Promise.all(
    selected.map((login) =>
      cache.get(JSON.stringify([token, login]), async () => {
        const user = await github.call(`/users/${encodeURIComponent(login)}`, { token });
        return {
          githubLogin: user.login,
          name: user.name || user.login,
          avatar: user.avatar_url,
          profileUrl: user.html_url
        };
      })
    )
  );
  return { accounts };
}
