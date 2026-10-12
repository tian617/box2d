# -*- coding: utf-8 -*-
"""Generate UTF-8 SVG figures for chapter 02a. ASCII source only."""
from pathlib import Path

OUT = Path(__file__).resolve().parent

S = {
    "t1": "\u56fe 2a-1\u3000\u8d28\u91cf\u7ba1\u5e73\u52a8\uff0c\u8f6c\u52a8\u60ef\u91cf\u7ba1\u8f6c\u52a8",
    "s1": "F=ma \u4e0e \u03c4=I\u03b1 \u6210\u5bf9\u3002I \u4e0d\u662f\u7b2c\u4e8c\u4e2a\u8d28\u91cf\uff0c\u5355\u4f4d\u4e5f\u4e0d\u662f\u5343\u514b\u3002",
    "l1a": "\u5e73\u52a8\uff1a\u540c\u6837\u7684\u529b\uff0c\u8c01\u66f4\u6c89",
    "msmall": "m \u5c0f",
    "abig": "a \u5927",
    "mbig": "m \u5927",
    "asmall": "a \u5c0f",
    "l1b": "\u8f6c\u52a8\uff1a\u540c\u6837\u7684\u62e7\uff0c\u8c01\u66f4\u96be\u8f6c",
    "ialpha_s": "I \u5c0f\uff0c\u03b1 \u5927",
    "ialpha_b": "I \u5927\uff0c\u03b1 \u5c0f",
    "title1": "\u8d28\u91cf\u5bf9\u5e73\u52a8\uff0c\u8f6c\u52a8\u60ef\u91cf\u5bf9\u8f6c\u52a8",
    "desc1": "\u540c\u6837\u7684\u63a8\uff0c\u8d28\u91cf\u5927\u5219\u5e73\u52a8\u52a0\u901f\u5ea6\u5c0f\uff1b\u540c\u6837\u7684\u62e7\uff0c\u8f6c\u52a8\u60ef\u91cf\u5927\u5219\u89d2\u52a0\u901f\u5ea6\u5c0f\u3002",
    "t2": "\u56fe 2a-2\u3000\u7ed5\u8f74\u8f6c\u52a8\u65f6\uff0c\u901f\u7387\u4e0e\u8ddd\u79bb\u6210\u6b63\u6bd4\uff0c\u52a8\u80fd\u5e26\u51fa r\u00b2",
    "s2": "\u540c\u4e00 \u03c9 \u4e0b\uff0c\u79bb\u8f74\u8d8a\u8fdc\u7684\u5c0f\u5757\u8dd1\u5f97\u8d8a\u5feb\u3002\u628a \u00bdmv\u00b2 \u52a0\u8d77\u6765\uff0c\u7cfb\u6570\u5c31\u662f I\u3002",
    "l2a": "\u521a\u4f53\u7ed5\u8d28\u5fc3 C \u5300\u901f\u8f6c\u52a8",
    "note2a": "\u03c9 \u5bf9\u6574\u5757\u521a\u4f53\u76f8\u540c\uff1bv \u968f r \u53d8",
    "sub2a": "\u5207\u5411\u901f\u5ea6\uff0c\u5782\u76f4\u4e8e\u534a\u5f84",
    "l2b": "\u628a\u6240\u6709\u5c0f\u5757\u7684\u52a8\u80fd\u52a0\u8d77\u6765",
    "erot": "E\u8f6c = \u00bd I \u03c9\u00b2",
    "idef": "I = \u03a3 m\u1d62 r\u1d62\u00b2 = \u222b r\u00b2 dm",
    "unit": "\u5355\u4f4d\uff1akg\u00b7m\u00b2",
    "sub2b": "I \u662f\u4e3a\u4e86\u8ba9\u8f6c\u52a8\u52a8\u80fd\u957f\u5f97\u50cf \u00bdmv\u00b2",
    "sub2c": "\u624d\u88ab\u5355\u72ec\u62e2\u51fa\u6765\u7684\u7cfb\u6570",
    "title2": "\u8f6c\u52a8\u60ef\u91cf\u7531 r\u00b2 \u52a0\u6743",
    "desc2": "\u521a\u4f53\u7ed5\u8d28\u5fc3\u8f6c\u52a8\u65f6\uff0c\u5fae\u5143\u901f\u7387 v=\u03c9r\uff0c\u52a8\u80fd\u51fa\u73b0 r\u00b2\uff0c\u4ece\u800c\u5b9a\u4e49 I=\u222b r\u00b2 dm\u3002",
    "eq1": "\u00bd m v\u00b2 = \u00bd m (\u03c9 r)\u00b2",
    "eq2": "= \u00bd (m r\u00b2) \u03c9\u00b2",
    "t3": "\u56fe 2a-3\u3000\u628a |r+d|\u00b2 \u62c6\u6210\u4e09\u9879\uff0c\u4e2d\u95f4\u90a3\u9879\u79ef\u5b8c\u662f\u96f6",
    "s3": "\u65b0\u8f74 O \u4e0e\u8d28\u5fc3\u8f74 C \u5e73\u884c\u3002P \u662f\u4e00\u5c0f\u5757\u3002\u53ea\u6709\u8d28\u5fc3\u5b9a\u4e49\u80fd\u8ba9\u4ea4\u53c9\u9879\u6d88\u5931\u3002",
    "l3a": "\u51e0\u4f55\uff1aO \u65b0\u8f74\uff0cC \u8d28\u5fc3\uff0cP \u5fae\u5143",
    "axisO": "\u65b0\u8f74 O",
    "labC": "C",
    "labP": "P",
    "labd": "d",
    "labr": "r",
    "labrd": "r + d",
    "note3a": "P \u76f8\u5bf9 O \u7684\u4f4d\u7f6e = r + d",
    "sub3a": "d \u5bf9\u6240\u6709\u5fae\u5143\u76f8\u540c\uff1br \u968f P \u53d8",
    "l3b": "\u79ef\u5206\u540e\u4e09\u9879",
    "term1": "\u2460  \u222b|r|\u00b2 dm = I_C",
    "term2": "\u2461  2d\u00b7\u222b r dm = 0",
    "term2why": "\u8d28\u5fc3\u5b9a\u4e49\uff1a\u76f8\u5bf9 C\uff0c\u52a0\u6743\u4f4d\u7f6e\u548c\u4e3a\u96f6",
    "term3": "\u2462  |d|\u00b2 \u222b dm = m|d|\u00b2",
    "result3": "I_O = I_C + m|d|\u00b2",
    "warn3": "\u4e00\u7aef\u5fc5\u987b\u662f\u8d28\u5fc3\u8f74\uff0c\u4e24\u8f74\u5fc5\u987b\u5e73\u884c",
    "title3": "\u5e73\u884c\u8f74\u5b9a\u7406\u7684\u4e09\u9879\u5c55\u5f00",
    "desc3": "I_O=\u222b|r+d|\u00b2 dm \u5c55\u5f00\u540e\uff0c\u4ea4\u53c9\u9879\u56e0\u8d28\u5fc3\u5b9a\u4e49\u6d88\u5931\uff0c\u5269\u4e0b I_C + md\u00b2\u3002",
    "t4": "\u56fe 2a-4\u3000\u5408\u5e76\uff1a\u8d28\u5fc3\u6309\u8d28\u91cf\u52a0\u6743\uff0c\u60ef\u91cf\u5148\u642c\u8f74\u518d\u76f8\u52a0",
    "s4": "\u7b2c\u4e00\u904d\u6c42 C\u3002\u7b2c\u4e8c\u904d\u628a\u6bcf\u5757\u7684 I_C \u7528 m d\u00b2 \u642c\u5230\u603b\u8d28\u5fc3\u3002\u4e0d\u80fd\u628a\u5404\u5757\u81ea\u5df1\u7684 I_C \u76f4\u63a5\u52a0\u3002",
    "l4a": "\u8d28\u5fc3\uff1a\u8d28\u91cf\u52a0\u6743\uff0c\u4e0d\u662f\u4e24\u5706\u5fc3\u8fde\u7ebf\u4e2d\u70b9",
    "a2kg": "A  2 kg",
    "b4kg": "B  4 kg",
    "mid": "\u51e0\u4f55\u4e2d\u70b9",
    "comC": "\u603b\u8d28\u5fc3 C",
    "note4a": "C = (mA cA + mB cB) / (mA+mB)",
    "sub4a": "\u66f4\u9760\u8fd1\u8f83\u91cd\u7684 B",
    "l4b": "\u60ef\u91cf\uff1a\u6bcf\u5757 I_C + m\u2016c\u2212C\u2016\u00b2",
    "ia": "A\uff1aI_A + mA dA\u00b2",
    "ib": "B\uff1aI_B + mB dB\u00b2",
    "sumI": "I_C = \u03a3 (I_i + m_i d_i\u00b2)",
    "bad4": "\u9519\uff1aI_A + I_B  \u6f0f\u4e86\u642c\u8f74",
    "title4": "\u590d\u5408\u521a\u4f53\u7684\u8d28\u5fc3\u4e0e\u60ef\u91cf",
    "desc4": "\u8d28\u5fc3\u662f\u5404\u5757\u8d28\u5fc3\u7684\u8d28\u91cf\u52a0\u6743\u3002\u603b\u60ef\u91cf\u662f\u5404\u5757\u81ea\u8eab\u60ef\u91cf\u52a0\u5e73\u884c\u8f74\u9879\u3002",
}

