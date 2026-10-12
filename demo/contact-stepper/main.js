const PHASE_PREPARE = 0;
const PHASE_VELOCITY = 1;
const PHASE_WARM = 2;
const PHASE_SOLVE = 3;
const PHASE_POSITION = 4;
const PHASE_RELAX = 5;
const PHASE_COMMIT = 6;

const PHASE_NAME = ["准备", "速度积分", "热启动", "软约束求解", "位置积分", "Relax", "提交"];

const canvas = document.getElementById("view");
const ctx = canvas.getContext("2d");
const progressEl = document.getElementById("progress");
const stateEl = document.getElementById("state");
const formulaEl = document.getElementById("formula");

let moduleApi = null;
let trace = null;
let frameIndex = -1;
let bigStep = 0;

function n(value) {
  if (!Number.isFinite(value)) {
    return "—";
  }
  return value.toFixed(6);
}

function vec(x, y) {
  return `(${n(x)}, ${n(y)})`;
}

function catalogOf(id) {
  return trace.catalog.find((item) => item.id === id);
}

function nameOf(id) {
  const item = catalogOf(id);
  if (!item) {
    return `#${id}`;
  }
  if (item.name === "ground") return "地面";
  if (item.name === "boxA") return "箱子A";
  if (item.name === "boxB") return "箱子B";
  return item.name;
}

function currentFrame() {
  if (!trace || frameIndex < 0 || frameIndex >= trace.frames.length) {
    return null;
  }
  return trace.frames[frameIndex];
}

function poseOf(body) {
  const c = body.dc;
  const s = body.ds;
  const angle = Math.atan2(s, c) + body.angle;
  return {
    x: body.x + body.dx,
    y: body.y + body.dy,
    angle,
  };
}

function bodyById(frame, id) {
  return frame.bodies.find((body) => body.id === id);
}

function rotate(angle, x, y) {
  const c = Math.cos(angle);
  const s = Math.sin(angle);
  return { x: c * x - s * y, y: s * x + c * y };
}

function worldAnchor(frame, bodyId, ax, ay) {
  const body = bodyById(frame, bodyId);
  if (!body) {
    return { x: ax, y: ay };
  }
  const pose = poseOf(body);
  const deltaRot = rotate(Math.atan2(body.ds, body.dc), ax, ay);
  return { x: pose.x + deltaRot.x, y: pose.y + deltaRot.y };
}

function toScreen(x, y) {
  const scale = 150;
  return {
    x: canvas.width * 0.5 + x * scale,
    y: canvas.height * 0.72 - y * scale,
  };
}

function softnessTerms(hertz, zeta, h) {
  const omega = 2 * Math.PI * hertz;
  const a1 = 2 * zeta + h * omega;
  const a2 = h * omega * a1;
  const a3 = 1 / (1 + a2);
  return {
    omega,
    a1,
    a2,
    a3,
    biasRate: omega / a1,
    massScale: a2 * a3,
    impulseScale: a3,
  };
}

function pairKey(point) {
  const names = [nameOf(point.bodyA), nameOf(point.bodyB)].sort();
  return names.join("–");
}

function impulseOnNamedBody(point, targetName) {
  if (nameOf(point.bodyB) === targetName) {
    return { x: point.pbx, y: point.pby };
  }
  if (nameOf(point.bodyA) === targetName) {
    return { x: point.pax, y: point.pay };
  }
  return { x: 0, y: 0 };
}

function sumImpulse(points, predicate, targetName) {
  let x = 0;
  let y = 0;
  let lambda = 0;
  for (const point of points) {
    if (!predicate(point)) {
      continue;
    }
    const impulse = impulseOnNamedBody(point, targetName);
    x += impulse.x;
    y += impulse.y;
    lambda += point.nAfter;
  }
  return { x, y, lambda };
}

function isGroundPair(point) {
  const names = [nameOf(point.bodyA), nameOf(point.bodyB)];
  return names.includes("地面") && names.includes("箱子A");
}

function isStackPair(point) {
  const names = [nameOf(point.bodyA), nameOf(point.bodyB)];
  return names.includes("箱子A") && names.includes("箱子B");
}

async function loadTrace() {
  const ptr = moduleApi.json();
  const text = moduleApi.module.UTF8ToString(ptr);
  trace = JSON.parse(text);
}

