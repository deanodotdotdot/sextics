/* The browser and OAuth return validation share the same internal destinations. */
((root) => {
  function parse(hash) {
    if (typeof hash !== 'string') return null;
    let path;
    try {
      path = decodeURIComponent(hash.replace(/^#/, ''));
    } catch {
      return null;
    }
    if (!path || path === 'home') return { page: 'home' };
    if (path === 'leaderboard?mode=comments')
      return { page: 'leaderboard', mode: 'comments', login: null };
    const parts = path.split('/');
    if (
      parts[0] === 'leaderboard' &&
      parts.length <= 3 &&
      (!parts[1] || /^[A-Za-z0-9][A-Za-z0-9-]{0,38}$/.test(parts[1])) &&
      (parts.length < 3 || parts[2] === 'comments')
    ) {
      return {
        page: 'leaderboard',
        login: parts[1] || null,
        mode: parts[2] === 'comments' ? 'comments' : 'solves'
      };
    }
    if (
      parts[0] === 'case' &&
      /^[A-Za-z0-9-]+$/.test(parts[1] || '') &&
      parts.length <= 4 &&
      (parts.length < 3 || ['discussion', 'solution'].includes(parts[2])) &&
      (parts.length < 4 ||
        (parts[2] === 'discussion' ? /^\d+$/ : /^[\p{L}\p{N}_-]+$/u).test(parts[3]))
    ) {
      return {
        page: 'case',
        caseId: parts[1],
        discussion: parts[2] === 'discussion',
        solution: parts[2] === 'solution',
        comment: parts[2] === 'discussion' ? parts[3] || null : null,
        anchor: parts[2] === 'solution' ? parts[3] || null : null
      };
    }
    if (
      parts[0] === 'technical-information' &&
      parts.length <= 3 &&
      parts.slice(1).every((part) => /^[\p{L}\p{N}_-]+$/u.test(part))
    ) {
      return {
        page: 'technical-information',
        chapterId: parts[1] || null,
        anchor: parts[2] || null
      };
    }
    return null;
  }
  function leaderboard(mode, login) {
    return login
      ? '#leaderboard/' + encodeURIComponent(login) + (mode === 'comments' ? '/comments' : '')
      : mode === 'comments'
        ? '#leaderboard?mode=comments'
        : '#leaderboard';
  }
  function startLinks(records, chapters, discussions) {
    const sources = new Map(),
      threads = new Map();
    for (const record of records) {
      const route = '#case/' + record.id;
      sources.set('data/' + record.id, route);
      sources.set('data/' + record.id + '/why.md', route);
      if (record.formalStatus === 'proved')
        sources.set('data/' + record.id + '/solution.md', route + '/solution');
    }
    for (const page of chapters.pages)
      sources.set(page.source, '#technical-information/' + page.id);
    sources.set(chapters.overview.source, '#technical-information');
    for (const [id, thread] of Object.entries(discussions.instances))
      threads.set(String(thread.number), '#case/' + id + '/discussion');
    function resolve(href) {
      try {
        const url = new URL(href, location.href);
        if (!['https:', 'http:'].includes(url.protocol) || url.username || url.password || url.port)
          return null;
        if (url.hostname === 'hodge.computer' && ['/', '/index.html'].includes(url.pathname))
          return parse(url.hash) ? url.hash : null;
        const path = decodeURIComponent(url.pathname).split('/');
        if (
          url.hostname !== 'github.com' ||
          path.slice(1, 3).join('/').toLowerCase() !== discussions.repository.toLowerCase()
        )
          return null;
        if (path[3] === 'discussions' && /^\d+$/.test(path[4]) && !path.slice(5).join('/')) {
          const route = threads.get(path[4]),
            comment = /^#discussioncomment-(\d+)$/.exec(url.hash);
          return route && (!url.hash || comment || /^#discussion-\d+$/.test(url.hash))
            ? route + (comment ? '/' + comment[1] : '')
            : null;
        }
        if (!['blob', 'tree'].includes(path[3]) || path[4] !== 'main') return null;
        const route = sources.get(path.slice(5).join('/').replace(/\/$/, ''));
        if (!route) return null;
        if (url.hash && route === '#technical-information') return null;
        const anchored = route + (url.hash ? '/' + url.hash.slice(1) : '');
        return parse(anchored) ? anchored : url.hash ? null : route;
      } catch {
        return null;
      }
    }
    function localize(root) {
      for (const link of [
        ...(root.matches?.('a[href]') ? [root] : []),
        ...root.querySelectorAll('a[href]')
      ]) {
        if (link.matches('.discussion-github,[data-github-original]')) continue;
        const route = resolve(link.href);
        if (!route) continue;
        link.href = route;
        link.removeAttribute('target');
        link.removeAttribute('rel');
      }
    }
    localize(document);
    new MutationObserver((changes) => {
      for (const change of changes)
        for (const node of change.addedNodes) if (node.nodeType === 1) localize(node);
    }).observe(document.body, { childList: true, subtree: true });
  }
  const api = { parse, leaderboard, startLinks };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.HodgeRoutes = api;
})(globalThis);
