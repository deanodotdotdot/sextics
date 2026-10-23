import { readFile } from 'node:fs/promises';
import path from 'node:path';
import {
  readCommentLeaderboard,
  readContributorComments,
  readProfiles,
  invalidateCommentLeaderboard
} from './comment-leaderboard.mjs';
import {
  GitHub,
  ServiceError,
  readDiscussion,
  readDiscussionCounts,
  readReplies,
  postComment
} from './github.mjs';

const noStore = {
  'Cache-Control': 'no-store',
  'X-Content-Type-Options': 'nosniff',
  'Referrer-Policy': 'no-referrer',
  'X-Frame-Options': 'DENY'
};
function send(res, status, body, headers = {}) {
  res.writeHead(status, {
    ...noStore,
    'Content-Type': 'application/json; charset=utf-8',
    ...headers
  });
  res.end(typeof body === 'string' || Buffer.isBuffer(body) ? body : JSON.stringify(body));
}
function redirect(res, location, cookies) {
  send(res, 303, '', { Location: location, ...(cookies ? { 'Set-Cookie': cookies } : {}) });
}
async function jsonBody(req) {
  const chunks = [];
  let size = 0;
  for await (const chunk of req) {
    size += chunk.length;
    if (size > 131072) throw new ServiceError(413, 'The comment is too long.');
    chunks.push(chunk);
  }
  try {
    return JSON.parse(Buffer.concat(chunks).toString('utf8'));
  } catch {
    throw new ServiceError(400, 'Invalid request.');
  }
}
export async function createHandler({ root, origin, auth, appConfig }) {
  const base = new URL(origin);
  if (base.origin !== origin || base.protocol !== 'https:')
    throw new Error('Use a fixed HTTPS origin.');
  const config = { repository: 'hodge-computer/sextics', ...appConfig };
  if (config.repository !== 'hodge-computer/sextics')
    throw new Error('Unexpected discussion repository.');
  const github = new GitHub(config);
  const catalogue = JSON.parse(await readFile(path.join(root, 'data/catalogue.json'), 'utf8'));
  const records = catalogue.instanceIds;
  if (!Array.isArray(records)) throw new Error('Invalid instance catalogue.');
  const instanceIds = new Set(records);
  async function contributors() {
    const response = await fetch(`${origin}/assets/atlas/index.json`, {
      cache: 'no-cache',
      redirect: 'error',
      signal: AbortSignal.timeout(5000)
    });
    if (!response.ok) throw new ServiceError(503, 'The published contributor list is unavailable.');
    const atlas = await response.json();
    return new Set(
      atlas.records
        .filter((record) => record.formalStatus === 'proved')
        .map((record) => record.credit.githubLogin.toLowerCase())
    );
  }
  async function mappings() {
    let index;
    try {
      index = JSON.parse(await readFile(path.join(root, 'discussions/index.json'), 'utf8'));
    } catch (error) {
      if (error.code === 'ENOENT')
        throw new ServiceError(503, 'The discussion has not been connected yet.');
      throw error;
    }
    if (index.repository !== config.repository) throw new Error('Invalid discussion repository.');
    if (
      !Object.entries(index.instances).every(
        ([id, entry]) =>
          instanceIds.has(id) &&
          entry &&
          Number.isSafeInteger(entry.number) &&
          entry.number > 0 &&
          typeof entry.nodeId === 'string'
      )
    )
      throw new Error('Invalid discussion mapping.');
    return index.instances;
  }
  async function mapping(id) {
    if (!instanceIds.has(id)) throw new ServiceError(404, 'Unknown instance.');
    const entry = (await mappings())[id];
    if (!entry) throw new ServiceError(503, 'The discussion has not been connected yet.');
    return entry;
  }
  async function handler(req, res) {
    try {
      const url = new URL(req.url, origin),
        session = await auth.get(req.headers.cookie);
      if (url.pathname === '/api/session' && req.method === 'GET')
        return send(res, 200, {
          connected: !!config.client_id,
          user: session?.user || null,
          csrf: session?.csrf || null
        });
      if (url.pathname === '/auth/github' && req.method === 'GET') {
        if (!config.client_id)
          throw new ServiceError(503, 'GitHub sign-in has not been connected yet.');
        const flow = await auth.start(url.searchParams.get('returnTo'));
        const target = new URL('https://github.com/login/oauth/authorize');
        target.search = new URLSearchParams({
          client_id: config.client_id,
          redirect_uri: `${origin}/auth/github/callback`,
          state: flow.state,
          code_challenge: flow.challenge,
          code_challenge_method: 'S256'
        });
        return redirect(res, target.href, flow.cookie);
      }
      if (url.pathname === '/auth/github/callback' && req.method === 'GET') {
        const flow = await auth.finish(url.searchParams.get('state'), req.headers.cookie);
        if (url.searchParams.has('error'))
          return redirect(res, flow.returnTo, auth.cookie(auth.flowName, '', 0));
        const code = url.searchParams.get('code');
        if (!code || code.length > 512) throw new ServiceError(400, 'Sign-in code is missing.');
        const tokens = await github.exchange(code, flow.verifier, `${origin}/auth/github/callback`);
        const user = await github.viewer(tokens.access_token);
        await auth.remove(req.headers.cookie);
        const created = await auth.create(tokens, user);
        return redirect(res, flow.returnTo, created.cookies);
      }
      if (url.pathname === '/api/sign-out' && req.method === 'POST') {
        auth.requireWrite(req, session);
        return send(
          res,
          200,
          { ok: true },
          { 'Set-Cookie': await auth.remove(req.headers.cookie) }
        );
      }
      if (url.pathname === '/api/discussion-counts' && req.method === 'GET')
        return send(res, 200, await readDiscussionCounts(github, await mappings(), session));
      if (url.pathname === '/api/comment-leaderboard' && req.method === 'GET')
        return send(res, 200, await readCommentLeaderboard(github, await mappings(), session));
      const contributor = /^\/api\/comment-leaderboard\/([^/]+)$/.exec(url.pathname);
      if (contributor && req.method === 'GET')
        return send(
          res,
          200,
          await readContributorComments(github, await mappings(), contributor[1], session)
        );
      if (url.pathname === '/api/profiles' && req.method === 'GET')
        return send(
          res,
          200,
          await readProfiles(
            github,
            (url.searchParams.get('logins') || '').split(',').filter(Boolean),
            session,
            await contributors()
          )
        );
      const match = /^\/api\/discussions\/([A-Za-z0-9-]+)(\/replies)?$/.exec(url.pathname);
      if (match) {
        const entry = await mapping(match[1]);
        if (req.method === 'GET') {
          const cursor = url.searchParams.get('after');
          if (cursor?.length > 512) throw new ServiceError(400, 'Invalid page.');
          if (match[2]) {
            const commentId = url.searchParams.get('commentId');
            if (!commentId || commentId.length > 200)
              throw new ServiceError(400, 'Invalid comment.');
            return send(res, 200, await readReplies(github, entry, commentId, cursor, session));
          }
          return send(res, 200, await readDiscussion(github, entry, cursor, session));
        }
        if (req.method === 'POST' && !match[2]) {
          auth.requireWrite(req, session);
          const input = await jsonBody(req);
          if (
            !input ||
            typeof input.body !== 'string' ||
            !input.body.trim() ||
            input.body.length > 30000 ||
            Object.keys(input).some((k) => !['body', 'replyToId'].includes(k))
          )
            throw new ServiceError(400, 'Write a comment of at most 30,000 characters.');
          if (
            input.replyToId !== undefined &&
            (typeof input.replyToId !== 'string' || input.replyToId.length > 200)
          )
            throw new ServiceError(400, 'Invalid reply.');
          await auth.claimPost(session);
          const comment = await postComment(github, entry, input.body, input.replyToId, session);
          invalidateCommentLeaderboard(github);
          return send(res, 201, comment);
        }
        throw new ServiceError(405, 'Method not allowed.');
      }
      throw new ServiceError(404, 'Not found.');
    } catch (error) {
      const status = error instanceof ServiceError ? error.status : 500;
      const message =
        status === 500 ? 'The request could not be completed. Please try again.' : error.message;
      // Do not log request URLs, tokens, OAuth codes, cookies, or upstream responses.
      send(res, status, { error: message });
    }
  }
  return handler;
}
