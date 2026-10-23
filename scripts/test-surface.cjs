// Failure-path regression tests. No GPU or external service required.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const { gzipSync } = require('node:zlib');
const path = require('node:path');
const source = (name) => fs.readFileSync(path.join(__dirname, '../assets', name), 'utf8');
const event = (target, name, props = {}) =>
  target.dispatchEvent(Object.assign(new Event(name), props));

function core({ floatTargets = true, framebufferComplete = true, reducedMotion = true } = {}) {
  let now = 0,
    raf = null,
    lost = false,
    waiting = false,
    resumeFetch;
  const calls = [],
    status = [],
    failures = [];
  const gl = new Proxy(
    {},
    {
      get(target, name) {
        if (typeof name !== 'string') return target[name];
        if (name.toUpperCase() === name) return name;
        if (name === 'isContextLost') return () => lost;
        return (...args) => {
          calls.push(name);
          if (lost) throw new Error('Used a lost WebGL context: ' + name);
          if (name === 'getError') return 'NO_ERROR';
          if (name === 'getExtension') return floatTargets ? {} : null;
          if (name === 'checkFramebufferStatus')
            return framebufferComplete ? 'FRAMEBUFFER_COMPLETE' : 'INCOMPLETE';
          if (name === 'getShaderParameter' || name === 'getProgramParameter') return true;
          if (name === 'clientWaitSync') return waiting ? 'TIMEOUT_EXPIRED' : 'CONDITION_SATISFIED';
          if (name.startsWith('create') || name === 'getUniformLocation' || name === 'fenceSync')
            return {};
        };
      }
    }
  );
  const canvas = Object.assign(new EventTarget(), {
    clientWidth: 800,
    clientHeight: 600,
    width: 800,
    height: 600,
    getContext: () => gl
  });
  const view = Object.assign(new EventTarget(), {
    innerWidth: 800,
    innerHeight: 600,
    devicePixelRatio: 1
  });
  const page = Object.assign(new EventTarget(), { hidden: false });
  const meta = {
    format: 'indexed-p3-n3-phase2-d1-v3',
    stride: 9,
    edgeBound: 1,
    phaseSigns: [1, 1, 1, 1, 1, 1],
    vertexCount: 3,
    triangleCount: 1,
    positionMin: [0, 0, 0],
    positionMax: [0.1, 0.1, 0.1],
    centerOriginal: [0, 0, 0],
    displayScale: 10,
    planeMatrix: Array.from({ length: 6 }, () => [0, 0, 0, 0])
  };
  const vertices = new Float32Array([
    0, 0, 0, 0, 0, 1, 0, 0, 0, 0.1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0.1, 0, 0, 0, 1, 0, 0, 0
  ]);
  const context = {
    AbortController,
    Blob,
    DecompressionStream,
    setTimeout,
    URL,
    Float32Array,
    Float64Array,
    Uint16Array,
    Int16Array,
    Uint32Array,
    Uint8Array,
    ArrayBuffer,
    Map,
    performance: { now: () => now },
    location: { href: 'http://localhost/assets/surface-worker.js' },
    requestAnimationFrame: (fn) => ((raf = fn), 1),
    cancelAnimationFrame: () => {
      raf = null;
    },
    fetch: async (url) => {
      await new Promise((resolve) => {
        if (context.pauseFetch) resumeFetch = resolve;
        else resolve();
      });
      return {
        ok: true,
        json: async () => ({
          encoding: 'float32-p3-n3-phase2-d1',
          meta,
          vertices: 'vertices.bin.gz',
          indices: 'indices.bin.gz'
        }),
        arrayBuffer: async () => {
          const data = String(url).includes('indices') ? new Uint32Array([0, 1, 2]) : vertices;
          const compressed = gzipSync(Buffer.from(data.buffer));
          return compressed.buffer.slice(
            compressed.byteOffset,
            compressed.byteOffset + compressed.byteLength
          );
        }
      };
    }
  };
  vm.runInNewContext(source('divisor.js'), context);
  vm.runInNewContext(source('mesh.js'), context);
  vm.runInNewContext(source('renderer.js'), context);
  const renderer = context.HodgeSurfaceCore.create(canvas, {
    host: { view, page, reducedMotion },
    onStatus: (s) => status.push(s),
    onFatal: (message) => failures.push(message)
  });
  const record = {
    id: 'test',
    title: 'Test surface',
    render: {
      mesh: 'meshes/test.json',
      camera: { orientation: [0.5, 0.5, 0.5, 0.5], distance: 8, center: [0, 0, 0] }
    }
  };
  return {
    renderer,
    record,
    calls,
    status,
    failures,
    view,
    page,
    frame(time) {
      now = time;
      const fn = raf;
      raf = null;
      fn?.(now);
    },
    lose(emit = true) {
      lost = true;
      if (emit) event(canvas, 'webglcontextlost');
    },
    restore() {
      lost = false;
      event(canvas, 'webglcontextrestored');
    },
    wait(value) {
      waiting = value;
    },
    pause() {
      context.pauseFetch = true;
    },
    resume() {
      context.pauseFetch = false;
      resumeFetch();
    }
  };
}