MARKERS = """
    <marker id="ah-ink" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 10 5 0 10z" fill="#1f2937"/></marker>
    <marker id="ah-n" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 10 5 0 10z" fill="#1d4ed8"/></marker>
    <marker id="ah-v" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 10 5 0 10z" fill="#047857"/></marker>
    <marker id="ah-o" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 10 5 0 10z" fill="#c2410c"/></marker>
    <marker id="ah-p" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 10 5 0 10z" fill="#7c3aed"/></marker>
"""

STYLE = """
      .title { font: 700 16px "Segoe UI","Microsoft YaHei",sans-serif; fill:#111827; }
      .sub { font: 12px "Segoe UI","Microsoft YaHei",sans-serif; fill:#4b5563; }
      .lab { font: 700 13px "Segoe UI","Microsoft YaHei",sans-serif; fill:#111827; }
      .small { font: 12px "Segoe UI","Microsoft YaHei",sans-serif; fill:#374151; }
      .note { font: 12px "Segoe UI","Microsoft YaHei",sans-serif; fill:#1f2937; }
      .ok { font: 700 12px "Segoe UI","Microsoft YaHei",sans-serif; fill:#047857; }
      .eq { font: 700 14px "Segoe UI","Microsoft YaHei",sans-serif; fill:#111827; }
"""


