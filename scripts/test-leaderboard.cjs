// Accepted credit only, distinct instances, identity matching, ties; no network.
const assert = require('node:assert/strict'),
  fs = require('node:fs'),
  path = require('node:path'),
  vm = require('node:vm');
const root = path.join(__dirname, '..'),
  context = { window: {} };
vm.runInNewContext(fs.readFileSync(path.join(root, 'assets/leaderboard.js'), 'utf8'), context);
const rank = (data, records) =>
  JSON.parse(JSON.stringify(context.window.HodgeLeaderboard.rank(data, records)));
const base = { schemaVersion: 2, basis: 'accepted-proofs' };
const fixtures = ['zoe', 'amy', 'amy', 'zoe', 'lee'].map((githubLogin, i) => ({
  id: String(i),
  status: 'solved',
  certificateAvailable: true,
  formalStatus: 'proved',
  credit: { githubLogin }
}));
const days = [1, 2, 5, 4, 3];
const credits = fixtures.map((r, i) => ({
  instanceId: r.id,
  githubLogin: r.credit.githubLogin,
  origin: 'contribution',
  acceptedAt: `2026-10-0${days[i]}T12:00:00Z`
}));
const data = { ...base, credits };
assert.deepEqual(
  rank(data, fixtures).map((r) => [r.githubLogin, r.rank, r.score]),
  [
    ['zoe', 1, 2],
    ['amy', 2, 2],
    ['lee', 3, 1]
  ]
);
// Zoe reached two solves first; the date a PR was opened is irrelevant.
assert.equal(
  rank(
    {
      ...base,
      credits: credits.map((c) => ({
        ...c,
        awardedAt: c.githubLogin === 'amy' ? '2020-01-01' : '2030-01-01'
      }))
    },
    fixtures
  )[0].githubLogin,
  'zoe'
);
const added = ['amy', 'zoe'].map((githubLogin, i) => ({
  ...fixtures[0],
  id: String(i + 5),
  credit: { githubLogin }
}));
const addedCredits = added.map((r, i) => ({
  instanceId: r.id,
  githubLogin: r.credit.githubLogin,
  origin: 'contribution',
  acceptedAt: `2026-10-0${i + 6}T12:00:00Z`
}));
assert.deepEqual(
  rank({ ...base, credits: [...credits, ...addedCredits] }, [...fixtures, ...added]).map((r) => [
    r.githubLogin,
    r.score
  ]),
  [
    ['amy', 3],
    ['zoe', 3],
    ['lee', 1]
  ]
);
// Exact-time ties use alphabetical login order.
assert.equal(
  rank(
    { ...base, credits: credits.map((c) => ({ ...c, acceptedAt: '2026-10-01T12:00:00Z' })) },
    fixtures
  )[0].githubLogin,
  'amy'
);
for (const acceptedAt of [undefined, 'invalid'])
  assert.throws(
    () => rank({ ...base, credits: [{ ...credits[0], acceptedAt }] }, fixtures),
    /acceptance date/
  );
assert.deepEqual(
  rank({ ...base, credits: [...credits, { ...credits[0], githubLogin: 'Zoe' }] }, fixtures),
  rank(data, fixtures)
);
for (const changed of [
  { ...credits[0], instanceId: 'missing' },
  { ...credits[0], githubLogin: 'someone-else' },
  { ...credits[0], githubLogin: 'invalid/account' }
])
  assert.throws(() => rank({ ...base, credits: [changed] }, fixtures));
for (const changed of [{ formalStatus: 'unproved' }])
  assert.throws(() => rank({ ...base, credits: [credits[0]] }, [{ ...fixtures[0], ...changed }]));
assert.deepEqual(rank({ ...base, credits: [] }, fixtures), []);
const records = JSON.parse(fs.readFileSync(path.join(root, 'data/index.json'))).records;
const live = JSON.parse(fs.readFileSync(path.join(root, 'leaderboard/credits.json')));
assert.equal(
  rank(live, records).reduce((sum, r) => sum + r.score, 0),
  new Set(live.credits.map((c) => c.instanceId)).size
);
console.log(
  'Leaderboard: accepted credit, identity matching, distinct instances, ties, and current totals passed.'
);
