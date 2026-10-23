import http from 'node:http';
import { readFile, writeFile, realpath, stat, mkdir } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { readCommentLeaderboard, readContributorComments, readProfiles, invalidateCommentLeaderboard } from './comment-leaderboard.mjs';
import { Auth, equal } from './auth.mjs';
import { GitHub, ServiceError, readDiscussion, readDiscussionCounts, readReplies, postComment } from './github.mjs';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const escape = value => String(value).replace(/[&<>"']/g, char => ({ '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;' }[char]));
const mime = { '.html':'text/html; charset=utf-8', '.js':'text/javascript; charset=utf-8', '.css':'text/css; charset=utf-8', '.json':'application/json', '.md':'text/plain; charset=utf-8', '.rec':'text/plain; charset=utf-8', '.lean':'text/plain; charset=utf-8', '.svg':'image/svg+xml', '.png':'image/png', '.jpg':'image/jpeg', '.jpeg':'image/jpeg', '.webp':'image/webp', '.ico':'image/x-icon', '.woff':'font/woff', '.woff2':'font/woff2', '.ttf':'font/ttf', '.gz':'application/gzip' };
const noStore = { 'Cache-Control':'no-store', 'X-Content-Type-Options':'nosniff', 'Referrer-Policy':'no-referrer', 'X-Frame-Options':'DENY' };
function send(res, status, body, headers = {}) {
  res.writeHead(status, { ...noStore, 'Content-Type':'application/json; charset=utf-8', ...headers });
  res.end(typeof body === 'string' || Buffer.isBuffer(body) ? body : JSON.stringify(body));
}
function redirect(res, location, cookies) { send(res, 303, '', { Location: location, ...(cookies ? { 'Set-Cookie':cookies } : {}) }); }
async function jsonBody(req) {
  const chunks = []; let size = 0;
  for await (const chunk of req) {
    size += chunk.length;
    if (size > 131072) throw new ServiceError(413, 'The comment is too long.');
    chunks.push(chunk);
  }
  try { return JSON.parse(Buffer.concat(chunks).toString('utf8')); }
  catch { throw new ServiceError(400, 'Invalid request.'); }
}
function page(title, content) {
  return `<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>${escape(title)}</title><style>body{margin:10vh auto;padding:24px;max-width:640px;background:#0e1624;color:#d5deec;font:16px/1.65 system-ui}h1{line-height:1.2}a{color:#b6cef4}button{padding:12px 18px;background:#b6cef4;color:#10203a;border:0;border-radius:6px;font:inherit}li{margin:12px 0}</style><h1>${escape(title)}</h1>${content}</html>`;
}

export async function createService({ root = ROOT, origin, setupOrigin = origin, configFile, setupToken = '', request = fetch, github: suppliedGitHub, auth: suppliedAuth, appConfig, apiOnly = false } = {}) {
  root = await realpath(root);
  const base = new URL(origin);
  if (base.origin !== origin || !(base.protocol === 'https:' || (base.protocol === 'http:' && ['127.0.0.1','localhost','[::1]'].includes(base.hostname)))) throw new Error('Use a fixed HTTPS origin, or loopback for local testing.');
  const setupBase = new URL(setupOrigin);
  if (setupOrigin !== origin && !(setupBase.origin === setupOrigin && setupBase.protocol === 'http:' && ['127.0.0.1','localhost','[::1]'].includes(setupBase.hostname))) throw new Error('A separate app-registration origin must be loopback.');
  if (configFile && (path.resolve(configFile) === root || path.resolve(configFile).startsWith(root + path.sep))) throw new Error('Keep GitHub app credentials outside the website checkout.');
  const config = { repository:'hodge-computer/sextics', ...appConfig };
  if (configFile) {
    try { Object.assign(config, JSON.parse(await readFile(configFile, 'utf8'))); }
    catch (error) { if (error.code !== 'ENOENT') throw error; }
  }
  if (config.repository !== 'hodge-computer/sextics') throw new Error('Unexpected discussion repository.');
  const github = suppliedGitHub || new GitHub(config, request), auth = suppliedAuth || new Auth(origin), setupAuth = new Auth(setupOrigin);
  // Use a distinct browser-binding cookie for app registration.
  setupAuth.flowName = setupAuth.secure ? '__Host-hodge_setup' : 'hodge_setup';
  const catalogue = JSON.parse(await readFile(path.join(root, 'data/catalogue.json'), 'utf8'));
  const records = Array.isArray(catalogue) ? catalogue : catalogue.instanceIds || catalogue.records || catalogue.instances;
  if (!Array.isArray(records)) throw new Error('Invalid instance catalogue.');
  const instanceIds = new Set(records.map(r => typeof r === 'string' ? r : r.id));
  async function mappings() {
    let index;
    try { index = JSON.parse(await readFile(path.join(root, 'discussions/index.json'), 'utf8')); }
    catch (error) { if (error.code === 'ENOENT') throw new ServiceError(503, 'The discussion has not been connected yet.'); throw error; }
    if (index.repository !== config.repository) throw new Error('Invalid discussion repository.');
    return Object.fromEntries(Object.entries(index.instances || {}).filter(([id,entry]) => instanceIds.has(id) && entry && Number.isSafeInteger(entry.number) && entry.number > 0 && typeof entry.nodeId === 'string'));
  }
  async function mapping(id) {
    if (!instanceIds.has(id)) throw new ServiceError(404, 'Unknown instance.');
    const entry = (await mappings())[id];
    if (!entry) throw new ServiceError(503, 'The discussion has not been connected yet.');
    return entry;
  }
  async function staticFile(url, req, res) {
    let pathname;
    try { pathname = decodeURIComponent(url.pathname); } catch { throw new ServiceError(400, 'Invalid path.'); }
    if (pathname === '/') pathname = '/index.html';
    const parts = pathname.slice(1).split('/');
    if (parts.some(p => !p || p.startsWith('.') || p.includes('\\') || p.includes('\0'))) throw new ServiceError(404, 'Not found.');
    const allowed = pathname === '/index.html' || ['assets','data','leaderboard','discussions','docs'].includes(parts[0]);
    const extension = path.extname(pathname);
    if (!allowed || !mime[extension]) throw new ServiceError(404, 'Not found.');
    const target = path.join(root, ...parts);
    let resolved;
    try { resolved = await realpath(target); } catch { throw new ServiceError(404, 'Not found.'); }
    if (!resolved.startsWith(root + path.sep) || !(await stat(resolved)).isFile()) throw new ServiceError(404, 'Not found.');
    send(res, 200, req.method === 'HEAD' ? '' : await readFile(resolved), { 'Content-Type':mime[extension], 'Cache-Control':'no-cache' });
  }
  async function handler(req, res) {
    try {
      const url = new URL(req.url, origin), session = await auth.get(req.headers.cookie);
      if (url.pathname === '/api/session' && req.method === 'GET') return send(res, 200, { connected:!!config.client_id, signInUrl:`${origin}/auth/github`, user:session?.user || null, csrf:session?.csrf || null });
      if (url.pathname === '/auth/github' && req.method === 'GET') {
        if (!config.client_id) throw new ServiceError(503, 'GitHub sign-in has not been connected yet.');
        const flow = await auth.start(url.searchParams.get('returnTo'));
        const target = new URL('https://github.com/login/oauth/authorize');
        target.search = new URLSearchParams({ client_id:config.client_id, redirect_uri:`${origin}/auth/github/callback`, state:flow.state, code_challenge:flow.challenge, code_challenge_method:'S256' });
        return redirect(res, target.href, flow.cookie);
      }
      if (url.pathname === '/auth/github/callback' && req.method === 'GET') {
        const flow = await auth.finish(url.searchParams.get('state'), req.headers.cookie);
        if (url.searchParams.has('error')) return redirect(res, flow.returnTo, auth.cookie(auth.flowName, '', 0));
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
        return send(res, 200, { ok:true }, { 'Set-Cookie':await auth.remove(req.headers.cookie) });
      }
      if (url.pathname === '/api/discussion-counts' && req.method === 'GET') return send(res, 200, await readDiscussionCounts(github, await mappings(), session));
      if (url.pathname === '/api/comment-leaderboard' && req.method === 'GET') return send(res, 200, await readCommentLeaderboard(github, await mappings(), session));
      const contributor = /^\/api\/comment-leaderboard\/([^/]+)$/.exec(url.pathname);
      if (contributor && req.method === 'GET') return send(res, 200, await readContributorComments(github, await mappings(), contributor[1], session));
      if (url.pathname === '/api/profiles' && req.method === 'GET') return send(res, 200, await readProfiles(github, (url.searchParams.get('logins') || '').split(',').filter(Boolean), session));
      const match = /^\/api\/discussions\/([A-Za-z0-9-]+)(\/replies)?$/.exec(url.pathname);
      if (match) {
        const entry = await mapping(match[1]);
        if (req.method === 'GET') {
          const cursor = url.searchParams.get('after');
          if (cursor?.length > 512) throw new ServiceError(400, 'Invalid page.');
          if (match[2]) {
            const commentId = url.searchParams.get('commentId');
            if (!commentId || commentId.length > 200) throw new ServiceError(400, 'Invalid comment.');
            return send(res, 200, await readReplies(github, entry, commentId, cursor, session));
          }
          return send(res, 200, await readDiscussion(github, entry, cursor, session));
        }
        if (req.method === 'POST' && !match[2]) {
          auth.requireWrite(req, session);
          const input = await jsonBody(req);
          if (!input || typeof input.body !== 'string' || !input.body.trim() || input.body.length > 30000 || Object.keys(input).some(k => !['body','replyToId'].includes(k))) throw new ServiceError(400, 'Write a comment of at most 30,000 characters.');
          if (input.replyToId !== undefined && (typeof input.replyToId !== 'string' || input.replyToId.length > 200)) throw new ServiceError(400, 'Invalid reply.');
          await auth.claimPost(session);
          const comment = await postComment(github, entry, input.body, input.replyToId, session);
          invalidateCommentLeaderboard(github);
          return send(res, 201, comment);
        }
        throw new ServiceError(405, 'Method not allowed.');
      }
      if (url.pathname === '/auth/setup' && req.method === 'GET') {
        if (!setupToken || !configFile || config.client_id || !equal(url.searchParams.get('key'), setupToken)) throw new ServiceError(404, 'Not found.');
        const flow = setupAuth.start('/#home');
        const manifest = { name:'Sextics', url:origin, description:'Sign in to hodge.computer and join the mathematical discussion.',
          hook_attributes:{ url:`${origin}/api/github-webhook`, active:false }, public:false,
          redirect_url:`${setupOrigin}/auth/setup/callback`, callback_urls:[`${origin}/auth/github/callback`],
          default_permissions:{ discussions:'write', metadata:'read' }, default_events:[] };
        return send(res, 200, page('Connect GitHub Discussions', `<p>Create <strong>Sextics</strong>, a GitHub App owned by <strong>hodge-computer</strong>. It will request:</p><ul><li>Discussions: read and write.</li><li>Repository metadata: read.</li></ul><p>After creating it, install it only on <strong>hodge-computer/sextics</strong>. The repository stays private. Comments are posted as the user who signs in.</p><form method="post" action="https://github.com/organizations/hodge-computer/settings/apps/new?state=${escape(flow.state)}"><input type="hidden" name="manifest" value="${escape(JSON.stringify(manifest))}"><button>Create GitHub App</button></form>`), { 'Content-Type':'text/html; charset=utf-8', 'Set-Cookie':flow.cookie });
      }
      if (url.pathname === '/auth/setup/callback' && req.method === 'GET') {
        if (!setupToken || !configFile || config.client_id) throw new ServiceError(404, 'Not found.');
        setupAuth.finish(url.searchParams.get('state'), req.headers.cookie);
        const code = url.searchParams.get('code');
        if (!code || !/^[A-Za-z0-9_-]{1,512}$/.test(code)) throw new ServiceError(400, 'Invalid registration code.');
        const response = await request(`https://api.github.com/app-manifests/${code}/conversions`, { method:'POST', redirect:'error', signal:AbortSignal.timeout(20000), headers:{ Accept:'application/vnd.github+json', 'User-Agent':'hodge-computer-discussions' } });
        if (!response.ok) throw new ServiceError(502, 'GitHub app registration could not be completed.');
        const registered = await response.json();
        if (!registered.id || !registered.client_id || !registered.client_secret || !registered.pem || !/^[a-z0-9-]+$/.test(registered.slug)) throw new ServiceError(502, 'Incomplete GitHub app registration.');
        const saved = { repository:config.repository, id:registered.id, slug:registered.slug, client_id:registered.client_id, client_secret:registered.client_secret, pem:registered.pem };
        await mkdir(path.dirname(configFile), { recursive:true, mode:0o700 });
        await writeFile(configFile, JSON.stringify(saved), { flag:'wx', mode:0o600 });
        Object.assign(config, saved);
        return send(res, 200, page('Install the discussion app', `<p>The app has been created. Complete the connection by installing it on <strong>hodge-computer/sextics</strong>.</p><p><a href="https://github.com/apps/${escape(saved.slug)}/installations/new">Choose the repository on GitHub →</a></p><p>Then return to the website and use “Sign in with GitHub”.</p><p><a href="/#home">Return to hodge.computer →</a></p>`), { 'Content-Type':'text/html; charset=utf-8', 'Set-Cookie':setupAuth.cookie(setupAuth.flowName, '', 0) });
      }
      if (url.pathname.startsWith('/api/') || url.pathname.startsWith('/auth/')) throw new ServiceError(404, 'Not found.');
      if (!['GET','HEAD'].includes(req.method)) throw new ServiceError(405, 'Method not allowed.');
      if (apiOnly) throw new ServiceError(404, 'Not found.');
      return await staticFile(url, req, res);
    } catch (error) {
      const status = error instanceof ServiceError ? error.status : 500;
      const message = status === 500 ? 'The request could not be completed. Please try again.' : error.message;
      // Do not log request URLs, tokens, OAuth codes, cookies, or upstream responses.
      send(res, status, { error:message });
    }
  }
  const server = http.createServer(handler);
  server.requestTimeout = 30000; server.headersTimeout = 10000;
  return { server, handler, auth, github, config };
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const port = Number(process.env.HODGE_PORT || 8772);
  const origin = process.env.HODGE_ORIGIN || `http://127.0.0.1:${port}`;
  const service = await createService({ root:process.env.HODGE_SITE_ROOT || ROOT, origin, setupOrigin:process.env.HODGE_SETUP_ORIGIN || origin, configFile:process.env.HODGE_GITHUB_APP_CONFIG, setupToken:process.env.HODGE_SETUP_TOKEN });
  service.server.listen(port, '127.0.0.1', () => console.log(`Local discussion service ready on port ${port}`));
}
