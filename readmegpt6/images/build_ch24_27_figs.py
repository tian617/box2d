# -*- coding: utf-8 -*-
"""SVG figures for chapters 24-27 (warm start, soft solve, position, relax)."""
from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parent
FONT = '"Segoe UI","Microsoft YaHei","Noto Sans SC",sans-serif'
MONO = '"Consolas","Cascadia Mono","Microsoft YaHei",monospace'
COLORS = {
    "ink": "#1f2937", "n": "#1d4ed8", "v": "#047857",
    "o": "#c2410c", "p": "#7c3aed", "r": "#b91c1c", "g": "#6b7280",
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
      .hot {{ font: 700 12px {FONT}; fill:#c2410c; }}
      .ok {{ font: 700 12px {FONT}; fill:#047857; }}
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


def LN(x1, y1, x2, y2, color="#9ca3af", sw=1, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{sw}"{d}/>'


def A(x1, y1, x2, y2, m="ink", sw=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{COLORS[m]}" '
            f'stroke-width="{sw}"{d} marker-end="url(#ah-{m})"/>')


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


def stage_strip(hot_index, caption):
    b = []
    b.append(T(480, 28, caption, "title", "middle"))
    b.append(T(480, 50, "子步里五件事按固定顺序各做一遍。橙色是本章。", "sub", "middle"))
    b.append(R(12, 100, 86, 112, "#f3f4f6", "#9ca3af"))
    b.append(T(55, 140, "准备", "lab", "middle"))
    b.append(T(55, 162, "循环之前", "small", "middle"))
    b.append(T(55, 182, "只做 1 次", "small", "middle"))
    b.append(R(108, 72, 714, 214, "#ffffff", "#6b7280", rx=10, dash="6 4"))
    b.append(T(465, 94, "子步循环内。N = 4 时，这五件事整体重复 4 轮", "lab", "middle"))
    boxes = [
        ("① 速度积分", "外力 重力 阻尼"),
        ("② 热启动", "重放旧冲量"),
        ("③ 求解", "软约束 法向"),
        ("④ 位置积分", "累加位移转角"),
        ("⑤ Relax", "摩擦 反弹"),
    ]
    xs = [120, 260, 400, 540, 680]
    for i, ((title, line), x) in enumerate(zip(boxes, xs)):
        if i == hot_index:
            b.append(R(x, 112, 130, 100, "#fed7aa", "#c2410c", sw=3))
        else:
            b.append(R(x, 112, 130, 100, "#f8fafc", "#9ca3af"))
        b.append(T(x + 65, 150, title, "lab", "middle"))
        b.append(T(x + 65, 178, line, "small", "middle"))
    for x in xs[:-1]:
        b.append(A(x + 130, 162, x + 140, 162, "ink", 2))
    b.append(R(834, 100, 114, 112, "#f3f4f6", "#9ca3af"))
    b.append(T(891, 136, "收尾", "lab", "middle"))
    b.append(T(891, 160, "存冲量", "small", "middle"))
    b.append(T(891, 180, "写回位置", "small", "middle"))
    b.append(T(891, 200, "清空力", "small", "middle"))
    return b


def fig24_01():
    b = stage_strip(1, "图 24-1　热启动在一个子步里的位置")
    b.append(T(480, 312, "速度积分刚把重力加进速度。热启动立刻把上一子步的支撑冲量打回去。", "note", "middle"))
    svg("fig-24-01-substep-position.svg", 960, 330, "热启动位置", "热启动是子步第二步。", "\n  ".join(b))


def fig24_02():
    b = []
    b.append(T(480, 28, "图 24-2　一份旧冲量同时推开两个刚体", "title", "middle"))
    b.append(T(480, 50, "法线从 A 指向 B。正的法向冲量把 B 沿法线推，把 A 沿反方向推。", "sub", "middle"))
    b.append(R(70, 110, 200, 120, "#e5e7eb", "#6b7280"))
    b.append(T(170, 160, "A  地面", "lab", "middle"))
    b.append(T(170, 186, "静态：1/m = 0", "small", "middle"))
    b.append(T(170, 208, "速度不变", "small", "middle"))
    b.append(R(390, 90, 160, 110, "#dbeafe", "#1d4ed8", sw=2))
    b.append(T(470, 140, "B  箱子", "lab", "middle"))
    b.append(T(470, 166, "m = 2 kg", "small", "middle"))
    b.append(T(470, 188, "v 沿法线增加", "ok", "middle"))
    b.append(A(270, 170, 385, 145, "o", 3))
    b.append(T(300, 140, "P = λ n", "hot"))
    b.append(T(80, 280, "λ 是上一子步留下的法向冲量，这一步不重新计算它的大小。", "note"))
    b.append(T(80, 304, "切向冲量同样重放：P 里还有 λt · t。滚动阻力只改角速度。", "note"))
    svg("fig-24-02-impulse-pair.svg", 960, 340, "热启动冲量", "旧冲量沿法线作用在一对刚体上。", "\n  ".join(b))


def fig24_03():
    b = []
    b.append(T(480, 28, "图 24-3　静放在地上的箱子：重力刚加速，热启动把它抵消", "title", "middle"))
    b.append(T(480, 50, "数字：m = 2 kg，g = −10，h = 1/240 s，缓存 λ = 1/12 N·s。", "sub", "middle"))
    rows = [
        (90, "速度积分之后", "vy = −0.0417 m/s", "#fee2e2", "#b91c1c"),
        (330, "热启动打回 λ", "Δvy = +0.0417 m/s", "#ffedd5", "#c2410c"),
        (570, "热启动之后", "vy = 0", "#dcfce7", "#047857"),
    ]
    for x, title, line, fill, stroke in rows:
        b.append(R(x, 100, 210, 90, fill, stroke, sw=2))
        b.append(T(x + 105, 138, title, "lab", "middle"))
        b.append(T(x + 105, 166, line, "eq", "middle"))
    b.append(A(300, 145, 325, 145, "ink", 2))
    b.append(A(540, 145, 565, 145, "ink", 2))
    b.append(T(80, 240, "若没有热启动，求解器得从 0 开始把这 0.0417 重新找出来。", "note"))
    b.append(T(80, 264, "接触还在时，上一子步的答案几乎就是这一子步的答案。", "note"))
    svg("fig-24-03-cancel-gravity.svg", 960, 300, "热启动抵消重力", "静接触上热启动抵消本子步重力。", "\n  ".join(b))


def fig25_01():
    b = stage_strip(2, "图 25-1　软约束求解在一个子步里的位置")
    b.append(T(480, 312, "这一步只补法向冲量。摩擦、反弹、滚动阻力留到第 ⑤ 步。", "note", "middle"))
    svg("fig-25-01-substep-position.svg", 960, 330, "求解位置", "软约束求解是子步第三步。", "\n  ".join(b))


def fig25_02():
    b = []
    b.append(T(480, 28, "图 25-2　间隙 s 的两种处理", "title", "middle"))
    b.append(T(480, 50, "s > 0 是还没碰上；s < 0 是已经陷进去。法线从地面指向箱子。", "sub", "middle"))
    b.append(R(40, 90, 420, 180, "#f8fafc", "#1d4ed8"))
    b.append(T(250, 118, "还没碰上   s > 0", "lab", "middle"))
    b.append(R(150, 150, 140, 40, "#dbeafe", "#1d4ed8"))
    b.append(T(220, 176, "箱子", "small", "middle"))
    b.append(R(80, 220, 280, 18, "#e5e7eb", "#6b7280", rx=2))
    b.append(T(250, 256, "目标：接近速度不要超过 s/h", "note", "middle"))
    b.append(R(500, 90, 420, 180, "#fff7ed", "#c2410c"))
    b.append(T(710, 118, "已经重叠   s < 0", "lab", "middle"))
    b.append(R(610, 190, 140, 40, "#fed7aa", "#c2410c"))
    b.append(T(680, 216, "箱子", "small", "middle"))
    b.append(R(540, 214, 280, 18, "#e5e7eb", "#6b7280", rx=2))
    b.append(T(710, 256, "目标：用软弹簧慢慢推开", "note", "middle"))
    svg("fig-25-02-separation.svg", 960, 300, "间隙两种情况", "正间隙用推测，负间隙用软约束。", "\n  ".join(b))


def fig25_03():
    b = []
    b.append(T(480, 28, "图 25-3　一次法向冲量增量怎么出来", "title", "middle"))
    steps = [
        (30, "1. 算现在的间隙 s"),
        (250, "2. 由 s 得到速度目标"),
        (500, "3. 看接触点还差多少速度"),
        (30, "4. 乘有效质量，得到增量"),
        (250, "5. 累加后不许小于 0"),
        (500, "6. 只把增量打进两边速度"),
    ]
    for i, (x, text) in enumerate(steps):
        y = 80 if i < 3 else 180
        b.append(R(x, y, 200, 70, "#fff7ed" if i == 4 else "#f8fafc", "#c2410c" if i == 4 else "#9ca3af", sw=2))
        b.append(T(x + 100, y + 42, text, "small", "middle"))
    b.append(T(480, 290, "单边约束：接触只能推、不能拉。累加冲量一旦要变成负数，就停在 0。", "note", "middle"))
    svg("fig-25-03-impulse-steps.svg", 960, 320, "法向增量步骤", "软约束求解的六步。", "\n  ".join(b))


def fig26_01():
    b = stage_strip(3, "图 26-1　位置积分在一个子步里的位置")
    b.append(T(480, 312, "用的是求解之后的速度。写的是本大步累计位移，不是世界坐标本身。", "note", "middle"))
    svg("fig-26-01-substep-position.svg", 960, 330, "位置积分位置", "位置积分是子步第四步。", "\n  ".join(b))


def fig26_02():
    b = []
    b.append(T(480, 28, "图 26-2　一个刚体上的三步，顺序不能换", "title", "middle"))
    items = [
        (40, "① 锁住的轴", "被锁的 vx、vy 或 ω 先写成 0", "#ede9fe", "#7c3aed"),
        (340, "② 速度封顶", "线速度默认不超过 400 m/s", "#fee2e2", "#b91c1c"),
        (640, "③ 走一小步", "Δp += h v，转角同样累加", "#dcfce7", "#047857"),
    ]
    for x, title, line, fill, stroke in items:
        b.append(R(x, 90, 270, 110, fill, stroke, sw=2))
        b.append(T(x + 135, 132, title, "lab", "middle"))
        b.append(T(x + 135, 164, line, "small", "middle"))
    b.append(A(310, 145, 335, 145, "ink", 2))
    b.append(A(610, 145, 635, 145, "ink", 2))
    b.append(T(80, 250, "先封顶再走路，超速的那一截不会进入位移。", "note"))
    b.append(T(80, 274, "世界变换要等全部子步结束，在收尾里一次性写回。", "note"))
    svg("fig-26-02-order.svg", 960, 310, "位置积分顺序", "锁定、封顶、再积分。", "\n  ".join(b))


def fig26_03():
    b = []
    b.append(T(480, 28, "图 26-3　位移增量跨子步累加，世界坐标先不动", "title", "middle"))
    b.append(T(120, 80, "大步开始", "lab", "middle"))
    b.append(R(70, 100, 100, 36, "#f3f4f6", "#6b7280"))
    b.append(T(120, 124, "Δp = 0", "eq", "middle"))
    xs = [230, 400, 570, 740]
    for i, x in enumerate(xs, start=1):
        b.append(R(x, 90, 120, 56, "#dbeafe", "#1d4ed8"))
        b.append(T(x + 60, 114, f"子步 {i}", "lab", "middle"))
        b.append(T(x + 60, 136, "Δp += h v", "eq", "middle"))
    for x in [170, 350, 520, 690]:
        b.append(A(x, 118, x + 55, 118, "n", 2))
    b.append(R(300, 200, 360, 70, "#fef3c7", "#c2410c", sw=2))
    b.append(T(480, 230, "收尾才做一次", "lab", "middle"))
    b.append(T(480, 254, "质心 += 最终的 Δp，朝向乘上累计转动", "small", "middle"))
    svg("fig-26-03-accumulate.svg", 960, 300, "位移累加", "子步只累加增量。", "\n  ".join(b))


def fig27_01():
    b = stage_strip(4, "图 27-1　Relax 在一个子步里的位置")
    b.append(T(480, 312, "位置已经按新速度走完。Relax 不再用“陷进去了就推”的那一项。", "note", "middle"))
    svg("fig-27-01-substep-position.svg", 960, 330, "Relax 位置", "Relax 是子步第五步。", "\n  ".join(b))


def fig27_02():
    b = []
    b.append(T(480, 28, "图 27-2　同一次接触，求解和 Relax 各管一块", "title", "middle"))
    b.append(R(40, 80, 420, 200, "#fff7ed", "#c2410c", sw=2))
    b.append(T(250, 110, "③ 求解   useBias = true", "lab", "middle"))
    for i, line in enumerate(["法向软约束（重叠时）", "推测接触（还有间隙时）", "单边：冲量 ≥ 0", "不做摩擦、不做反弹"]):
        b.append(T(70, 150 + i * 28, line, "small"))
    b.append(R(500, 80, 420, 200, "#ecfdf5", "#047857", sw=2))
    b.append(T(710, 110, "⑤ Relax   useBias = false", "lab", "middle"))
    for i, line in enumerate(["重叠修正这一项关掉", "法向再修一次速度", "库仑摩擦、滚动阻力", "恢复系数（反弹）"]):
        b.append(T(530, 150 + i * 28, line, "small"))
    svg("fig-27-02-split.svg", 960, 320, "求解与 Relax 分工", "两阶段共用求解器，开关不同。", "\n  ".join(b))


def fig27_03():
    b = []
    b.append(T(480, 28, "图 27-3　摩擦冲量被法向冲量卡住", "title", "middle"))
    b.append(A(180, 250, 180, 80, "n", 3))
    b.append(T(192, 100, "法向 λn", "lab"))
    b.append(A(180, 250, 420, 250, "o", 3))
    b.append(T(250, 236, "切向 λt", "lab"))
    b.append(LN(180, 250, 80, 140, "#b91c1c", 2, "6 4"))
    b.append(LN(180, 250, 280, 140, "#b91c1c", 2, "6 4"))
    b.append(T(70, 128, "上限 +μ λn", "hot"))
    b.append(T(290, 128, "下限 −μ λn", "hot"))
    b.append(T(500, 120, "想要的切向冲量如果落在两条虚线之间，", "note"))
    b.append(T(500, 148, "接触点的滑动速度会被尽量消掉。", "note"))
    b.append(T(500, 190, "超出虚线就停在边界上：开始打滑。", "note"))
    b.append(T(500, 232, "μ 是摩擦系数，λn 是此刻的法向冲量。", "note"))
    svg("fig-27-03-friction.svg", 960, 300, "摩擦锥", "切向冲量被摩擦系数和法向冲量限制。", "\n  ".join(b))


def main():
    fig24_01()
    fig24_02()
    fig24_03()
    fig25_01()
    fig25_02()
    fig25_03()
    fig26_01()
    fig26_02()
    fig26_03()
    fig27_01()
    fig27_02()
    fig27_03()


if __name__ == "__main__":
    main()
