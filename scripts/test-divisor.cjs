// Independent double-precision reference for the generated fragment expression.
// This is test-only arithmetic: the website never samples D at mesh vertices.
const assert = require('node:assert/strict'),
  fs = require('node:fs'),
  path = require('node:path');
require('../assets/divisor.js');
const cm = (a, b) => [a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]],
  ca = (a, b) => [a[0] + b[0], a[1] + b[1]];
const scalar = (x, y = 0) => ({ v: [x, y], g: Array.from({ length: 6 }, () => [0, 0]) });
const add = (a, b) => ({ v: ca(a.v, b.v), g: a.g.map((g, j) => ca(g, b.g[j])) });
const mul = (a, b) => ({ v: cm(a.v, b.v), g: a.g.map((g, j) => ca(cm(g, b.v), cm(a.v, b.g[j]))) });
const power = (a, n) => {
  let r = scalar(1);
  for (let j = 0; j < n; j++) r = mul(r, a);
  return r;
};
function reference(formula, signs, point) {
  const scale = Math.max(...point.map(Math.abs)),
    x = point.map((p) => p / scale),
    z = x.map((p, j) => {
      const v = signs[j] < 0 ? scalar(0, p) : scalar(p);
      v.g[j] = signs[j] < 0 ? [0, 1] : [1, 0];
      return v;
    });
  const sparse = (terms, variables) =>
    terms.reduce(
      (out, [c, e]) =>
        add(
          out,
          e.reduce(
            (v, n, j) => mul(v, power(variables[j], n)),
            Array.isArray(c) ? scalar(...c) : scalar(c)
          )
        ),
      scalar(0)
    );
  let factors = [];
  if (Array.isArray(formula)) {
    const common = signs.map((_, j) => Math.min(...formula.map(([, e]) => e[j])));
    for (let j = 0; j < 6; j++) if (common[j]) factors.push(z[j]);
    factors.push(
      sparse(
        formula.map(([c, e]) => [c, e.map((n, j) => n - common[j])]),
        z
      )
    );
  } else {
    const values = [];
    for (const [op, a, b] of formula.nodes) {
      let v;
      if (op === 'variable') v = z[a];
      else if (op === 'rational') {
        const [p, q = 1] = a.split('/');
        v = scalar(Number(p) / Number(q));
      } else if (op === 'sqrt') v = scalar(Math.sqrt(a));
      else if (op === 'add') v = add(values[a], values[b]);
      else if (op === 'mul') v = mul(values[a], values[b]);
      else if (op === 'pow') v = power(values[a], b);
      else throw Error(op);
      values.push(v);
    }
    const seen = new Set();
    function collect(n) {
      if (seen.has(n)) return;
      seen.add(n);
      const [op, a, b] = formula.nodes[n];
      if (op === 'mul') {
        collect(a);
        collect(b);
      } else if (op === 'pow') collect(a);
      else factors.push(values[n]);
    }
    collect(formula.output);
  }
  let result = Infinity;
  for (const f of factors) {
    const norm = Math.hypot(...f.g.flat());
    if (norm) result = Math.min(result, Math.hypot(...f.v) / norm);
    else if (!Math.hypot(...f.v)) return 0;
  }
  return result;
}
function fixtures() {
  const root = path.join(__dirname, '../data'),
    out = [];
  for (const id of fs.readdirSync(root)) {
    const file = path.join(root, id, 'record.json');
    if (!fs.existsSync(file)) continue;
    const r = JSON.parse(fs.readFileSync(file));
    if (r.status !== 'solved') continue;
    const formula = r.render.divisorProgram || r.render.divisorTerms;
    // Accepted existence proofs need not supply a drawable denominator.
    // A saved divisor must still be present in the generated rendering data.
    if (!formula) {
      assert.equal(r.evidenceKind, 'existence-proof', 'Missing D: ' + id);
      assert.ok(
        !r.D && !fs.existsSync(path.join(root, id, 'display-divisor.json')),
        'Missing saved D: ' + id
      );
      continue;
    }
    out.push({ id, formula, signs: r.render.phaseSigns, plane: r.render.planeMatrix });
  }
  for (const mask of Array.from({ length: 64 }, (_, j) => j))
    for (const id of ['one-reflection', 'two-ternary-dense-two-odd-hessian-d48']) {
      const base = out.find((f) => f.id === id);
      out.push({
        ...base,
        id: id + '-phase-' + mask,
        signs: Array.from({ length: 6 }, (_, j) => (mask & (1 << j) ? -1 : 1))
      });
    }
  return out;
}
function jsField(source, point) {
  const make = (v, a = [0, 0, 0], b = [0, 0, 0]) => ({ v, a, b }),
    dc = (v) => make(v),
    da = (x, y) =>
      make(
        x.v + y.v,
        x.a.map((v, j) => v + y.a[j]),
        x.b.map((v, j) => v + y.b[j])
      ),
    dm = (x, y) =>
      make(
        x.v * y.v,
        x.a.map((v, j) => v * y.v + x.v * y.a[j]),
        x.b.map((v, j) => v * y.v + x.v * y.b[j])
      );
  const divisorDistance = (r, i, complex) => {
    const n = Math.hypot(...r.a, ...r.b, ...i.a, ...i.b);
    return (complex ? Math.hypot(r.v, i.v) : r.v) / (n || 1);
  };
  let body = source.split('float divisorField(vec3 a,vec3 b) {')[1];
  body = body
    .slice(body.indexOf('DivJet d'), body.lastIndexOf('}'))
    .replace(/\bDivJet (d\d+)=/g, 'const $1=')
    .replace(/\bfloat /g, 'let ')
    .replace(/\bDivJet\(/g, 'make(')
    .replace(/vec3\(([^()]*)\)/g, '[$1]')
    .replace(/\b(min|abs|sign)\(/g, 'Math.$1(');
  const scale = Math.max(...point.map(Math.abs)),
    x = point.map((v) => v / scale);
  return new Function('a', 'b', 'make', 'dc', 'da', 'dm', 'divisorDistance', body)(
    x.slice(0, 3),
    x.slice(3),
    make,
    dc,
    da,
    dm,
    divisorDistance
  );
}
function run() {
  let count = 0,
    max = 0;
  for (const f of fixtures()) {
    const pixel = HodgeDivisor.fragment(f.formula, f.signs, f.plane);
    assert.ok(pixel.operations > 0 && pixel.operations <= 4096);
    for (let k = 0; k < 12; k++) {
      const point = Array.from({ length: 6 }, (_, j) => Math.sin(k * 1.7 + j * 1.9 + 0.3));
      const a = Math.abs(jsField(pixel.source, point)),
        b = reference(f.formula, f.signs, point),
        delta = Math.abs(a - b);
      assert.ok(Number.isFinite(a) && delta < 1e-8, `${f.id}: ${a} != ${b}`);
      max = Math.max(max, delta);
      count++;
    }
  }
  assert.deepEqual(Object.keys(HodgeDivisor), ['fragment']);
  console.log(
    `${count} generated expression comparisons, all saved divisors and 64 phase choices for both large formulas; max error ${max}.`
  );
}
if (require.main === module) run();
module.exports = { fixtures, reference };