def wrap(title, desc, width, height, body):
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-labelledby="t d">
  <title id="t">{title}</title>
  <desc id="d">{desc}</desc>

  <defs>
{MARKERS}
    <style>
{STYLE}
    </style>
  </defs>

  <rect width="{width}" height="{height}" fill="#ffffff"/>
{body}
</svg>
"""


def fig1():
    s = S
    body = f"""
  <text x="440" y="28" text-anchor="middle" class="title">{s['t1']}</text>
  <text x="440" y="50" text-anchor="middle" class="sub">{s['s1']}</text>

  <rect x="16" y="64" width="416" height="300" rx="10" fill="#f8fafc" stroke="#e5e7eb"/>
  <text x="224" y="88" text-anchor="middle" class="lab">{s['l1a']}</text>
  <rect x="90" y="150" width="120" height="80" fill="#bfdbfe" stroke="#1d4ed8" stroke-width="2"/>
  <text x="150" y="196" text-anchor="middle" class="small">{s['msmall']}</text>
  <line x1="220" y1="190" x2="300" y2="190" stroke="#047857" stroke-width="2.6" marker-end="url(#ah-v)"/>
  <text x="248" y="176" class="small" fill="#047857">{s['abig']}</text>
  <rect x="90" y="250" width="200" height="80" fill="#fed7aa" stroke="#c2410c" stroke-width="2"/>
  <text x="190" y="296" text-anchor="middle" class="small">{s['mbig']}</text>
  <line x1="300" y1="290" x2="360" y2="290" stroke="#c2410c" stroke-width="2.6" marker-end="url(#ah-o)"/>
  <text x="318" y="276" class="small" fill="#c2410c">{s['asmall']}</text>
  <text x="224" y="348" text-anchor="middle" class="ok">a = F / m</text>

  <rect x="448" y="64" width="416" height="300" rx="10" fill="#f8fafc" stroke="#e5e7eb"/>
  <text x="656" y="88" text-anchor="middle" class="lab">{s['l1b']}</text>
  <circle cx="656" cy="168" r="36" fill="#dbeafe" stroke="#1d4ed8" stroke-width="2"/>
  <circle cx="656" cy="168" r="4" fill="#111827"/>
  <path d="M 686 150 A 28 28 0 0 1 686 186" fill="none" stroke="#047857" stroke-width="2.4" marker-end="url(#ah-v)"/>
  <text x="720" y="172" class="small" fill="#047857">{s['ialpha_s']}</text>
  <circle cx="656" cy="268" r="52" fill="none" stroke="#c2410c" stroke-width="14"/>
  <circle cx="656" cy="268" r="4" fill="#111827"/>
  <path d="M 700 246 A 40 40 0 0 1 700 290" fill="none" stroke="#c2410c" stroke-width="2.4" marker-end="url(#ah-o)"/>
  <text x="724" y="274" class="small" fill="#c2410c">{s['ialpha_b']}</text>
  <text x="656" y="348" text-anchor="middle" class="ok">{'\u03b1'} = {'\u03c4'} / I</text>
