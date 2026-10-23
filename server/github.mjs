import { RequestCache } from './cache.mjs';
import { createSign } from 'node:crypto';

export class ServiceError extends Error {
  constructor(status, message) {
    super(message);
    this.status = status;
  }
}

export class GitHub {
  constructor(config) {
    this.config = config;
    this.activeRequests = 0;
    this.waiters = [];
  }

  async call(path, { token, method = 'GET', body } = {}) {
    if (this.activeRequests >= 4) {
      if (this.waiters.length >= 64)
        throw new ServiceError(429, 'GitHub is busy. Please try again shortly.');
      await new Promise((resolve) => this.waiters.push(resolve));
    } else this.activeRequests++;
    try {
      const response = await fetch(`https://api.github.com${path}`, {
        method,
        redirect: 'error',
        signal: AbortSignal.timeout(20000),
        headers: {
          Accept: 'application/vnd.github+json',
          'X-GitHub-Api-Version': '2026-03-10',
          'User-Agent': 'hodge-computer-discussions',
          Authorization: `Bearer ${token}`,
          ...(body ? { 'Content-Type': 'application/json' } : {})
        },
        ...(body ? { body: JSON.stringify(body) } : {})
      });
      if (!response.ok) {
        const status = response.status;
        throw new ServiceError(
          status === 401 ? 401 : status === 403 || status === 404 ? 403 : 502,
          status === 401
            ? 'Please sign in again.'
            : status === 403 || status === 404
              ? 'Your GitHub account cannot access this discussion.'
              : 'GitHub is unavailable. Please try again.'
        );
      }
      return response.status === 204 ? null : await response.json();
    } finally {
      const next = this.waiters.shift();
      if (next) next();
      else this.activeRequests--;
    }
  }

  async graphql(query, variables, token) {
    const value = await this.call('/graphql', {
      token,
      method: 'POST',
      body: { query, variables }
    });
    if (value.errors?.length)
      throw new ServiceError(
        403,
        'GitHub could not complete this request. Check your access and try again.'
      );
    return value.data;
  }

  async exchange(code, verifier, redirectUri) {
    const response = await fetch('https://github.com/login/oauth/access_token', {
      method: 'POST',
      redirect: 'error',
      signal: AbortSignal.timeout(20000),
      headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
      body: JSON.stringify({
        client_id: this.config.client_id,
        client_secret: this.config.client_secret,
        code,
        code_verifier: verifier,
        redirect_uri: redirectUri
      })
    });
    if (!response.ok)
      throw new ServiceError(502, 'GitHub sign-in is unavailable. Please try again.');
    const result = await response.json();
    if (result.error || !result.access_token)
      throw new ServiceError(401, 'Sign-in expired. Please try again.');
    return result;
  }

  async installationToken() {
    if (this.cachedToken?.expires > Date.now() + 60000) return this.cachedToken.token;
    if (!this.config.id || !this.config.pem)
      throw new ServiceError(503, 'GitHub Discussions has not been connected yet.');
    const now = Math.floor(Date.now() / 1000);
    const encode = (value) => Buffer.from(JSON.stringify(value)).toString('base64url');
    const unsigned = `${encode({ alg: 'RS256', typ: 'JWT' })}.${encode({ iat: now - 60, exp: now + 300, iss: this.config.id })}`;
    const jwt = `${unsigned}.${createSign('RSA-SHA256').update(unsigned).sign(this.config.pem, 'base64url')}`;
    const installation = await this.call(`/repos/${this.config.repository}/installation`, {
      token: jwt
    });
    const result = await this.call(`/app/installations/${installation.id}/access_tokens`, {
      token: jwt,
      method: 'POST',
      body: {
        repositories: [this.config.repository.split('/')[1]],
        permissions: { discussions: 'read', metadata: 'read' }
      }
    });
    this.cachedToken = { token: result.token, expires: Date.parse(result.expires_at) };
    return result.token;
  }

  async viewer(token) {
    const user = await this.call('/user', { token });
    return {
      login: user.login,
      name: user.name || user.login,
      avatar: user.avatar_url,
      url: user.html_url
    };
  }

  async readToken(session) {
    if (session) return session.token;
    const token = await this.installationToken();
    // Always check visibility before using app credentials for an anonymous reader.
    const repository = await this.call(`/repos/${this.config.repository}`, { token });
    if (repository.private)
      throw new ServiceError(401, 'Sign in with GitHub to read this discussion.');
    return token;
  }
}

export const commentFields = `id body url createdAt updatedAt isMinimized
  author { login avatarUrl url }`;
const pageFields = 'totalCount pageInfo { hasNextPage endCursor }';
const countFields = `${pageFields} nodes { id replies { totalCount } }`;
const withReplies = `${commentFields} replies(first:20) { ${pageFields} nodes { ${commentFields} } }`;
const clean = (comment) => ({
  ...comment,
  body: comment.isMinimized ? '' : comment.body,
  ...(comment.replies
    ? { replies: { ...comment.replies, nodes: comment.replies.nodes.filter(Boolean).map(clean) } }
    : {})
});

