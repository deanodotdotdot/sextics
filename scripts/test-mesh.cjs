const assert = require('node:assert/strict');
const { test } = require('node:test');
const { create, validateDynamicMesh } = require('../assets/mesh.js');

test('superseding a mesh aborts its request and cannot reuse its late result', async () => {
  const original = global.fetch;
  const requests = [];
  global.fetch = (url, { signal }) =>
    new Promise((resolve, reject) => {
      requests.push({ url: String(url), signal, resolve });
      signal.addEventListener('abort', () => reject(signal.reason), { once: true });
    });
  const meshes = create('http://localhost/assets/');
  try {
    const first = meshes.load('first.json');
    const rejected = assert.rejects(first, { name: 'AbortError' });
    const second = meshes.load('second.json');
    const cancelled = assert.rejects(second, { name: 'AbortError' });
    assert.equal(requests[0].signal.aborted, true);
    assert.equal(meshes.load('second.json'), second);
    meshes.cancel();
    await Promise.all([rejected, cancelled]);
    assert.equal(requests[1].signal.aborted, true);
    assert.equal(requests.length, 2);
  } finally {
    meshes.dispose();
    global.fetch = original;
  }
});

test('geometry validation rejects invalid normals and out-of-range indices', async () => {
  const meta = {
    format: 'indexed-p3-n3-phase2-d1-v3',
    stride: 9,
    vertexCount: 3,
    triangleCount: 1,
    displayScale: 1,
    centerOriginal: [0, 0, 0],
    edgeBound: 1
  };
  const vertices = new Float32Array([
    0, 0, 0, 0, 0, 1, 0, 0, 0, 0.1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0.1, 0, 0, 0, 1, 0, 0, 0
  ]);
  const indices = new Uint32Array([0, 1, 2]);
  await validateDynamicMesh(vertices.buffer, indices.buffer, meta);
  indices[2] = 3;
  await assert.rejects(
    validateDynamicMesh(vertices.buffer, indices.buffer, meta),
    /index out of range/
  );
  indices[2] = 2;
  vertices[5] = 0;
  await assert.rejects(validateDynamicMesh(vertices.buffer, indices.buffer, meta), /normal/);
});
