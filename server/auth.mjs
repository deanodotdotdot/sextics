import routes from '../assets/routes.js';
import { randomBytes, createHash, timingSafeEqual } from 'node:crypto';
import { ServiceError } from './github.mjs';

const random = () => randomBytes(32).toString('base64url');
const valid = (value) => typeof value === 'string' && /^[A-Za-z0-9_-]{43}$/.test(value);
const key = (type, value) => `${type}#${createHash('sha256').update(value).digest('hex')}`;

function equal(a, b) {
  if (typeof a !== 'string' || typeof b !== 'string') return false;
  const left = Buffer.from(a),
    right = Buffer.from(b);
  return left.length === right.length && timingSafeEqual(left, right);
}
function cookies(header = '') {
  return Object.fromEntries(
    header
      .split(';')
      .map((s) => s.trim().split('='))
      .filter((parts) => parts.length === 2)
  );
}
function returnPath(value) {
  return typeof value === 'string' && value.startsWith('/#') && routes.parse(value.slice(1))
    ? value
    : '/#home';
}

export class Auth {
  constructor(origin, store) {
    this.origin = origin;
    this.store = store;
    this.sessionName = '__Host-hodge_session';
    this.flowName = '__Host-hodge_oauth';
  }
  cookie(name, value, maxAge) {
    return `${name}=${value}; Path=/; HttpOnly; SameSite=Lax; Max-Age=${maxAge}; Secure`;
  }
  async start(returnTo) {
    const state = random(),
      binding = random(),
      verifier = random();
    await this.store.put(key('flow', state), {
      binding,
      verifier,
      returnTo: returnPath(returnTo),
      expires: Date.now() + 600000
    });
    return {
      state,
      challenge: createHash('sha256').update(verifier).digest('base64url'),
      cookie: this.cookie(this.flowName, binding, 600)
    };
  }
  async finish(state, header) {
    if (!valid(state))
      throw new ServiceError(400, 'Sign-in could not be confirmed. Please try again.');
    const flow = await this.store.consume(key('flow', state));
    if (!flow || flow.expires <= Date.now() || !equal(flow.binding, cookies(header)[this.flowName]))
      throw new ServiceError(400, 'Sign-in could not be confirmed. Please try again.');
    return flow;
  }
  async create(tokens, user) {
    const id = random(),
      seconds = Math.min(8 * 3600, Number(tokens.expires_in) || 8 * 3600);
    if (seconds <= 0 || typeof tokens.access_token !== 'string' || !tokens.access_token)
      throw new ServiceError(401, 'Please sign in again.');
    await this.store.put(key('session', id), {
      token: tokens.access_token,
      user,
      csrf: random(),
      expires: Date.now() + seconds * 1000,
      lastPost: 0
    });
    return {
      id,
      cookies: [this.cookie(this.sessionName, id, seconds), this.cookie(this.flowName, '', 0)]
    };
  }
  async get(header) {
    const id = cookies(header)[this.sessionName];
    if (!valid(id)) return null;
    const storageKey = key('session', id),
      session = await this.store.get(storageKey);
    return session && session.expires > Date.now() ? { ...session, storageKey } : null;
  }
  async remove(header) {
    const id = cookies(header)[this.sessionName];
    if (valid(id)) await this.store.remove(key('session', id));
    return this.cookie(this.sessionName, '', 0);
  }
  async claimPost(session) {
    if (!session?.storageKey || !(await this.store.claimPost(session.storageKey, Date.now())))
      throw new ServiceError(429, 'Please wait a few seconds before posting again.');
  }
  requireWrite(req, session) {
    if (!session) throw new ServiceError(401, 'Sign in with GitHub to post.');
    if (req.headers.origin !== this.origin || !equal(req.headers['x-csrf-token'], session.csrf))
      throw new ServiceError(403, 'Please reload the page before posting.');
    if (!/^application\/json(?:;|$)/i.test(req.headers['content-type'] || ''))
      throw new ServiceError(415, 'Use JSON for this request.');
  }
}