function drawBox(pose, hx, hy, fill, label) {
  ctx.save();
  const origin = toScreen(pose.x, pose.y);
  ctx.translate(origin.x, origin.y);
  ctx.rotate(-pose.angle);
  ctx.fillStyle = fill;
  ctx.strokeStyle = "#d5e4f7";
  ctx.lineWidth = 1.5;
  const scale = 150;
  ctx.fillRect(-hx * scale, -hy * scale, hx * 2 * scale, hy * 2 * scale);
  ctx.strokeRect(-hx * scale, -hy * scale, hx * 2 * scale, hy * 2 * scale);
  ctx.fillStyle = "#081018";
  ctx.font = "13px Microsoft YaHei, sans-serif";
  ctx.textAlign = "center";
  ctx.fillText(label, 0, 4);
  ctx.restore();
}

function drawArrow(x0, y0, x1, y1, color) {
  const a = toScreen(x0, y0);
  const b = toScreen(x1, y1);
  ctx.strokeStyle = color;
  ctx.fillStyle = color;
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(a.x, a.y);
  ctx.lineTo(b.x, b.y);
  ctx.stroke();
  const angle = Math.atan2(b.y - a.y, b.x - a.x);
  ctx.beginPath();
  ctx.moveTo(b.x, b.y);
  ctx.lineTo(b.x - 8 * Math.cos(angle - 0.4), b.y - 8 * Math.sin(angle - 0.4));
  ctx.lineTo(b.x - 8 * Math.cos(angle + 0.4), b.y - 8 * Math.sin(angle + 0.4));
  ctx.closePath();
  ctx.fill();
}

function shortName(point) {
  return isGroundPair(point) ? "地–A" : "A–B";
}

function drawFloor(pose) {
  const top = toScreen(0, pose.y + 0.5);
  ctx.fillStyle = "#6d7c70";
  ctx.fillRect(0, top.y, canvas.width, canvas.height - top.y);
  ctx.strokeStyle = "#d5e4f7";
  ctx.beginPath();
  ctx.moveTo(0, top.y);
  ctx.lineTo(canvas.width, top.y);
  ctx.stroke();
  ctx.fillStyle = "#081018";
  ctx.font = "13px Microsoft YaHei, sans-serif";
  ctx.textAlign = "center";
  ctx.fillText("地面", canvas.width / 2, top.y + 28);
}

function roundRect(x, y, w, h) {
  ctx.beginPath();
  ctx.roundRect(x, y, w, h, 6);
}

function drawCallouts(frame) {
  const items = frame.points.map((point) => {
    const at = worldAnchor(frame, point.bodyA, point.ax, point.ay);
    return {
      point,
      at,
      screen: toScreen(at.x, at.y),
      side: isGroundPair(point) ? "left" : "right",
    };
  });

  ctx.font = "12px Microsoft YaHei, sans-serif";
  const boxH = 58;
  for (const side of ["left", "right"]) {
    const group = items.filter((item) => item.side === side).sort((a, b) => a.screen.y - b.screen.y);
    let nextY = 16;
    for (const item of group) {
      item.boxY = Math.max(nextY, item.screen.y - boxH / 2);
      nextY = item.boxY + boxH + 8;
    }
  }

  for (const item of items) {
    const tip = { x: item.at.x + item.point.nx * 0.28, y: item.at.y + item.point.ny * 0.28 };
    drawArrow(item.at.x, item.at.y, tip.x, tip.y, "#f2d16b");
    drawArrow(item.at.x, item.at.y, item.at.x + item.point.pbx * 8, item.at.y + item.point.pby * 8, "#ff8d7a");

    const lines = [
      `${shortName(item.point)} · 点${item.point.point}`,
      `s ${n(item.point.s)}`,
      `λn ${n(item.point.nAfter)}`,
    ];
    const width = 118;
    const x = item.side === "left" ? 12 : canvas.width - 12 - width;
    const y = item.boxY;
    const color = item.side === "left" ? "#d2a15a" : "#7ea0d8";
    const anchorX = item.side === "left" ? x + width : x;
    const anchorY = y + 18;
    ctx.strokeStyle = color;
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(item.screen.x, item.screen.y);
    ctx.lineTo(anchorX, anchorY);
    ctx.stroke();
    ctx.fillStyle = "rgba(16, 21, 28, 0.92)";
    roundRect(x, y, width, boxH);
    ctx.fill();
    ctx.strokeStyle = color;
    ctx.stroke();
    ctx.fillStyle = "#f7f1df";
    ctx.textAlign = "left";
    lines.forEach((line, index) => {
      ctx.fillText(line, x + 8, y + 16 + index * 16);
    });
  }
}

