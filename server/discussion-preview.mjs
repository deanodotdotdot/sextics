/* Synthetic browser fixture. No credentials, persisted comments, or external requests. */
import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import { createService } from './server.mjs';
import { ServiceError } from './github.mjs';

const root = fileURLToPath(new URL('../', import.meta.url));
const repository = 'hodge-computer/sextics';
const page = (nodes, total = nodes.length, more = false) => ({
  nodes,
  totalCount: total,
  pageInfo: { hasNextPage: more, endCursor: more ? 'next' : null }
});

export async function createPreview({ origin = 'http://127.0.0.1:8773', postDelay = 0 } = {}) {
  const { instances } = JSON.parse(
    await readFile(new URL('../discussions/index.json', import.meta.url))
  );
  const entry = instances.holdout;
  let serial = 0;
  function comment(body, extra = {}) {
    const number = ++serial;
    return {
      id: `C_local_${number}`,
      body,
      isMinimized: false,
      url: `https://github.com/${repository}/discussions/${entry.number}#discussioncomment-${number}`,
      createdAt: '2026-10-15T14:00:00Z',
      updatedAt: '2026-10-15T14:00:00Z',
      author: {
        login: 'local-tester',
        name: 'Local test account',
        url: 'https://github.com/local-tester'
      },
      discussion: { id: entry.nodeId },
      replyTo: null,
      replies: page([]),
      ...extra
    };
  }
  const first = comment(
    'Synthetic discussion: start with **homogeneity**. $D$ has degree $d$.\n\n$$\\deg N_i = d + 6q - 5.$$'
  );
  const replies = [
    comment('Check $\\gcd(D,F)=1$.', { replyTo: { id: first.id } }),
    comment('Additional reply with $q=2$.', { replyTo: { id: first.id } })
  ];
  first.replies = page(replies);
  const comments = [
    first,
    comment('This must never be shown.', { isMinimized: true }),
    comment(
      'Safety fixture: <img src=x onerror=alert(1)> [unsafe](javascript:alert(1))\n\n$\\href{javascript:alert(1)}{bad}$'
    )
  ];
  const allComments = () => comments.flatMap((c) => [c, ...c.replies.nodes]);
  function node(id) {
    const mapped = Object.values(instances).find((e) => e.nodeId === id);
    return mapped
      ? { id, comments: page(id === entry.nodeId ? comments : []) }
      : allComments().find((c) => c.id === id) || null;
  }
  const github = {
    config: { repository },
    readToken: async () => 'local-token',
    call: async (url) => ({
      login: url.split('/').at(-1),
      name: 'Synthetic profile',
      avatar_url: '/assets/favicon.svg',
      html_url: 'https://github.com/local-tester'
    }),
    async graphql(query, vars) {
      if (query.startsWith('mutation')) {
        if (postDelay) await new Promise((resolve) => setTimeout(resolve, postDelay));
        if (vars.input.body === 'SIMULATE_FAILURE')
          throw new ServiceError(502, 'Simulated outage.');
        const added = comment(vars.input.body);
        if (vars.input.replyToId) {
          const parent = comments.find((c) => c.id === vars.input.replyToId);
          added.replyTo = { id: parent.id };
          parent.replies = page([...parent.replies.nodes, added]);
        } else comments.push(added);
        return { addDiscussionComment: { comment: added } };
      }
      if (vars.ids) return { nodes: vars.ids.map(node) };
      if (vars.id) {
        const found = node(vars.id);
        return {
          node: found && {
            ...found,
            replies: vars.after
              ? page(found.replies.nodes.slice(1), found.replies.totalCount)
              : found.replies
          }
        };
      }
      const mapped = Object.values(instances).find((e) => e.number === vars.number);
      if (!mapped) return { repository: { discussion: null } };
      const selected = mapped.nodeId === entry.nodeId ? comments : [];
      const visible = vars.after
        ? selected.slice(1)
        : selected
            .slice(0, 1)
            .map((c) => ({
              ...c,
              replies: page(
                c.replies.nodes.slice(0, 1),
                c.replies.totalCount,
                c.replies.totalCount > 1
              )
            }));
      return {
        repository: {
          discussion: {
            id: mapped.nodeId,
            number: mapped.number,
            title: 'Local fixture',
            body: 'Synthetic conversation about $(F,q,A)$.',
            locked: false,
            url: `https://github.com/${repository}/discussions/${mapped.number}`,
            commentTotals: page(selected),
            comments: page(visible, selected.length, !vars.after && selected.length > 1)
          }
        }
      };
    }
  };
  const service = await createService({
    root,
    origin,
    github,
    appConfig: { client_id: 'local-fixture' }
  });
  const signed = await service.auth.create(
    { access_token: 'local-token' },
    { login: 'local-tester', name: 'Local test account', url: 'https://github.com/local-tester' }
  );
  let html = await readFile(new URL('../index.html', import.meta.url), 'utf8');
  html = html
    .replace(
      /<script defer src="assets\/surface.js[^"]*"><\/script>/,
      '<script>window.HodgeRenderer={create:()=>null};</script>'
    )
    .replace(
      'ALGEBRAIC GEOMETRY <span>/</span> OPEN RESEARCH',
      'LOCAL TEST · SYNTHETIC COMMENTS · NO MESSAGES LEAVE THIS COMPUTER'
    );
  const handler = service.server.listeners('request')[0];
  service.server.removeAllListeners('request');
  service.server.on('request', (req, res) => {
    if (new URL(req.url, origin).pathname === '/') {
      res.writeHead(200, {
        'Content-Type': 'text/html; charset=utf-8',
        'Cache-Control': 'no-store',
        'Set-Cookie': req.url.includes('signedout')
          ? 'hodge_session=; Path=/; Max-Age=0'
          : signed.cookies
      });
      res.end(html);
    } else handler(req, res);
  });
  return { ...service, signed, entry };
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const service = await createPreview({
    postDelay: Number(process.env.HODGE_PREVIEW_POST_DELAY || 0)
  });
  service.server.listen(8773, '127.0.0.1', () =>
    console.log(
      'Local synthetic discussion fixture: http://127.0.0.1:8773/#case/holdout/discussion'
    )
  );
  for (const signal of ['SIGTERM', 'SIGINT'])
    process.on(signal, () => service.server.close(() => process.exit(0)));
}
