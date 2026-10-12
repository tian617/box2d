# -*- coding: utf-8 -*-
"""Generate SVG figures for chapter 23 (sub-step velocity integration)."""
import math
from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parent

FONT = '"Segoe UI","Microsoft YaHei","Noto Sans SC",sans-serif'
MONO = '"Consolas","Cascadia Mono","Microsoft YaHei",monospace'

COLORS = {
    "ink": "#1f2937",
    "n": "#1d4ed8",
    "v": "#047857",
    "o": "#c2410c",
    "p": "#7c3aed",
    "r": "#b91c1c",
    "g": "#6b7280",
}

STYLE = f"""
  <defs>
    {''.join(f'<marker id="ah-{k}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 10 5 0 10z" fill="{c}"/></marker>' for k, c in COLORS.items())}
    <style>
      .title {{ font: 700 16px {FONT}; fill:#111827; }}
      .sub {{ font: 12px {FONT}; fill:#4b5563; }}
      .lab {{ font: 700 13px {FONT}; fill:#111827; }}
      .small {{ font: 12px {FONT}; fill:#374151; }}
      .note {{ font: 12px {FONT}; fill:#1f2937; }}
      .eq {{ font: 12px {MONO}; fill:#1f2937; }}
      .eqb {{ font: 700 13px {MONO}; fill:#111827; }}
      .ok {{ font: 700 12px {FONT}; fill:#047857; }}
      .bad {{ font: 700 12px {FONT}; fill:#b91c1c; }}
      .hot {{ font: 700 12px {FONT}; fill:#c2410c; }}
    </style>
  </defs>
"""


def esc(s):
    return escape(s, quote=False)


def T(x, y, s, cls="small", anchor="start"):
    return f'<text x="{x}" y="{y}" class="{cls}" text-anchor="{anchor}">{esc(s)}</text>'


