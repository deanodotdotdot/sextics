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
      (parts.length < 3 || parts[2] === 'discussion') &&
      (parts.length < 4 || /^\d+$/.test(parts[3]))
    ) {
      return {
        page: 'case',
        caseId: parts[1],
        discussion: parts[2] === 'discussion',
        comment: parts[3] || null
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
  const api = { parse, leaderboard };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.HodgeRoutes = api;
})(globalThis);
