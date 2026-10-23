/* Credits are derived from instance records; they do not confer formal acceptance. */
(() => {
  'use strict';
  function rank(data, records) {
    if (
      data?.schemaVersion !== 2 ||
      data.basis !== 'accepted-proofs' ||
      !Array.isArray(data.credits)
    )
      throw new Error('Invalid leaderboard data.');
    const known = new Map(records.map((record) => [record.id, record])),
      accounts = new Map();
    for (const credit of data.credits) {
      const login = credit?.githubLogin;
      if (typeof login !== 'string' || !/^[a-z\d](?:[a-z\d-]{0,37}[a-z\d])?$/i.test(login))
        throw new Error('Invalid account.');
      const record = known.get(credit.instanceId),
        key = login.toLowerCase();
      if (
        !record ||
        record.formalStatus !== 'proved' ||
        record.credit?.githubLogin.toLowerCase() !== key
      )
        throw new Error('Credit does not match the instance.');
      if (!accounts.has(key))
        accounts.set(key, {
          githubLogin: login,
          solves: new Set(),
          baseline: new Set(),
          scoreReachedAt: 0
        });
      const account = accounts.get(key);
      if (!account.solves.has(record.id)) {
        const acceptedAt = Date.parse(credit.acceptedAt);
        if (!Number.isFinite(acceptedAt)) throw new Error('Missing acceptance date.');
        account.scoreReachedAt = Math.max(account.scoreReachedAt, acceptedAt);
      }
      account.solves.add(record.id);
      if (credit.origin === 'starting-example') account.baseline.add(record.id);
    }
    const rows = [...accounts.values()]
      .filter((a) => a.solves.size)
      .map((a) => ({
        githubLogin: a.githubLogin,
        score: a.solves.size,
        startingExamples: a.baseline.size,
        instanceIds: [...a.solves],
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