def R(x, y, w, h, fill="#f8fafc", stroke="#d1d5db", rx=8, sw=1.5, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>'


def A(x1, y1, x2, y2, m="ink", sw=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{COLORS[m]}" '
            f'stroke-width="{sw}"{d} marker-end="url(#ah-{m})"/>')


def LN(x1, y1, x2, y2, color="#9ca3af", sw=1, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{sw}"{d}/>'


def svg(name, w, h, title, desc, body):
    text = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img">
  <title>{esc(title)}</title>
  <desc>{esc(desc)}</desc>
{STYLE}
  <rect width="{w}" height="{h}" fill="#ffffff"/>
  {body}
</svg>
"""
    (OUT / name).write_text(text, encoding="utf-8")
    print("wrote", name)


# ---------------------------------------------------------------- fig 23-01
def fig01():
    b = []
    b.append(T(480, 28, "图 23-1　速度积分在一个子步里的位置", "title", "middle"))
    b.append(T(480, 50, "子步里的五件事按固定顺序各做一遍；本章只讲第 ① 件。", "sub", "middle"))

    b.append(R(12, 100, 86, 112, "#f3f4f6", "#9ca3af"))
    b.append(T(55, 136, "准备", "lab", "middle"))
    b.append(T(55, 158, "子步循环之前", "small", "middle"))
    b.append(T(55, 178, "只做 1 次", "small", "middle"))

    b.append(R(108, 72, 714, 214, "#ffffff", "#6b7280", rx=10, dash="6 4"))
    b.append(T(465, 94, "子步循环：N = 4 时，下面五件事整体重复 4 轮", "lab", "middle"))

    boxes = [
        ("① 速度积分", "外力 重力 阻尼", "只改 v 和 ω", True),
        ("② 热启动", "上一步的冲量", "先打进速度", False),
        ("③ 求解", "带偏置解约束", "改 v 和 ω", False),
        ("④ 位置积分", "用新速度走位置", "推进 p 和朝向", False),
        ("⑤ 松弛", "关偏置再解一遍", "摩擦恢复在此", False),
    ]
    xs = [120, 260, 400, 540, 680]
    for (t, l1, l2, hot), x in zip(boxes, xs):
        if hot:
            b.append(R(x, 112, 130, 112, "#fed7aa", "#c2410c", sw=3))
        else:
            b.append(R(x, 112, 130, 112, "#f8fafc", "#9ca3af"))
        b.append(T(x + 65, 142, t, "lab", "middle"))
        b.append(T(x + 65, 170, l1, "small", "middle"))
        b.append(T(x + 65, 192, l2, "small", "middle"))
    for x in xs[:-1]:
        b.append(A(x + 130, 168, x + 140, 168, "ink", 2))

    b.append(A(185, 260, 185, 228, "o", 2.5))
    b.append(T(198, 254, "本章主角：只读 F、τ、阻尼、g，只写 v、ω", "hot"))

    b.append(R(834, 100, 114, 112, "#f3f4f6", "#9ca3af"))
    b.append(T(891, 130, "收尾", "lab", "middle"))
    b.append(T(891, 154, "存冲量", "small", "middle"))
    b.append(T(891, 174, "位置写回刚体", "small", "middle"))
    b.append(T(891, 194, "清空力和力矩", "small", "middle"))
    b.append(T(891, 232, "全部子步之后", "small", "middle"))

    b.append(T(480, 312, "② ③ ⑤ 在解约束；① ④ 在推进时间。约束扫几遍和子步走几轮是两回事。", "note", "middle"))
    svg("fig-23-01-substep-position.svg", 960, 330,
        "速度积分在子步中的位置", "子步内顺序：速度积分、热启动、求解、位置积分、松弛。", "\n  ".join(b))


# ---------------------------------------------------------------- fig 23-02
def fig02():
    b = []
    b.append(T(440, 28, "图 23-2　速度积分读什么、写什么、不碰什么", "title", "middle"))
    b.append(T(440, 50, "输入来自三处，输出只有两个数：新的线速度 v 和角速度 ω。", "sub", "middle"))

    # left: b2BodyState
    b.append(R(16, 70, 262, 96, "#dbeafe", "#1d4ed8"))
    b.append(T(28, 92, "b2BodyState（每个醒着的刚体一份）", "lab"))
    b.append(T(28, 118, "linearVelocity", "eq")); b.append(T(176, 118, "v", "eqb")); b.append(T(214, 118, "m/s", "small"))
    b.append(T(28, 142, "angularVelocity", "eq")); b.append(T(176, 142, "ω", "eqb")); b.append(T(214, 142, "rad/s", "small"))

    # left: b2BodySim
    b.append(R(16, 180, 262, 202, "#ede9fe", "#7c3aed"))
    b.append(T(28, 202, "b2BodySim（每个醒着的刚体一份）", "lab"))
    rows = [
        ("force", "F", "N"),
        ("torque", "τ", "N·m"),
        ("invMass", "1/m", "1/kg"),
        ("invInertia", "1/I", "1/(kg·m²)"),
        ("linearDamping", "c_v", "1/s"),
        ("angularDamping", "c_ω", "1/s"),
        ("gravityScale", "g_s", "无量纲"),
    ]
    y = 228
    for n, s, u in rows:
        b.append(T(28, y, n, "eq")); b.append(T(160, y, s, "eqb")); b.append(T(196, y, u, "small"))
        y += 22

    # left: world
    b.append(R(16, 396, 262, 70, "#fef9c3", "#a16207"))
    b.append(T(28, 418, "世界与步进参数", "lab"))
    b.append(T(28, 438, "gravity  g = (0, −10) m/s²（默认）", "eq"))
    b.append(T(28, 456, "h = Δt / N（子步时长，秒）", "eq"))

    # center
    b.append(R(306, 100, 306, 300, "#ffffff", "#c2410c", sw=3))
    b.append(T(459, 128, "b2IntegrateVelocitiesTask", "lab", "middle"))
    b.append(T(459, 148, "每个刚体各算一次，彼此不依赖", "small", "middle"))
    b.append(T(326, 190, "线速度", "hot"))
    b.append(T(326, 214, "v ←  v / (1 + h·c_v)", "eqb"))
    b.append(T(352, 238, "+ h·(1/m)·F", "eqb"))
    b.append(T(352, 262, "+ h·g_s·g", "eqb"))
    b.append(T(326, 306, "角速度", "hot"))
    b.append(T(326, 330, "ω ←  ω / (1 + h·c_ω)", "eqb"))
    b.append(T(352, 354, "+ h·(1/I)·τ", "eqb"))
    b.append(T(459, 388, "源码：src/solver.c  第 66–112 行", "small", "middle"))

    b.append(A(278, 118, 306, 190, "ink"))
    b.append(A(278, 290, 306, 290, "ink"))
    b.append(A(278, 430, 306, 350, "ink"))

    # right
    b.append(R(640, 100, 224, 112, "#d1fae5", "#047857", sw=2.5))
    b.append(T(652, 124, "写回 b2BodyState", "lab"))
    b.append(T(652, 150, "linearVelocity ← 新 v", "eq"))
    b.append(T(652, 172, "angularVelocity ← 新 ω", "eq"))
    b.append(T(652, 196, "只有这两个字段被改写", "ok"))
    b.append(A(612, 156, 640, 156, "v", 2.5))

    b.append(R(640, 236, 224, 230, "#fef2f2", "#b91c1c"))
    b.append(T(652, 260, "这一步不碰", "lab"))
    for i, s in enumerate([
        "位置 deltaPosition",
        "朝向 deltaRotation",
        "力和力矩的清零（大步末）",
        "速度上限钳制（位置积分里）",
        "运动锁定（位置积分里）",
        "休眠判断（大步末）",
    ]):
        b.append(T(652, 286 + i * 26, s, "small"))
    svg("fig-23-02-data-flow.svg", 880, 486,
        "速度积分的数据流", "输入：状态速度、力、力矩、逆质量、阻尼、重力缩放、重力、h；输出：新速度。",
        "\n  ".join(b))


# ---------------------------------------------------------------- fig 23-03
def fig03():
    b = []
    b.append(T(440, 28, "图 23-3　对一个刚体的处理顺序（共 7 步，循环体对每个醒着的刚体各执行一次）", "title", "middle"))
    b.append(T(440, 50, "橙色那一步是全部计算的汇合点：旧速度先缩，再加增量。", "sub", "middle"))
    steps = [
        ("读出旧速度", "把 v 和 ω 取到局部变量", "v, w ← linearVelocity, angularVelocity", "第 83–84 行"),
        ("算阻尼缩放比", "两次除法，结果在 0 到 1 之间", "kv = 1/(1+h·c_v)；  kw = 1/(1+h·c_ω)", "第 94–95 行"),
        ("决定吃不吃重力", "invMass 为 0 的刚体不受重力", "gs = (invMass>0) ? gravityScale : 0", "第 98 行"),
        ("线速度增量", "外力项加重力项，不含阻尼", "Δv = h·invMass·F + h·gs·g", "第 101 行"),
        ("角速度增量", "只有力矩项，没有重力项", "Δω = h·invInertia·τ", "第 102 行"),
        ("合成新速度", "旧速度先缩小，再加增量", "v = kv·v + Δv；  w = kw·w + Δω", "第 104–105 行"),
        ("写回状态", "只写速度，不写位置", "linearVelocity = v；  angularVelocity = w", "第 107–108 行"),
    ]
    y0 = 70
    for i, (t, d, f, ln) in enumerate(steps):
        y = y0 + i * 68
        hot = i == 5
        b.append(R(64, y, 300, 54, "#fed7aa" if hot else "#f8fafc", "#c2410c" if hot else "#9ca3af", sw=2.5 if hot else 1.5))
        b.append(R(380, y, 484, 54, "#ffffff", "#c2410c" if hot else "#d1d5db", sw=2.5 if hot else 1.2))
        cy = y + 27
        b.append(f'<circle cx="36" cy="{cy}" r="14" fill="{"#c2410c" if hot else "#1d4ed8"}"/>')
        b.append(f'<text x="36" y="{cy + 5}" text-anchor="middle" class="lab" style="fill:#ffffff">{i + 1}</text>')
        if i < len(steps) - 1:
            b.append(A(36, cy + 14, 36, cy + 68 - 14, "n", 2))
        b.append(T(78, y + 22, t, "lab"))
        b.append(T(78, y + 43, d, "small"))
        b.append(T(392, y + 22, f, "eq"))
        b.append(T(392, y + 43, "src/solver.c  " + ln, "small"))
    svg("fig-23-03-loop-order.svg", 880, 566,
        "速度积分循环体的七步顺序", "读速度、算阻尼、定重力缩放、算两个增量、合成、写回。", "\n  ".join(b))


# ---------------------------------------------------------------- fig 23-04
def fig04():
    b = []
    b.append(T(440, 28, "图 23-4　一个子步里阻尼要把速度乘多少？三种写法比较", "title", "middle"))
    b.append(T(440, 50, "横轴 z = h·c（子步时长乘阻尼系数，无量纲）；纵轴是这一步速度保留的比例。", "sub", "middle"))
    x0, y0, ppx, ppy = 70, 220, 240, 140

    def px(z):
        return x0 + z * ppx

    def py(v):
        return y0 - v * ppy

    # grid
    for z in (0.5, 1.0, 1.5, 2.0):
        b.append(LN(px(z), 80, px(z), 360, "#e5e7eb"))
        b.append(T(px(z), 380, f"{z:g}", "small", "middle"))
    for v in (1.0, 0.5, -0.5, -1.0):
        b.append(LN(x0, py(v), 550, py(v), "#e5e7eb"))
        b.append(T(60, py(v) + 4, f"{v:g}", "small", "end"))
    b.append(LN(x0, y0, 550, y0, "#6b7280", 1.5))
    b.append(LN(x0, 80, x0, 360, "#6b7280", 1.5))
    b.append(T(60, y0 + 4, "0", "small", "end"))
    b.append(T(px(1.0), 402, "z = h·c", "small", "middle"))

    def path(fn, color, dash=None, width=2.5):
        pts = []
        z = 0.0
        while z <= 2.0001:
            pts.append(f"{px(z):.1f},{py(fn(z)):.1f}")
            z += 0.02
        d = f' stroke-dasharray="{dash}"' if dash else ""
        return f'<polyline points="{" ".join(pts)}" fill="none" stroke="{color}" stroke-width="{width}"{d}/>'

    b.append(path(lambda z: 1 - z, "#b91c1c", "6 4"))
    b.append(path(lambda z: math.exp(-z), "#c2410c"))
    b.append(path(lambda z: 1 / (1 + z), "#1d4ed8"))
    b.append(LN(px(0.01), 84, px(0.01), 216, "#7c3aed", 1.5, "3 3"))
    b.append(T(86, 262, "z≈0.01 在最左端：", "hot"))
    b.append(T(86, 282, "三条线几乎重合", "hot"))

    # legend
    lx = 590
    b.append(R(lx, 76, 274, 130, "#f8fafc", "#e5e7eb"))
    b.append(LN(lx + 14, 98, lx + 54, 98, "#c2410c", 2.5))
    b.append(T(lx + 62, 102, "e^(−z)   精确解（连续物理）", "small"))
    b.append(LN(lx + 14, 128, lx + 54, 128, "#1d4ed8", 2.5))
    b.append(T(lx + 62, 132, "1/(1+z)  Box2D 实际使用", "small"))
    b.append(LN(lx + 14, 158, lx + 54, 158, "#b91c1c", 2.5, "6 4"))
    b.append(T(lx + 62, 162, "1−z      显式欧拉", "small"))
    b.append(T(lx + 14, 192, "显式写法 z>1 会翻向，z>2 会发散", "bad"))

    b.append(R(lx, 222, 274, 158, "#ffffff", "#e5e7eb"))
    b.append(T(lx + 14, 244, "数值对照", "lab"))
    b.append(T(lx + 14, 268, "z", "eqb")); b.append(T(lx + 70, 268, "1/(1+z)", "eqb")); b.append(T(lx + 170, 268, "e^(−z)", "eqb"))
    data = [(0.01, 0.990099, 0.990050), (0.1, 0.909091, 0.904837), (1.0, 0.500000, 0.367879), (2.0, 0.333333, 0.135335)]
    for i, (z, a, e) in enumerate(data):
        yy = 290 + i * 20
        b.append(T(lx + 14, yy, f"{z:g}", "eq")); b.append(T(lx + 70, yy, f"{a:.6f}", "eq")); b.append(T(lx + 170, yy, f"{e:.6f}", "eq"))
    b.append(T(lx + 14, 372, "不翻向、不放大；代价是 z 大时衰减偏弱", "small"))
    svg("fig-23-04-damping-curve.svg", 880, 420,
        "阻尼缩放比：精确解、Box2D 的 Padé 写法、显式欧拉", "三条曲线在 z 很小时重合，z 变大后分开。",
        "\n  ".join(b))


# ---------------------------------------------------------------- fig 23-05
def fig05():
    b = []
    b.append(T(440, 28, "图 23-5　一个子步里 x 方向速度的变化：先缩，再加", "title", "middle"))
    b.append(T(440, 50, "例：h = 1/240 s，c_v = 2.4 1/s，vₓ = 3 m/s，F = (4, 0) N，m = 2 kg。箭头长度为示意，放大了缩小量与增量。", "sub", "middle"))
    px0 = [16, 305, 594]
    titles = ["① 旧速度", "② 乘缩放比（阻尼）", "③ 加增量（外力）"]
    for x, t in zip(px0, titles):
        b.append(R(x, 70, 270, 236, "#f8fafc", "#e5e7eb"))
        b.append(T(x + 135, 94, t, "lab", "middle"))
    # panel1
    b.append(A(34, 170, 254, 170, "n", 3.5))
    b.append(T(151, 150, "vₓ = 3", "eqb", "middle"))
    b.append(T(151, 210, "来自上一个子步结束时", "small", "middle"))
    b.append(T(151, 232, "（或大步开始时的状态）", "small", "middle"))
    # panel2
    b.append(A(323, 170, 543, 170, "g", 2, "5 4"))
    b.append(T(433, 142, "旧：3", "small", "middle"))
    b.append(A(323, 196, 513, 196, "n", 3.5))
    b.append(T(418, 224, "kv = 1/(1+0.01) = 0.990099", "eq", "middle"))
    b.append(T(418, 246, "vₓ·kv = 2.970297", "eqb", "middle"))
    b.append(T(418, 272, "缩小了约 0.0297 m/s", "small", "middle"))
    # panel3
    b.append(A(612, 170, 792, 170, "n", 3.5))
    b.append(A(792, 170, 836, 170, "o", 3.5))
    b.append(T(702, 148, "2.970297", "small", "middle"))
    b.append(T(814, 148, "+0.008333", "hot", "middle"))
    b.append(T(727, 214, "Δvₓ = h·F/m = 4/(240·2)", "eq", "middle"))
    b.append(T(727, 236, "新 vₓ = 2.978630", "eqb", "middle"))
    b.append(T(727, 262, "y 方向同理：", "small", "middle"))
    b.append(T(727, 282, "−0.990099 − 0.041667 = −1.031766", "eq", "middle"))
    b.append(A(286, 170, 304, 170, "ink", 2))
    b.append(A(575, 170, 593, 170, "ink", 2))
    b.append(T(440, 336, "缩放比永远在 (0, 1]，只会让速度变小；增量项可正可负，不受阻尼影响。", "note", "middle"))
    svg("fig-23-05-shrink-then-add.svg", 880, 352,
        "先缩小再加增量", "旧速度乘阻尼缩放比后，再加上本子步外力和重力造成的速度增量。", "\n  ".join(b))


# ---------------------------------------------------------------- fig 23-06
def fig06():
    b = []
    b.append(T(440, 28, "图 23-6　力的生命周期：一个大步里每个子步都读同一份 F", "title", "middle"))
    b.append(T(440, 50, "力是“持续作用”：缓冲区在大步内保持不变，大步收尾才清零。", "sub", "middle"))
    b.append(R(16, 76, 232, 118, "#ede9fe", "#7c3aed"))
    b.append(T(28, 98, "大步开始前：游戏逻辑", "lab"))
    b.append(T(28, 122, "b2Body_ApplyForce(F, 作用点)", "eq"))
    b.append(T(28, 146, "force  += F", "eq"))
    b.append(T(28, 168, "torque += r × F", "eq"))
    b.append(T(28, 186, "（r 从质心指向作用点）", "small"))
    b.append(A(248, 135, 276, 135, "p", 2.5))
    xs = [280, 418, 556, 694]
    for k, x in enumerate(xs):
        b.append(R(x, 76, 130, 118, "#fff7ed", "#c2410c", sw=2))
        b.append(T(x + 65, 98, f"子步 {k + 1}", "lab", "middle"))
        b.append(T(x + 65, 124, "读 force、torque", "small", "middle"))
        b.append(T(x + 65, 146, "Δv = h·F/m", "eq", "middle"))
        b.append(T(x + 65, 168, "缓冲区不清零", "ok", "middle"))
        if k < 3:
            b.append(A(x + 130, 135, xs[k + 1], 135, "o", 2))
    b.append(T(280, 222, "4 个子步合计：Σ h·F/m = N·(Δt/N)·F/m = Δt·F/m", "eqb"))
    b.append(R(280, 248, 544, 68, "#fef2f2", "#b91c1c"))
    b.append(T(292, 272, "大步收尾 b2FinalizeBodiesTask", "lab"))
    b.append(T(292, 296, "force = 0；torque = 0  （src/solver.c 第 631–633 行）", "eq"))
    b.append(A(759, 194, 759, 248, "r", 2.5))
    b.append(R(16, 248, 248, 120, "#dbeafe", "#1d4ed8"))
    b.append(T(28, 272, "对比：冲量", "lab"))
    b.append(T(28, 296, "b2Body_ApplyLinearImpulse", "eq"))
    b.append(T(28, 318, "直接改 state 里的 v 和 ω，", "small"))
    b.append(T(28, 338, "只发生一次，不进本循环。", "small"))
    b.append(T(28, 358, "因此不能每个子步重复施加。", "small"))
    b.append(T(560, 352, "如果第一个子步后就清零：效果只剩 1/N。", "bad"))
    b.append(T(560, 372, "如果每个子步都重新累加：效果变成 N 倍。", "bad"))
    svg("fig-23-06-force-lifetime.svg", 880, 392,
        "力的生命周期", "力在大步前写入缓冲，所有子步读取同一份，大步收尾才清零。", "\n  ".join(b))


# ---------------------------------------------------------------- fig 23-07
def fig07():
    b = []
    b.append(T(440, 28, "图 23-7　为什么先积分速度，再解约束（教学示意：静止在地面上的方块）", "title", "middle"))
    b.append(T(440, 50, "h = 1/240 s，重力 g = −10 m/s²。每个子步重力把速度改 h·g = −0.0417 m/s。", "sub", "middle"))
    for (x, title, col, fillc, steps) in [
        (16, "Box2D 的顺序：先积分速度，再解约束", "#047857", "#ecfdf5", [
            ("子步开始", "方块静止在地面，v = 0"),
            ("① 速度积分", "v = 0 + h·g = −0.0417 m/s"),
            ("③ 求解", "接触冲量把 v 推回 ≈ 0"),
            ("④ 位置积分", "Δy = h·v ≈ 0，不陷入地面"),
        ]),
        (456, "反例：先解约束，再积分速度", "#b91c1c", "#fef2f2", [
            ("子步开始", "方块静止在地面，v = 0"),
            ("求解", "此刻 v = 0，没有速度可纠"),
            ("速度积分", "v = −0.0417 m/s"),
            ("位置积分", "Δy = h·v = −0.000174 m，已陷入"),
        ]),
    ]:
        b.append(R(x, 64, 408, 326, fillc, col, sw=2))
        b.append(T(x + 204, 88, title, "lab", "middle"))
        for i, (t, d) in enumerate(steps):
            y = 104 + i * 70
            b.append(R(x + 16, y, 376, 52, "#ffffff", "#9ca3af"))
            b.append(T(x + 28, y + 22, t, "lab"))
            b.append(T(x + 28, y + 42, d, "small"))
            if i < 3:
                b.append(A(x + 204, y + 52, x + 204, y + 70, "ink", 2))
    b.append(T(440, 414, "先让所有人按受力“自由走一小步”，再用约束把越界的速度纠回来；位置只用纠正过的速度去推进。", "note", "middle"))
    svg("fig-23-07-why-before-constraints.svg", 880, 432,
        "为什么先积分速度再解约束", "对比两种顺序对静止在地面上的方块的影响。", "\n  ".join(b))


if __name__ == "__main__":
    fig01(); fig02(); fig03(); fig04(); fig05(); fig06(); fig07()