"""
    return wrap(s["title1"], s["desc1"], 880, 380, body)


def fig2():
    s = S
    body = f"""
  <text x="440" y="28" text-anchor="middle" class="title">{s['t2']}</text>
  <text x="440" y="50" text-anchor="middle" class="sub">{s['s2']}</text>

  <rect x="16" y="64" width="416" height="320" rx="10" fill="#f8fafc" stroke="#e5e7eb"/>
  <text x="224" y="88" text-anchor="middle" class="lab">{s['l2a']}</text>
  <circle cx="210" cy="220" r="92" fill="#dbeafe" stroke="#1d4ed8" stroke-width="2"/>
  <circle cx="210" cy="220" r="5" fill="#111827"/>
  <text x="222" y="214" class="small">C</text>
  <line x1="210" y1="220" x2="286" y2="164" stroke="#c2410c" stroke-width="2.2" marker-end="url(#ah-o)"/>
  <text x="232" y="178" class="small" fill="#c2410c">r</text>
  <circle cx="292" cy="160" r="10" fill="#047857"/>
  <text x="306" y="148" class="small" fill="#047857">dm</text>
  <line x1="292" y1="160" x2="348" y2="236" stroke="#047857" stroke-width="2.6" marker-end="url(#ah-v)"/>
  <text x="330" y="188" class="small" fill="#047857">v = {'\u03c9'} r</text>
  <path d="M 248 248 A 40 40 0 0 0 172 258" fill="none" stroke="#7c3aed" stroke-width="2.2" marker-end="url(#ah-p)"/>
  <text x="224" y="348" text-anchor="middle" class="note">{s['note2a']}</text>
  <text x="224" y="368" text-anchor="middle" class="sub">{s['sub2a']}</text>

  <rect x="448" y="64" width="416" height="320" rx="10" fill="#f8fafc" stroke="#e5e7eb"/>
  <text x="656" y="88" text-anchor="middle" class="lab">{s['l2b']}</text>
  <text x="656" y="150" text-anchor="middle" class="eq">{s['eq1']}</text>
  <text x="656" y="186" text-anchor="middle" class="eq">{s['eq2']}</text>
  <text x="656" y="240" text-anchor="middle" class="ok">{s['erot']}</text>
  <text x="656" y="274" text-anchor="middle" class="lab">{s['idef']}</text>
  <text x="656" y="320" text-anchor="middle" class="note">{s['unit']}</text>
  <text x="656" y="348" text-anchor="middle" class="sub">{s['sub2b']}</text>
  <text x="656" y="368" text-anchor="middle" class="sub">{s['sub2c']}</text>
"""
    return wrap(s["title2"], s["desc2"], 880, 400, body)


def fig3():
    s = S
    body = f"""
  <text x="440" y="28" text-anchor="middle" class="title">{s['t3']}</text>
  <text x="440" y="50" text-anchor="middle" class="sub">{s['s3']}</text>

  <rect x="16" y="64" width="416" height="340" rx="10" fill="#f8fafc" stroke="#e5e7eb"/>
  <text x="224" y="88" text-anchor="middle" class="lab">{s['l3a']}</text>
  <line x1="88" y1="110" x2="88" y2="380" stroke="#c2410c" stroke-width="3"/>
  <text x="98" y="128" class="lab" fill="#c2410c">{s['axisO']}</text>
  <circle cx="88" cy="250" r="5" fill="#c2410c"/>
  <text x="64" y="246" class="small">O</text>
  <ellipse cx="250" cy="230" rx="110" ry="70" fill="#dbeafe" stroke="#1d4ed8" stroke-width="2"/>
  <circle cx="250" cy="230" r="6" fill="#111827"/>
  <text x="260" y="224" class="lab">{s['labC']}</text>
  <circle cx="330" cy="168" r="9" fill="#047857"/>
  <text x="342" y="158" class="small" fill="#047857">{s['labP']}</text>
  <line x1="88" y1="250" x2="244" y2="230" stroke="#c2410c" stroke-width="2.2" marker-end="url(#ah-o)"/>
  <text x="150" y="228" class="small" fill="#c2410c">{s['labd']}</text>
  <line x1="250" y1="230" x2="322" y2="174" stroke="#1d4ed8" stroke-width="2.2" marker-end="url(#ah-n)"/>
  <text x="268" y="192" class="small" fill="#1d4ed8">{s['labr']}</text>
  <line x1="88" y1="250" x2="322" y2="176" stroke="#047857" stroke-width="2.0" stroke-dasharray="6 4" marker-end="url(#ah-v)"/>
  <text x="170" y="290" class="small" fill="#047857">{s['labrd']}</text>
  <text x="224" y="368" text-anchor="middle" class="note">{s['note3a']}</text>
  <text x="224" y="388" text-anchor="middle" class="sub">{s['sub3a']}</text>

  <rect x="448" y="64" width="416" height="340" rx="10" fill="#f8fafc" stroke="#e5e7eb"/>
  <text x="656" y="88" text-anchor="middle" class="lab">{s['l3b']}</text>
  <text x="656" y="140" text-anchor="middle" class="eq">{s['term1']}</text>
  <text x="656" y="186" text-anchor="middle" class="eq">{s['term2']}</text>
  <text x="656" y="214" text-anchor="middle" class="sub">{s['term2why']}</text>
  <text x="656" y="260" text-anchor="middle" class="eq">{s['term3']}</text>
  <text x="656" y="318" text-anchor="middle" class="ok">{s['result3']}</text>
  <text x="656" y="354" text-anchor="middle" class="note">{s['warn3']}</text>