function draw() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = "#10151c";
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  const frame = currentFrame();
  const bodies = frame ? frame.bodies : [];
  for (const item of trace.catalog) {
    const body = bodies.find((row) => row.id === item.id);
    const pose = body
      ? poseOf(body)
      : { x: item.name === "ground" ? 0 : 0, y: item.name === "ground" ? -0.5 : item.name === "boxA" ? 0.496 : 1.492, angle: 0 };
    if (item.name === "ground") {
      drawFloor(pose);
    } else {
      const fill = item.name === "boxA" ? "#d2a15a" : "#7ea0d8";
      drawBox(pose, item.hx, item.hy, fill, nameOf(item.id));
    }
  }

  if (frame && frame.points.length > 0) {
    drawCallouts(frame);
  }
}

function metrics(pairs) {
  return `<dl class="metrics">${pairs.map(([label, value]) => `<dt>${label}</dt><dd>${value}</dd>`).join("")}</dl>`;
}

function pointCard(point) {
  return `<article class="point"><header>点 ${point.point}</header>${metrics([
    ["s", `${n(point.s)} m`],
    ["vn", `${n(point.vn)} m/s`],
    ["λn", `${n(point.nAfter)} N·s`],
    ["Δλn", n(point.nDelta)],
    ["λt", `${n(point.tAfter)} N·s`],
    ["打到 A", vec(point.pax, point.pay)],
    ["打到 B", vec(point.pbx, point.pby)],
  ])}</article>`;
}

function renderState() {
  const frame = currentFrame();
  if (!frame) {
    stateEl.innerHTML = "<p class='note'>还没有步进。点「下一步」跑完一个大步，并停在准备帧。</p>";
    formulaEl.innerHTML = "";
    return;
  }

  const ground = sumImpulse(frame.points, isGroundPair, "箱子A");
  const stack = sumImpulse(frame.points, isStackPair, "箱子B");
  const bodies = frame.bodies
    .map((body) => {
      const pose = poseOf(body);
      return `<article class="card"><h3>${nameOf(body.id)}</h3>${metrics([
        ["v", vec(body.vx, body.vy)],
        ["ω", n(body.w)],
        ["位置", vec(pose.x, pose.y)],
        ["Δp", vec(body.dx, body.dy)],
      ])}</article>`;
    })
    .join("");

  const groups = [];
  for (const point of frame.points) {
    const key = pairKey(point);
    let group = groups.find((item) => item.key === key);
    if (!group) {
      group = { key, points: [], kind: isGroundPair(point) ? "ground" : "stack" };
      groups.push(group);
    }
    group.points.push(point);
  }
  const contacts = groups
    .map(
      (group) =>
        `<section class="pair"><h3>${group.key}</h3><div class="points">${group.points.map(pointCard).join("")}</div></section>`
    )
    .join("");

  stateEl.innerHTML = `
    <div class="summary">
      <article class="card ground"><span class="k">地面 → 箱子 A</span><span class="big">${vec(ground.x, ground.y)}</span><span class="sub">Σλn ${n(ground.lambda)}</span></article>
      <article class="card stack"><span class="k">箱子 A → 箱子 B</span><span class="big">${vec(stack.x, stack.y)}</span><span class="sub">Σλn ${n(stack.lambda)}</span></article>
    </div>
    <div class="bodies" style="margin-top:8px">${bodies}</div>
    ${contacts}`;
  formulaEl.innerHTML = formulaHtml(frame);
}

function formulaCard(title, kind, pairs, equation) {
  return `<article class="card ${kind}"><h3>${title}</h3>${metrics(pairs)}${equation ? `<p class="eq">${equation}</p>` : ""}</article>`;
}

function deriveBlock(title, body) {
  return `<section class="derive"><h3>${title}</h3>${body}</section>`;
}

