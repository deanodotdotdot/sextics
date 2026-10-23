/* Credits are derived from instance records; they do not confer formal acceptance. */
(() => {
  'use strict';
  function rank(records) {
    const accounts = new Map();
    for (const record of records) {
      if (record.formalStatus !== 'proved') continue;
      const login = record.credit.githubLogin,
        key = login.toLowerCase();
      if (!accounts.has(key))
        accounts.set(key, {
          githubLogin: login,
          instanceIds: [],
          scoreReachedAt: 0
        });
      const account = accounts.get(key);
      const acceptedAt = Date.parse(record.credit.acceptedAt);
      if (!Number.isFinite(acceptedAt)) throw new Error('Missing acceptance date.');
      account.scoreReachedAt = Math.max(account.scoreReachedAt, acceptedAt);
      account.instanceIds.push(record.id);
    }
    const rows = [...accounts.values()]
      .map((a) => ({
        githubLogin: a.githubLogin,
        score: a.instanceIds.length,
        instanceIds: a.instanceIds,
        scoreReachedAt: a.scoreReachedAt
      }))
      .sort(
        (a, b) =>
          b.score - a.score ||
          a.scoreReachedAt - b.scoreReachedAt ||
          a.githubLogin.toLowerCase().localeCompare(b.githubLogin.toLowerCase(), 'en')
      );
    return rows.map((row, i) => ({ ...row, rank: i + 1 }));
  }
  window.HodgeLeaderboard = Object.freeze({ rank });
})();