export async function readDiscussion(github, entry, cursor, session) {
  const token = await github.readToken(session);
  const [owner, name] = github.config.repository.split('/');
  const data = await github.graphql(
    `query($owner:String!,$name:String!,$number:Int!,$after:String) {
    repository(owner:$owner,name:$name) { discussion(number:$number) {
      id number title body url locked
      comments(first:30,after:$after) { ${pageFields} nodes { ${withReplies} } }
      commentTotals: comments(first:100) { ${countFields} }
    } }
  }`,
    { owner, name, number: entry.number, after: cursor || null },
    token
  );
  const discussion = data.repository?.discussion;
  if (!discussion || discussion.id !== entry.nodeId)
    throw new ServiceError(404, 'This discussion is unavailable.');
  const { commentTotals, ...thread } = discussion;
  return {
    ...thread,
    totalCommentCount: await countCommentsAndReplies(github, entry.nodeId, commentTotals, token),
    viewerCanComment: !!session && !discussion.locked,
    comments: {
      ...discussion.comments,
      nodes: discussion.comments.nodes.filter(Boolean).map(clean)
    }
  };
}

// GitHub's connection total counts top-level comments only. Sum reply totals
// across every parent page without downloading comment or reply bodies.
async function countCommentsAndReplies(github, id, firstPage, token) {
  const topLevel = firstPage?.totalCount,
    replies = new Map(),
    cursors = new Set();
  if (!Number.isSafeInteger(topLevel) || topLevel < 0)
    throw new ServiceError(502, 'Discussion counts are unavailable. Please try again.');
  let page = firstPage;
  for (;;) {
    if (!Array.isArray(page?.nodes) || !page.pageInfo)
      throw new ServiceError(502, 'Discussion counts are unavailable. Please try again.');
    for (const comment of page.nodes) {
      if (!comment) continue;
      const count = comment.replies?.totalCount;
      if (!comment.id || !Number.isSafeInteger(count) || count < 0)
        throw new ServiceError(502, 'Discussion counts are unavailable. Please try again.');
      replies.set(comment.id, count);
    }
    if (!page.pageInfo.hasNextPage) break;
    const after = page.pageInfo.endCursor;
    if (!after || cursors.has(after))
      throw new ServiceError(502, 'Discussion counts are unavailable. Please try again.');
    cursors.add(after);
    const next = await github.graphql(
      `query($id:ID!,$after:String!) {
      node(id:$id) { ... on Discussion { id comments(first:100,after:$after) { ${countFields} } } }
    }`,
      { id, after },
      token
    );
    if (next.node?.id !== id) throw new ServiceError(404, 'This discussion is unavailable.');
    page = next.node.comments;
  }
  return topLevel + [...replies.values()].reduce((sum, count) => sum + count, 0);
}

// Fetch only counts for the atlas, not the contents of every conversation.
const countCaches = new WeakMap();
export async function readDiscussionCounts(github, entries, session) {
  const token = await github.readToken(session);
  const ids = Object.values(entries).map((entry) => entry.nodeId),
    key = JSON.stringify(Object.entries(entries));
  let cache = countCaches.get(github);
  if (!cache) countCaches.set(github, (cache = new RequestCache(120000)));
  return cache.get(JSON.stringify([token, key]), async () => {
    const byNode = new Map();
    for (let offset = 0; offset < ids.length; offset += 100) {
      const data = await github.graphql(
        `query($ids:[ID!]!) {
      nodes(ids:$ids) { ... on Discussion { id comments(first:100) { ${countFields} } } }
    }`,
        { ids: ids.slice(offset, offset + 100) },
        token
      );
      if (!Array.isArray(data.nodes))
        throw new ServiceError(502, 'GitHub returned an invalid discussion list.');
      for (const node of data.nodes) {
        if (node && ids.includes(node.id))
          byNode.set(node.id, await countCommentsAndReplies(github, node.id, node.comments, token));
      }
    }
    const value = {
      counts: Object.fromEntries(
        Object.entries(entries)
          .filter(([, entry]) => byNode.has(entry.nodeId))
          .map(([id, entry]) => [id, byNode.get(entry.nodeId)])
      )
    };
    return value;
  });
}

export async function readReplies(github, entry, commentId, cursor, session) {
  const token = await github.readToken(session);
  const data = await github.graphql(
    `query($id:ID!,$after:String) {
    node(id:$id) { ... on DiscussionComment {
      discussion { id } replyTo { id }
      replies(first:30,after:$after) { ${pageFields} nodes { ${commentFields} } }
    } }
  }`,
    { id: commentId, after: cursor || null },
    token
  );
  if (data.node?.discussion?.id !== entry.nodeId || data.node.replyTo)
    throw new ServiceError(404, 'This comment is unavailable.');
  return { ...data.node.replies, nodes: data.node.replies.nodes.filter(Boolean).map(clean) };
}

export async function postComment(github, entry, body, replyToId, session) {
  if (!session) throw new ServiceError(401, 'Sign in with GitHub to post.');
  if (replyToId) {
    const data = await github.graphql(
      `query($id:ID!){node(id:$id){... on DiscussionComment { discussion { id } replyTo { id } }}}`,
      { id: replyToId },
      session.token
    );
    if (data.node?.discussion?.id !== entry.nodeId || data.node.replyTo)
      throw new ServiceError(400, 'Choose a top-level comment in this discussion to reply to.');
  }
  const data = await github.graphql(
    `mutation($input:AddDiscussionCommentInput!) {
    addDiscussionComment(input:$input) { comment { ${commentFields} } }
  }`,
    { input: { discussionId: entry.nodeId, body, ...(replyToId ? { replyToId } : {}) } },
    session.token
  );
  countCaches.delete(github);
  return clean(data.addDiscussionComment.comment);
}
