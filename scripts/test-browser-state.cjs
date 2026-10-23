const test = require('node:test');
const assert = require('node:assert/strict');
const routes = require('../assets/routes.js');
const { create } = require('../assets/discussion-drafts.js');
function fixture() {
  const values = new Map();
  const storage = {
    getItem: (key) => values.get(key) || null,
    setItem: (key, value) => values.set(key, value),
    removeItem: (key) => values.delete(key)
  };
  return { drafts: create(storage), storage };
}
test('an old post cannot erase a newer draft, even with identical final text', () => {
  const { drafts, storage } = fixture();
  const submitted = drafts.save('case', 'A', null);
  drafts.save('case', 'B', null);
  drafts.save('case', 'A', null);
  assert.equal(drafts.clear('case', submitted), false);
  assert.equal(create(storage).read('case').body, 'A');
});
test('remounting preserves draft identity and successful completion clears the mounted copy', () => {
  const { drafts, storage } = fixture();
  const submitted = drafts.save('case', 'A', { id: 'parent' });
  const mounted = drafts.save('case', 'A', { id: 'parent' });
  assert.equal(mounted, submitted);
  let text = 'A';
  const unsubscribe = drafts.onClear((id, version) => {
    if (id === 'case' && version === mounted) text = '';
  });
  assert.equal(drafts.clear('case', submitted), true);
  assert.equal(text, '');
  drafts.save('case', text, null);
  assert.equal(create(storage).read('case'), undefined);
  unsubscribe();
});
test('blocked browser storage still preserves in-memory drafts', () => {
  const drafts = create({
    getItem() {
      throw Error();
    },
    setItem() {
      throw Error();
    },
    removeItem() {
      throw Error();
    }
  });
  const saved = drafts.save('case', 'A', null);
  assert.equal(drafts.read('case'), saved);
  assert.equal(drafts.clear('case', saved), true);
});
test('routes round-trip ranking mode and contributor independently of previous navigation', () => {
  for (const mode of ['comments', 'solves'])
    for (const login of [null, 'fqlx', 'comments']) {
      assert.deepEqual(routes.parse(routes.leaderboard(mode, login)), {
        page: 'leaderboard',
        mode,
        login
      });
    }
  assert.deepEqual(routes.parse('#case/holdout/discussion/123'), {
    page: 'case',
    caseId: 'holdout',
    discussion: true,
    comment: '123'
  });
  for (const hash of [
    '#case/%ZZ',
    '#case/foo/other',
    '#leaderboard/foo/comments/extra',
    '#home?next=evil',
    'https://evil.test'
  ])
    assert.equal(routes.parse(hash), null);
});