"""
    return wrap(s["title3"], s["desc3"], 880, 420, body)


def fig4():
    s = S
    body = f"""
  <text x="440" y="28" text-anchor="middle" class="title">{s['t4']}</text>
  <text x="440" y="50" text-anchor="middle" class="sub">{s['s4']}</text>

  <rect x="16" y="64" width="416" height="360" rx="10" fill="#f8fafc" stroke="#e5e7eb"/>
  <text x="224" y="88" text-anchor="middle" class="lab">{s['l4a']}</text>
  <circle cx="120" cy="230" r="36" fill="#bfdbfe" stroke="#1d4ed8" stroke-width="2"/>
  <circle cx="120" cy="230" r="5" fill="#111827"/>
  <text x="120" y="186" text-anchor="middle" class="small">{s['a2kg']}</text>
  <text x="120" y="284" text-anchor="middle" class="sub">cA=(0,0)</text>
  <circle cx="310" cy="250" r="52" fill="#fed7aa" stroke="#c2410c" stroke-width="2"/>
  <circle cx="310" cy="250" r="5" fill="#111827"/>
  <text x="310" y="196" text-anchor="middle" class="small">{s['b4kg']}</text>
  <text x="310" y="318" text-anchor="middle" class="sub">cB=(3,1)</text>
  <line x1="120" y1="230" x2="310" y2="250" stroke="#9ca3af" stroke-dasharray="5 4"/>
  <circle cx="215" cy="240" r="4" fill="#9ca3af"/>
  <text x="215" y="160" text-anchor="middle" class="sub">{s['mid']}</text>
  <line x1="215" y1="168" x2="215" y2="236" stroke="#9ca3af" stroke-dasharray="3 3"/>
  <circle cx="247" cy="243" r="7" fill="#047857"/>
  <text x="255" y="132" class="ok">{s['comC']}</text>
  <line x1="255" y1="140" x2="247" y2="236" stroke="#047857" stroke-width="2"/>
  <text x="224" y="368" text-anchor="middle" class="note">{s['note4a']}</text>
  <text x="224" y="392" text-anchor="middle" class="sub">{s['sub4a']}</text>

  <rect x="448" y="64" width="416" height="360" rx="10" fill="#f8fafc" stroke="#e5e7eb"/>
  <text x="656" y="88" text-anchor="middle" class="lab">{s['l4b']}</text>
  <text x="656" y="150" text-anchor="middle" class="eq">{s['ia']}</text>
  <text x="656" y="186" text-anchor="middle" class="eq">{s['ib']}</text>
  <text x="656" y="250" text-anchor="middle" class="ok">{s['sumI']}</text>
  <text x="656" y="300" text-anchor="middle" class="note" fill="#b91c1c">{s['bad4']}</text>
  <text x="656" y="360" text-anchor="middle" class="sub">dA=cA\u2212C\uff0c dB=cB\u2212C</text>
"""
    return wrap(s["title4"], s["desc4"], 880, 440, body)


def main():
    (OUT / "fig-02a-01-mass-vs-inertia.svg").write_text(fig1(), encoding="utf-8", newline="\n")
    (OUT / "fig-02a-02-rotate-ke.svg").write_text(fig2(), encoding="utf-8", newline="\n")
    (OUT / "fig-02a-03-parallel-axis.svg").write_text(fig3(), encoding="utf-8", newline="\n")
    (OUT / "fig-02a-04-composite.svg").write_text(fig4(), encoding="utf-8", newline="\n")
    print("wrote fig-02a-01 .. fig-02a-04")


if __name__ == "__main__":
    main()