function prepareDerivation(header) {
  const h = header.h;
  const zeta = header.damping;
  const dynamicF = header.contactHertz;
  const staticF = header.contactHertz * 2;
  const dynamic = softnessTerms(dynamicF, zeta, h);
  const fixed = softnessTerms(staticF, zeta, h);
  const row = (symbol, left, right) => `<tr><th>${symbol}</th><td>${left}</td><td>${right}</td></tr>`;
  return deriveBlock(
    "这些数就是上面两列，按 b2MakeSoft 算出来的",
    `<table>
      <tr><th>公式</th><th>A–B，f = ${n(dynamicF)}</th><th>地面，f = ${n(staticF)}</th></tr>
      ${row("ω = 2π f", `2π × ${n(dynamicF)} = ${n(dynamic.omega)}`, `2π × ${n(staticF)} = ${n(fixed.omega)}`)}
      ${row("a1 = 2ζ + h ω", `2×${n(zeta)} + ${n(h)}×${n(dynamic.omega)} = ${n(dynamic.a1)}`, `2×${n(zeta)} + ${n(h)}×${n(fixed.omega)} = ${n(fixed.a1)}`)}
      ${row("a2 = h ω a1", `${n(h)}×${n(dynamic.omega)}×${n(dynamic.a1)} = ${n(dynamic.a2)}`, `${n(h)}×${n(fixed.omega)}×${n(fixed.a1)} = ${n(fixed.a2)}`)}
      ${row("a3 = 1 / (1 + a2)", `1 / (1 + ${n(dynamic.a2)}) = ${n(dynamic.a3)}`, `1 / (1 + ${n(fixed.a2)}) = ${n(fixed.a3)}`)}
      ${row("biasRate = ω / a1", `${n(dynamic.omega)} / ${n(dynamic.a1)} = ${n(header.contactBias)}`, `${n(fixed.omega)} / ${n(fixed.a1)} = ${n(header.staticBias)}`)}
      ${row("massScale = a2 a3", `${n(dynamic.a2)} × ${n(dynamic.a3)} = ${n(header.contactMass)}`, `${n(fixed.a2)} × ${n(fixed.a3)} = ${n(header.staticMass)}`)}
      ${row("impulseScale = a3", n(header.contactImpulse), n(header.staticImpulse))}
    </table>`
  );
}

function pointDerivation(point, relax) {
  const kind = isGroundPair(point) ? "ground" : "stack";
  const title = `${pairKey(point)} 点${point.point}`;
  const biasLine = point.s > 0
    ? `s &gt; 0，b = s / h = ${n(point.s)} / h = ${n(point.bias)}`
    : relax
      ? `s ≤ 0 且 Relax 不用弹簧，b = 0，massScale = 1，impulseScale = 0。记录值 b = ${n(point.bias)}`
      : `s ≤ 0，b = max(massScale · biasRate · s, −pushSpeed) = ${n(point.bias)}`;
  const deltaExpr = `−${n(point.normalMass)} × (${n(point.massScale)} × ${n(point.vn)} + ${n(point.bias)}) − ${n(point.impulseScale)} × ${n(point.nBefore)}`;
  let body = `
    <p class="sym">s = s0 + (ΔpB − ΔpA) · n</p>
    <p class="plug">本点 s = ${n(point.s)} m</p>
    <p class="sym">vn = (vB + ωB × rB − vA − ωA × rA) · n</p>
    <p class="plug">打冲量前 vn = ${n(point.vn)} m/s</p>
    <p class="sym">b = s &gt; 0 ? s/h : max(massScale · biasRate · s, −vpush)</p>
    <p class="plug">${biasLine}</p>
    <p class="sym">Δλn = −normalMass (massScale · vn + b) − impulseScale · λn</p>
    <p class="plug">= ${deltaExpr}</p>
    <p class="plug">= ${n(point.nDelta)}</p>
    <p class="sym">λn ← max(λn + Δλn, 0)</p>
    <p class="plug">${n(point.nBefore)} + ${n(point.nDelta)} → ${n(point.nAfter)}</p>`;
  if (relax) {
    body += `
      <p class="sym">Δλt = tangentMass (−vt)，再夹到 ±μ λn</p>
      <p class="plug">vt = ${n(point.vt)}，Δλt = ${n(point.tDelta)}，摩擦锥 ±${n(point.frictionLimit)}</p>
      <p class="plug">λt：${n(point.tBefore)} → ${n(point.tAfter)}</p>`;
  }
  return `<article class="card ${kind}"><h3>${title}</h3>${body}</article>`;
}