function controller({
  supported = true,
  transferThrows = false,
  hidden = false,
  mobile = false,
  permissionRequired = false,
  permissionState,
  reducedMotion = false,
  secure = true
} = {}) {
  let now = 0,
    timer,
    replacement = 0;
  const workers = [],
    states = [],
    canvases = [];
  function makeCanvas() {
    const canvas = Object.assign(new EventTarget(), {
      clientWidth: 800,
      clientHeight: 600,
      style: {},
      classList: { toggle() {}, remove() {} },
      setAttribute() {},
      cloneNode: makeCanvas,
      replaceWith: () => replacement++
    });
    if (supported)
      canvas.transferControlToOffscreen = () => {
        if (transferThrows) throw Error('Transfer failed');
        return {};
      };
    canvases.push(canvas);
    return canvas;
  }
  const canvas = makeCanvas();
  const window = new EventTarget(),
    document = Object.assign(new EventTarget(), {
      hidden,
      currentScript: { src: 'http://localhost/assets/surface.js' }
    });
  window.isSecureContext = secure;
  window.screen = { orientation: { angle: 0 } };
  if (mobile) window.DeviceOrientationEvent = function () {};
  if (permissionRequired)
    window.DeviceOrientationEvent.requestPermission = () => {
      throw Error('Must never request sensor permission');
    };
  if (permissionState)
    window.navigator = {
      permissions: {
        query() {
          if (permissionState === 'unsupported') throw new TypeError('Unknown permission');
          return Promise.resolve({ state: permissionState });
        }
      }
    };
  class Worker {
    constructor() {
      this.messages = [];
      workers.push(this);
    }
    postMessage(message) {
      this.messages.push(message);
    }
    terminate() {
      this.terminated = true;
    }
    emit(type, value) {
      this.onmessage({ data: { type, value } });
    }
  }
  const context = {
    window,
    document,
    Worker,
    URL,
    console: { warn() {} },
    innerWidth: 800,
    innerHeight: 600,
    devicePixelRatio: 1,
    matchMedia: (q) => ({
      matches: q.includes('prefers-reduced-motion')
        ? reducedMotion
        : q.includes('pointer: coarse') && mobile
    }),
    performance: { now: () => now },
    setInterval: (fn) => ((timer = fn), 1),
    clearInterval: () => {
      timer = null;
    }
  };
  vm.runInNewContext(source('surface.js'), context);
  const api = window.HodgeRenderer.create(canvas, { onStatus: (s) => states.push(s) });
  return {
    api,
    states,
    workers,
    canvases,
    window,
    document,
    replacement: () => replacement,
    tick(time) {
      now = time;
      timer?.();
    },
    time(time) {
      now = time;
    },
    pulse() {
      workers.at(-1).emit('pulse');
    },
    hidden(value) {
      document.hidden = value;
      event(document, 'visibilitychange');
    }
  };
}