function formulaHtml(frame) {
  const header = trace.header;
  const h = header.h;
  if (frame.phase === PHASE_PREPARE) {
    const dynamic = softnessTerms(header.contactHertz, header.damping, h);
    const staticSoft = softnessTerms(header.contactHertz * 2, header.damping, h);
    return `<p class="note">h = ${n(h)} s，频率 ${n(header.contactHertz)} Hz，阻尼 ${n(header.damping)}。地面接触的频率再乘 2。</p>
      <div class="soft-row">
        ${formulaCard("A–B 动态软度", "stack", [
          ["ω", n(dynamic.omega)],
          ["a1", n(dynamic.a1)],
          ["a2", n(dynamic.a2)],
          ["a3", n(dynamic.a3)],
          ["biasRate", n(header.contactBias)],
          ["massScale", n(header.contactMass)],
          ["impulseScale", n(header.contactImpulse)],
        ])}
        ${formulaCard("地面 静态软度 ×2", "ground", [
          ["ω", n(staticSoft.omega)],
          ["a1", n(staticSoft.a1)],
          ["a2", n(staticSoft.a2)],
          ["a3", n(staticSoft.a3)],
          ["biasRate", n(header.staticBias)],
          ["massScale", n(header.staticMass)],
          ["impulseScale", n(header.staticImpulse)],
        ])}
      </div>
      ${prepareDerivation(header)}`;
  }

  if (frame.phase === PHASE_VELOCITY) {
    const gy = -10 * h;
    const cards = frame.bodies
      .filter((body) => body.invMass > 0)
      .map((body) => formulaCard(nameOf(body.id), "stack", [
        ["h·g", `(0, ${n(gy)})`],
        ["积分后 v", vec(body.vx, body.vy)],
      ]))
      .join("");
    const plugs = frame.bodies
      .filter((body) => body.invMass > 0)
      .map((body) => `<p class="plug">${nameOf(body.id)}：(${n(body.vx)}, ${n(body.vy - gy)}) + (0, ${n(gy)}) = ${vec(body.vx, body.vy)}</p>`)
      .join("");
    return `<div class="points">${cards}</div>
      ${deriveBlock("速度积分", `
        <p class="sym">v ← v / (1 + c h) + h (F/m + g)</p>
        <p class="plug">本场景 c = 0，F = 0，g = (0, −10)</p>
        <p class="sym">v ← v + h g</p>
        ${plugs}`)}`;
  }

  if (frame.phase === PHASE_WARM) {
    if (frame.points.length === 0) {
      return "<p class='note'>这一子步没有接触点。</p>";
    }
    const cards = frame.points
      .map((point) =>
        formulaCard(`${pairKey(point)} 点${point.point}`, isGroundPair(point) ? "ground" : "stack", [
          ["λn", n(point.nAfter)],
          ["λt", n(point.tAfter)],
          ["vn", n(point.vn)],
          ["s", n(point.s)],
          ["打到 B", vec(point.pbx, point.pby)],
        ])
      )
      .join("");
    const plugs = frame.points
      .map((point) => `<p class="plug">${pairKey(point)} 点${point.point}：${n(point.nAfter)} ${vec(point.nx, point.ny)} + ${n(point.tAfter)} ${vec(point.tx, point.ty)} = ${vec(point.pbx, point.pby)}，打到 A 的是相反数 ${vec(point.pax, point.pay)}</p>`)
      .join("");
    return `<div class="points">${cards}</div>
      ${deriveBlock("热启动不重新求 λ，只把旧冲量打进速度", `
        <p class="sym">P = λn n + λt t</p>
        <p class="sym">vA ← vA − P / mA，vB ← vB + P / mB</p>
        ${plugs}`)}`;
  }

  if (frame.phase === PHASE_SOLVE || frame.phase === PHASE_RELAX) {
    const relax = frame.phase === PHASE_RELAX;
    const cards = frame.points
      .map((point) => {
        const rows = [
          ["s", n(point.s)],
          ["vn", n(point.vn)],
          ["b", n(point.bias)],
          ["massScale", n(point.massScale)],
          ["impulseScale", n(point.impulseScale)],
          ["normalMass", n(point.normalMass)],
          ["λn", `${n(point.nBefore)} → ${n(point.nAfter)}`],
          ["Δλn", n(point.nDelta)],
        ];
        if (relax) {
          rows.push(["vt", n(point.vt)], ["Δλt", n(point.tDelta)], ["摩擦锥", `±${n(point.frictionLimit)}`]);
        }
        return formulaCard(`${pairKey(point)} 点${point.point}`, isGroundPair(point) ? "ground" : "stack", rows);
      })
      .join("");
    return `<div class="points">${cards}</div>
      ${deriveBlock(relax ? "Relax：先收回法向多推的速度，再按摩擦锥改切向" : "软约束：由当前 vn 和穿透算出这一拍的法向增量", `<div class="points">${frame.points.map((point) => pointDerivation(point, relax)).join("")}</div>`)}`;
  }

  if (frame.phase === PHASE_POSITION) {
    const cards = frame.bodies
      .filter((body) => body.invMass > 0)
      .map((body) =>
        formulaCard(nameOf(body.id), "stack", [
          ["Δp", vec(body.dx, body.dy)],
          ["h v", vec(header.h * body.vx, header.h * body.vy)],
        ])
      )
      .join("");
    const plugs = frame.bodies
      .filter((body) => body.invMass > 0)
      .map((body) => `<p class="plug">${nameOf(body.id)}：Δp ← Δp + ${n(header.h)} × ${vec(body.vx, body.vy)}，现在 Δp = ${vec(body.dx, body.dy)}</p>`)
      .join("");
    return `<div class="points">${cards}</div>
      ${deriveBlock("位置积分只累加位移，质心要到提交帧才写回", `
        <p class="sym">Δp ← Δp + h v</p>
        <p class="sym">Δq ← integrate(Δq, h ω)</p>
        ${plugs}`)}`;
  }

  const cards = frame.bodies
    .map((body) =>
      formulaCard(nameOf(body.id), "stack", [
        ["质心", vec(body.x, body.y)],
        ["Δp", vec(body.dx, body.dy)],
        ["v", vec(body.vx, body.vy)],
      ])
    )
    .join("");
  return `<div class="points">${cards}</div>
    ${deriveBlock("提交", `
      <p class="sym">center ← center + Δp</p>
      <p class="sym">Δp ← 0，并把 λn、λt 存回接触，留给下一步热启动</p>`)}`;
}

function renderProgress() {
  const frame = currentFrame();
  if (!frame) {
    progressEl.textContent = "尚未步进";
    return;
  }
  const sub = frame.subStep < 0 ? "—" : `${frame.subStep + 1}/4`;
  progressEl.textContent = `大步 ${bigStep} · 子步 ${sub} · ${PHASE_NAME[frame.phase] || frame.phase} · 帧 ${frameIndex + 1}/${trace.frames.length}`;
}

function render() {
  draw();
  renderState();
  renderProgress();
}

async function stepWorld() {
  moduleApi.step();
  await loadTrace();
  bigStep += 1;
}

async function onNext() {
  if (!trace || frameIndex + 1 >= trace.frames.length) {
    await stepWorld();
    frameIndex = 0;
  } else {
    frameIndex += 1;
  }
  render();
}

function onSubstep() {
  const frame = currentFrame();
  if (!frame) {
    return;
  }
  if (frame.phase === PHASE_PREPARE) {
    const relax = trace.frames.findIndex((item) => item.phase === PHASE_RELAX && item.subStep === 0);
    if (relax >= 0) {
      frameIndex = relax;
    }
  } else if (frame.subStep >= 0) {
    for (let i = frameIndex; i < trace.frames.length; i += 1) {
      if (trace.frames[i].phase === PHASE_RELAX && trace.frames[i].subStep === frame.subStep) {
        frameIndex = i;
        break;
      }
    }
  }
  render();
}

async function onBig() {
  if (trace && frameIndex >= 0 && frameIndex < trace.frames.length - 1) {
    frameIndex = trace.frames.length - 1;
    render();
    return;
  }
  await stepWorld();
  frameIndex = trace.frames.length - 1;
  render();
}

async function onReset() {
  moduleApi.reset();
  await loadTrace();
  frameIndex = -1;
  bigStep = 0;
  render();
}

async function boot() {
  if (typeof ContactTrace !== "function") {
    progressEl.textContent = "没有找到 contact_trace.js。请先用 Emscripten 编译 demo。";
    return;
  }

  const wasm = await ContactTrace();
  moduleApi = {
    module: wasm,
    reset: wasm.cwrap("demo_reset", null, []),
    step: wasm.cwrap("demo_step", "number", []),
    json: wasm.cwrap("demo_trace_json", "number", []),
  };
  moduleApi.reset();
  await loadTrace();
  document.getElementById("next").addEventListener("click", () => {
    onNext().catch((error) => {
      progressEl.textContent = String(error);
    });
  });
  document.getElementById("substep").addEventListener("click", onSubstep);
  document.getElementById("big").addEventListener("click", () => {
    onBig().catch((error) => {
      progressEl.textContent = String(error);
    });
  });
  document.getElementById("reset").addEventListener("click", () => {
    onReset().catch((error) => {
      progressEl.textContent = String(error);
    });
  });
  render();
}

boot().catch((error) => {
  progressEl.textContent = String(error);
});