(async () => {
  // Tilt is relative to the initial pose, bounded, screen-oriented, and silent
  // on platforms that require permission. Finger scrolling cannot override it.
  const tilt = controller({ mobile: true });
  const readings = () => tilt.workers[0].messages.filter((m) => m.name === 'parallax');
  const orient = (time, props = {}) => {
    tilt.time(time);
    event(tilt.window, 'deviceorientation', { alpha: 0, beta: 60, gamma: 0, ...props });
  };
  orient(0);
  assert.equal(readings().at(-1).properties.x, 0);
  orient(40, { gamma: 9 });
  assert.ok(Math.abs(readings().at(-1).properties.x - 0.5) < 1e-9);
  const readingCount = readings().length;
  orient(41, { gamma: 15 });
  assert.equal(readings().length, readingCount);
  orient(80, { beta: null });
  assert.equal(readings().length, readingCount);
  orient(90, { alpha: null });
  assert.equal(readings().length, readingCount);
  orient(120, { gamma: 60 });
  assert.equal(readings().at(-1).properties.x, 1);
  const inputs = tilt.workers[0].messages.length;
  event(tilt.window, 'pointermove', { pointerType: 'touch', clientX: 20, clientY: 20 });
  assert.equal(tilt.workers[0].messages.length, inputs);
  tilt.window.screen.orientation.angle = 90;
  orient(160);
  orient(200, { beta: 69 });
  assert.ok(Math.abs(readings().at(-1).properties.x - 0.5) < 1e-9);
  assert.ok(Math.abs(readings().at(-1).properties.y) < 1e-9);
  tilt.api.setMode('free');
  const freeCount = readings().length;
  orient(240, { gamma: 20 });
  assert.equal(readings().length, freeCount);
  tilt.api.setMode('parallax');
  orient(280, { gamma: 20 });
  assert.equal(readings().at(-1).properties.x, 0);
  tilt.hidden(true);
  const hiddenCount = readings().length;
  orient(320, { gamma: 40 });
  assert.equal(readings().length, hiddenCount);
  tilt.hidden(false);
  orient(360, { gamma: 40 });
  assert.equal(readings().at(-1).properties.x, 0);
  tilt.api.destroy();
  const destroyedCount = readings().length;
  orient(400);
  assert.equal(readings().length, destroyedCount);
  for (const options of [
    { mobile: true, permissionRequired: true },
    { mobile: true, reducedMotion: true },
    { mobile: true, secure: false },
    {}
  ]) {
    const c = controller(options);
    event(c.window, 'deviceorientation', { alpha: 0, beta: 60, gamma: 20 });
    assert.equal(c.workers[0].messages.filter((m) => m.name === 'parallax').length, 0);
    c.api.destroy();
  }
  for (const permissionState of ['granted', 'prompt', 'denied', 'unsupported']) {
    const c = controller({ mobile: true, permissionRequired: true, permissionState });
    await new Promise((resolve) => setImmediate(resolve));
    event(c.window, 'deviceorientation', { alpha: 0, beta: 60, gamma: 20 });
    assert.equal(
      c.workers[0].messages.filter((m) => m.name === 'parallax').length,
      permissionState === 'granted' ? 1 : 0
    );
    c.api.destroy();
  }

  // Generate physical device rotations independently with matrices, then encode
  // them as browser angles. Check the full input patch across upright/flat and
  // portrait/landscape poses, including the beta=90-degree representation change.
  const radians = Math.PI / 180;
  const mm = (a, b) =>
    a.map((row) => b[0].map((_, j) => row.reduce((sum, v, k) => sum + v * b[k][j], 0)));
  const rx = (t) => [
    [1, 0, 0],
    [0, Math.cos(t), -Math.sin(t)],
    [0, Math.sin(t), Math.cos(t)]
  ];
  const ry = (t) => [
    [Math.cos(t), 0, Math.sin(t)],
    [0, 1, 0],
    [-Math.sin(t), 0, Math.cos(t)]
  ];
  const rz = (t) => [
    [Math.cos(t), -Math.sin(t), 0],
    [Math.sin(t), Math.cos(t), 0],
    [0, 0, 1]
  ];
  function sensorAngles(m) {
    let beta = Math.asin(Math.max(-1, Math.min(1, m[2][1])));
    let alpha = Math.atan2(-m[0][1], m[1][1]);
    let gamma = Math.atan2(-m[2][0], m[2][2]);
    if (Math.abs(gamma) > Math.PI / 2) {
      gamma -= Math.sign(gamma) * Math.PI;
      beta = Math.sign(beta) * Math.PI - beta;
      alpha += Math.PI;
    }
    return {
      alpha: (alpha / radians + 360) % 360,
      beta: beta / radians,
      gamma: gamma / radians
    };
  }
  for (const angle of [0, 90, 180, 270]) {
    for (const [alpha, beta, gamma] of [
      [359, 0, 0],
      [37, 60, 0],
      [20, 89.5, 35],
      [220, 91, -20],
      [149, -75, 40]
    ]) {
      const c = controller({ mobile: true });
      c.window.screen.orientation.angle = angle;
      const initial = mm(mm(rz(alpha * radians), rx(beta * radians)), ry(gamma * radians));
      event(c.window, 'deviceorientation', { alpha, beta, gamma });
      let time = 40;
      for (const x of [-0.5, 0, 0.5])
        for (const y of [-0.5, 0, 0.5]) {
          // Convert screen axes back to device axes before applying the tilt.
          const s = Math.sin(angle * radians),
            cs = Math.cos(angle * radians);
          const local = mm(
            rx((x * s + y * cs) * 18 * radians),
            ry((x * cs - y * s) * 18 * radians)
          );
          c.time(time);
          time += 40;
          event(c.window, 'deviceorientation', sensorAngles(mm(initial, local)));
          const actual = c.workers[0].messages
            .filter((m) => m.name === 'parallax')
            .at(-1).properties;
          assert.ok(
            Math.abs(actual.x - x) < 0.005 && Math.abs(actual.y - y) < 0.005,
            `Tilt at ${alpha},${beta},${gamma}; screen ${angle}; expected ${x},${y}, got ${actual.x},${actual.y}`
          );
        }
      c.api.destroy();
    }
  }
  console.log(
    'Tilt parallax: calibration, bounds, throttling, portrait/landscape, scroll, free mode, visibility, cleanup, reduced motion, incomplete readings and permission handling passed.'
  );
  // Saved poses can include roll. It survives reset and returning to the
  // background view; selecting a different saved pose replaces it.
  const pose = core(),
    quaternion = [
      0.7848410404195184, 0.12778571965730126, 0.5102919966531698, -0.32756286309133836
    ];
  const rolled = {
    ...pose.record,
    render: {
      ...pose.record.render,
      camera: { ...pose.record.render.camera, orientation: quaternion }
    }
  };
  const samePose = () =>
    assert.ok(
      Math.abs(
        pose.renderer.getCamera().orientation.reduce((s, v, i) => s + v * quaternion[i], 0)
      ) >
        1 - 1e-12
    );
  await pose.renderer.setCase(rolled);
  samePose();
  pose.frame(100);
  pose.frame(150);
  samePose();
  pose.renderer.setMode('free');
  pose.renderer.resetCamera();
  samePose();
  pose.renderer.setMode('parallax');
  pose.frame(200);
  pose.frame(250);
  samePose();
  await pose.renderer.setCase(pose.record);
  const unrolled = core();
  await unrolled.renderer.setCase(unrolled.record);
  assert.deepEqual(
    Array.from(pose.renderer.getCamera().orientation),
    Array.from(unrolled.renderer.getCamera().orientation)
  );
  for (const orientation of [undefined, [0, 0, 0, 0], [0, 0, 1], [0, NaN, 0, 1]]) {
    await assert.rejects(
      pose.renderer.setCase({
        ...rolled,
        render: { ...rolled.render, camera: { ...rolled.render.camera, orientation } }
      }),
      /orientation/i
    );
  }
  pose.renderer.destroy();
  unrolled.renderer.destroy();

  // Missing float targets or incomplete framebuffers pause the view without
  // changing precision or replacing x-ray rendering with an opaque surface.
  for (const capability of [{ floatTargets: false }, { framebufferComplete: false }]) {
    const unsupported = core(capability);
    await unsupported.renderer.setCase({
      ...unsupported.record,
      render: {
        ...unsupported.record.render,
        camera: { ...unsupported.record.render.camera, distance: 1 }
      }
    });
    unsupported.frame(100);
    assert.equal(unsupported.failures.length, 1);
    assert.equal(unsupported.status.at(-1).state, 'error');
    assert.equal(unsupported.calls.includes('drawElements'), false);
    unsupported.renderer.destroy();
  }

  // Project actual camera movement onto the saved view's screen axes. Every
  // saved pose, including rolled cameras, must respond on two independent axes.
  const root = path.join(__dirname, '..');
  const ids = JSON.parse(fs.readFileSync(path.join(root, 'data/catalogue.json'))).instanceIds;
  const dot = (a, b) => a.reduce((sum, value, i) => sum + value * b[i], 0);
  const basis = ([x, y, z, w]) => ({
    right: [1 - 2 * (y * y + z * z), 2 * (x * y + w * z), 2 * (x * z - w * y)],
    up: [2 * (x * y - w * z), 1 - 2 * (x * x + z * z), 2 * (y * z + w * x)],
    back: [2 * (x * z + w * y), 2 * (y * z - w * x), 1 - 2 * (x * x + y * y)]
  });
  async function movedCamera(orientation, input) {
    const c = core({ reducedMotion: false });
    await c.renderer.setCase({
      ...c.record,
      render: {
        ...c.record.render,
        camera: { ...c.record.render.camera, orientation }
      }
    });
    if (input.phone) event(c.view, 'parallax', input.phone);
    else
      event(c.view, 'pointermove', {
        clientX: (input.x + 1) * 400,
        clientY: (input.y + 1) * 300
      });
    c.frame(100);
    const camera = c.renderer.getCamera();
    c.renderer.destroy();
    return JSON.parse(JSON.stringify(camera));
  }
  for (const id of [...ids, 'home']) {
    const { orientation } = JSON.parse(
      fs.readFileSync(path.join(root, `slices/${id}.json`))
    ).camera;
    const axes = basis(orientation);
    const views = await Promise.all(
      [
        { x: 0, y: 0 },
        { x: 0.5, y: 0 },
        { x: 0, y: 0.5 }
      ].map((input) => movedCamera(orientation, input))
    );
    const angles = views.map((camera) => {
      const back = basis(camera.orientation).back;
      return [
        Math.atan2(dot(back, axes.right), dot(back, axes.back)),
        Math.asin(dot(back, axes.up))
      ];
    });
    const horizontal = angles[1].map((v, i) => v - angles[0][i]);
    const vertical = angles[2].map((v, i) => v - angles[0][i]);
    assert.ok(
      horizontal[0] > 0.02 && Math.abs(horizontal[1]) < 0.0001,
      `${id}: horizontal parallax`
    );
    assert.ok(vertical[1] < -0.015 && Math.abs(vertical[0]) < 0.0001, `${id}: vertical parallax`);
    const phone = await movedCamera(orientation, { phone: { x: 0.5, y: 0 } });
    assert.deepEqual(phone, views[1], `${id}: mouse and phone share camera motion`);
  }
  console.log(
    'Parallax: independent horizontal/vertical movement for all 83 saved poses; mouse and phone agree.'
  );

  // Report ready only after the GPU confirms an actual frame, not after upload.
  let c = core();
  await c.renderer.setCase(c.record);
  assert.equal(c.status.at(-1).state, 'loading');
  c.frame(100);
  assert.equal(c.status.at(-1).state, 'loading');
  c.frame(150);
  assert.equal(c.status.at(-1).state, 'ready');

  const draws = c.calls.filter((x) => x === 'drawElements').length;
  for (let time = 200; time < 1000; time += 20) c.frame(time);
  assert.equal(c.calls.filter((x) => x === 'drawElements').length, draws);
  c.renderer.setMode('free');
  c.renderer.resetCamera();
  c.frame(1100);
  assert.ok(c.calls.filter((x) => x === 'drawElements').length > draws);

  // Switching formulas replaces the shader, but an identical formula reuses
  // it. Compiled shader objects and replaced programs must not accumulate.
  let switching = core();
  const first = {
    ...switching.record,
    formalStatus: 'proved',
    render: { ...switching.record.render, divisorTerms: [[1, [1, 0, 0, 0, 0, 0]]] }
  };
  const second = {
    ...first,
    render: { ...first.render, divisorTerms: [[1, [0, 1, 0, 0, 0, 0]]] }
  };
  await switching.renderer.setCase(first);
  await switching.renderer.setCase(first);
  assert.equal(switching.calls.filter((x) => x === 'createProgram').length, 1);
  await switching.renderer.setCase(second);
  assert.equal(switching.calls.filter((x) => x === 'createProgram').length, 2);
  assert.equal(switching.calls.filter((x) => x === 'deleteProgram').length, 1);
  assert.equal(switching.calls.filter((x) => x === 'deleteShader').length, 4);
  switching.renderer.destroy();
  assert.equal(switching.calls.filter((x) => x === 'deleteProgram').length, 2);

  // The screenshot's failure: navigation / resizing / teardown after loss or
  // restoration must never delete or bind handles from the former context.
  c.lose();
  const count = c.calls.length;
  await c.renderer.setCase(c.record);
  c.frame(200);
  c.restore();
  await c.renderer.setCase(c.record);
  c.renderer.destroy();
  assert.equal(c.calls.length, count);
  assert.equal(c.failures.length, 1);

  // A download finishing after loss cannot upload its now-stale surface.
  c = core();
  c.pause();
  const pending = c.renderer.setCase(c.record);
  c.lose();
  const before = c.calls.length;
  c.resume();
  await pending;
  assert.equal(c.calls.length, before);
  assert.equal(c.status.at(-1).state, 'error');

  // Detect loss even before the browser delivers its asynchronous lost event.
  c = core();
  c.lose(false);
  await c.renderer.setCase(c.record);
  assert.equal(c.failures.length, 1);

  // A live JS worker whose GPU never signals also has a bounded wait.
  c = core();
  await c.renderer.setCase(c.record);
  c.wait(true);
  c.frame(100);
  c.frame(5099);
  assert.equal(c.failures.length, 0);
  c.frame(5101);
  assert.match(c.failures[0], /stopped responding/);

  // Hidden-tab time is not charged to the GPU deadline.
  c = core();
  await c.renderer.setCase(c.record);
  c.wait(true);
  c.frame(100);
  c.page.hidden = true;
  c.frame(10000);
  c.page.hidden = false;
  event(c.page, 'visibilitychange');
  c.frame(10001);
  assert.equal(c.failures.length, 0);

  // A suspended animation can resume before the visibility message arrives.
  // That scheduling gap grants a fresh deadline, not an immediate GPU timeout.
  c = core();
  await c.renderer.setCase(c.record);
  c.wait(true);
  c.frame(100);
  c.frame(30000);
  assert.equal(c.failures.length, 0);
  c.frame(34999);
  assert.equal(c.failures.length, 0);
  c.frame(35001);
  assert.match(c.failures[0], /stopped responding/);

  // A blocked worker cannot block this watchdog; subsequent navigation sends
  // nothing to it and cannot overwrite the error with an eternal spinner.
  let h = controller();
  h.workers[0].emit('booting');
  await h.api.setCase({ id: 'a' });
  for (let time = 500; time <= 5500; time += 500) h.tick(time);
  assert.equal(h.workers[0].terminated, true);
  assert.equal(h.replacement(), 1);
  const sent = h.workers[0].messages.length;
  await h.api.setCase({ id: 'b' });
  h.api.setMode('free');
  h.api.destroy();
  assert.equal(h.workers[0].messages.length, sent);
  assert.equal(h.states.at(-1).state, 'error');

  // Allow the worker script itself to download before its heartbeat starts.
  h = controller();
  for (let time = 500; time <= 10000; time += 500) h.tick(time);
  assert.equal(h.workers[0].terminated, undefined);
  h.workers[0].emit('booting');
  for (let time = 10500; time <= 15500; time += 500) h.tick(time);
  assert.equal(h.workers[0].terminated, true);
  h = controller();
  for (let time = 500; time <= 30500; time += 500) h.tick(time);
  assert.equal(h.workers[0].terminated, true);
  assert.match(h.states.at(-1).message, /downloading/);

  // Slow network while the worker remains responsive is not a graphics hang.
  h = controller();
  for (let time = 1000; time < 15000; time += 1000) {
    h.pulse();
    h.tick(time);
  }
  assert.equal(h.workers[0].terminated, undefined);
  h.hidden(true);
  h.tick(40000);
  h.hidden(false);
  h.tick(40001);
  assert.equal(h.workers[0].terminated, undefined);

  // Background context loss defers a fresh canvas/worker until foregrounded.
  // The latest selection and camera mode survive; old GPU handles do not.
  h = controller();
  await h.api.setCase({ id: 'a' });
  h.api.setMode('free');
  h.hidden(true);
  h.workers[0].emit('fatal', 'Context lost');
  assert.equal(h.workers[0].terminated, true);
  assert.equal(h.workers.length, 1);
  assert.equal(h.states.at(-1).state, 'loading');
  await h.api.setCase({ id: 'b' });
  h.time(30000);
  h.hidden(false);
  assert.equal(h.workers.length, 2);
  assert.equal(h.replacement(), 1);
  assert.equal(h.workers[1].messages.find((m) => m.type === 'case').record.id, 'b');
  assert.equal(h.workers[1].messages.find((m) => m.type === 'mode').mode, 'free');
  assert.equal(h.canvases[1].style.touchAction, 'none');
  h.workers[1].emit('status', { state: 'ready', meta: { id: 'b' } });
  const messages = h.workers[1].messages.length;
  event(h.canvases[0], 'pointerdown', { pointerId: 1 });
  assert.equal(h.workers[1].messages.length, messages);
  event(h.canvases[1], 'pointerdown', { pointerId: 1 });
  assert.equal(h.workers[1].messages.length, messages + 1);
  h.workers[0].emit('fatal', 'Stale failure');
  h.workers[0].emit('status', { state: 'error' });
  h.workers[0].emit('mode', 'parallax');
  assert.equal(h.states.at(-1).state, 'ready');
  assert.equal(h.api.getMeta().id, 'b');
  assert.equal(h.api.getMode(), 'free');
  assert.equal(h.workers[1].terminated, undefined);

  // Only one attempt per return: a broken replacement stops permanently.
  h.workers[1].emit('fatal', 'Still broken');
  assert.equal(h.workers.length, 2);
  assert.equal(h.workers[1].terminated, true);
  await h.api.setCase({ id: 'c' });
  h.hidden(true);
  h.hidden(false);
  assert.equal(h.states.at(-1).state, 'error');
  assert.equal(h.workers.length, 2);

  // Browsers may deliver context loss just after visibility changes back.
  h = controller();
  h.workers[0].emit('booting');
  h.hidden(true);
  h.time(30000);
  h.hidden(false);
  h.workers[0].emit('fatal', 'Late context loss');
  assert.equal(h.workers.length, 2);
  assert.equal(h.workers[0].terminated, true);

  // A worker that never resumes is also retried once; the fresh worker still
  // has its own bounded timeout if graphics remain unresponsive.
  h = controller();
  h.workers[0].emit('booting');
  h.hidden(true);
  h.time(30000);
  h.hidden(false);
  for (let time = 30500; time <= 35500; time += 500) h.tick(time);
  assert.equal(h.workers.length, 2);
  h.workers[1].emit('booting');
  for (let time = 36000; time <= 41000; time += 500) h.tick(time);
  assert.equal(h.workers.length, 2);
  assert.equal(h.states.at(-1).state, 'error');

  // A delayed main-page timer must not mistake whole-page suspension for a
  // worker hang. Subsequent regular ticks still enforce the five-second limit.
  h = controller();
  h.workers[0].emit('booting');
  h.tick(30000);
  assert.equal(h.workers[0].terminated, undefined);
  for (let time = 30500; time <= 35500; time += 500) h.tick(time);
  assert.equal(h.workers[0].terminated, true);

  // Do not start GPU work in an initially hidden tab; replay its selection on
  // first visibility. Destroying a deferred recovery removes its listeners.
  h = controller({ hidden: true });
  await h.api.setCase({ id: 'a' });
  assert.equal(h.workers.length, 0);
  h.hidden(false);
  assert.equal(h.workers.length, 1);
  assert.equal(h.workers[0].messages.find((m) => m.type === 'case').record.id, 'a');
  h.hidden(true);
  h.workers[0].emit('fatal', 'Context lost');
  h.api.destroy();
  h.hidden(false);
  event(h.window, 'resize');
  assert.equal(h.workers.length, 1);

  h = controller({ supported: false });
  assert.equal(h.workers.length, 0);
  assert.equal(h.states.at(-1).state, 'error');
  h = controller({ transferThrows: true });
  assert.equal(h.workers[0].terminated, true);
  console.log(
    'Surface resilience: first-frame readiness, context loss/restoration, background recovery, retry limit, stale events, late loads, GPU and worker timeouts, suspension grace, slow network, unsupported browsers passed.'
  );
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
