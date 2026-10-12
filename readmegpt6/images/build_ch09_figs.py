# -*- coding: utf-8 -*-
"""Generate UTF-8 SVG figures for chapter 09. ASCII source only."""
from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parent

# Chinese strings via unicode escapes so this file stays ASCII-safe.
S = {
    "f1t": "\u56fe 9-1  \u5148\u770b\u6e05\u573a\u666f\uff1an \u4ece A \u6307\u5411 B\uff0cu \u662f\u76f8\u5bf9\u63a5\u8fd1/\u5206\u79bb\u901f\u5ea6",
    "f1s": "\u672c\u7ae0\u516c\u5f0f\u90fd\u5efa\u5728\u8fd9\u4e00\u5bf9\u7b26\u53f7\u4e0a\u3002\u5148\u8ba4\u56fe\uff0c\u518d\u4ee3\u5165\u6570\u5b57\u3002",
    "f1a": "\u60c5\u5f62\u4e00\uff1a\u4e24\u4e2a\u90fd\u80fd\u52a8\u7684\u7269\u4f53\u5bf9\u649e",
    "f1b": "\u60c5\u5f62\u4e8c\uff1a\u5730\u9762\u662f A\uff0c\u4e0b\u843d\u7bb1\u5b50\u662f B",
    "rigidA": "\u521a\u4f53 A",
    "rigidB": "\u521a\u4f53 B",
    "u_neg": "\u672c\u56fe\u53cc\u65b9\u5bf9\u649e\uff0cu < 0\uff0c\u6b63\u5728\u63a5\u8fd1",
    "u_sign": "u = 0 \u521a\u63a5\u89e6\u4e14\u4e0d\u518d\u9760\u8fd1  |  u > 0 \u6b63\u5728\u5206\u5f00",
    "goal": "\u6c42\u89e3\u5668\u8981\u7b97\u7684\uff1a\u7528\u4e00\u5bf9\u51b2\u91cf\u628a u \u6539\u5230\u76ee\u6807\u503c",
    "groundA": "A \u5730\u9762\uff08\u53ef\u53d6\u9759\u8d28\u91cf\u65e0\u9650\uff09",
    "com": "\u8d28\u5fc3",
    "vbdown": "vB \u5411\u4e0b",
    "boxfall": "\u7bb1\u5b50\u4e0b\u843d\u65f6 u = vBy < 0",
    "nup": "\u6cd5\u7ebf\u671d\u4e0a\uff0c\u4e0d\u8981\u628a\u4e0b\u843d\u5199\u6210\u6b63\u901f\u5ea6",
    "f2t": "\u56fe 9-2  \u7b2c 3.1 \u8282\uff1a\u4e24\u4e2a\u8d28\u70b9\u5bf9\u5fc3\u78b0\u649e\uff0c\u6c42\u89e3\u5668\u5230\u5e95\u5728\u7b97\u4ec0\u4e48",
    "f2s": "\u5df2\u77e5 mA=2 kg\uff0cmB=3 kg\uff0c\u78b0\u524d\u901f\u5ea6 3 \u4e0e -1 m/s\uff0ce=0.5\u3002\u901f\u5ea6\u90fd\u662f\u6cbf n \u7684\u5206\u91cf\u3002",
    "before": "1. \u78b0\u524d\uff1a\u6b63\u5728\u63a5\u8fd1",
    "impulse": "2. \u4e00\u5bf9\u51b2\u91cf\uff1a\u4f5c\u7528\u53cd\u4f5c\u7528",
    "after": "3. \u78b0\u540e\uff1a\u5df2\u7ecf\u5206\u79bb",
    "neg_close": "\u8d1f\u53f7 = \u53cc\u65b9\u6cbf n \u6b63\u5728\u9760\u8fd1",
    "target_u": "\u76ee\u6807\uff1a\u78b0\u540e u = -e u = 2 m/s",
    "push_back": "\u88ab\u63a8\u56de\u53bb",
    "push_fwd": "\u88ab\u63a8\u5411\u524d",
    "du_rel": "\u76f8\u5bf9\u901f\u5ea6\u4e00\u5171\u6539\u4e86 6 m/s",
    "k_note": "K * lambda = \u76f8\u5bf9\u901f\u5ea6\u589e\u52a0\u91cf",
    "check": "\u7528\u4e24\u4e2a\u6761\u4ef6\u548c\u4e00\u6b21\u6362\u7b97\u68c0\u67e5\uff0c\u786e\u8ba4\u7b97\u7684\u662f\u540c\u4e00\u5bf9\u51b2\u91cf",
    "rest": "\u6062\u590d\u5173\u7cfb",
    "mom": "\u603b\u7ebf\u52a8\u91cf",
    "meff": "\u6709\u6548\u8d28\u91cf\u6362\u7b97",
    "f3t": "\u56fe 9-3  \u7b2c 4 \u8282\uff1a\u51b2\u91cf\u4e0d\u7a7f\u8fc7\u8d28\u5fc3\uff0c\u7bb1\u5b50\u4f1a\u8f6c",
    "f3s": "\u4e16\u754c\u5750\u6807\uff1a\u53f3\u4e3a +x\uff0c\u4e0a\u4e3a +y\u3002\u9006\u65f6\u9488\u4e3a\u6b63\u89d2\u901f\u5ea6\u3002",
    "what": "\u8fd9\u4e00\u6b65\u5728\u7b97\u4ec0\u4e48",
    "ang": "\u89d2\u52a8\u91cf\u5b9a\u7406\uff1aI \u0394\u03c9 = r \u00d7 P",
    "ccw": "\u9006\u65f6\u9488",
    "corner": "\u63a5\u89e6\u70b9 / \u53f3\u4e0b\u89d2",
    "lever": "\u53f3\u4e0b\u89d2\u88ab\u5411\u4e0a\u6253\uff0c\u6760\u6746\u8ba9\u7bb1\u5b50\u5de6\u8f6c",
    "ifcom": "\u82e5\u51b2\u91cf\u7a7f\u8fc7\u8d28\u5fc3\uff0cr \u00d7 P = 0\uff0c\u53ea\u6539\u5e73\u52a8\u3002",
    "needw": "\u8fb9\u89d2\u78b0\u649e\u5fc5\u987b\u540c\u65f6\u6539 v \u548c \u03c9\uff0c\u4e0d\u80fd\u53ea\u6539\u8d28\u5fc3\u901f\u5ea6\u3002",
    "f4t": "\u56fe 9-4  \u7b2c 5 \u8282\uff1a\u7ea6\u675f\u770b\u7684\u662f\u63a5\u89e6\u70b9\u901f\u5ea6\uff0c\u4e0d\u662f\u8d28\u5fc3\u901f\u5ea6",
    "f4s": "\u4f8b\uff1a\u03c9 = 2 rad/s\uff0c r = (0.5, -0.5) m\uff0c\u8f6c\u52a8\u8d21\u732e \u03c9 \u00d7 r = (1, 1) m/s\u3002",
    "where": "\u516c\u5f0f\u5728\u56fe\u4e0a\u7684\u4f4d\u7f6e",
    "vp": "\u5355\u70b9\u901f\u5ea6\uff1avp = v + \u03c9 \u00d7 r",
    "both": "\u89d2\u70b9\u65e2\u968f\u8d28\u5fc3\u5e73\u52a8\uff0c\u53c8\u88ab\u8f6c\u52a8\u7529\u51fa\u53bb",
    "vrel": "\u4e24\u7269\u4f53\u63a5\u89e6\u70b9\u76f8\u5bf9\u901f\u5ea6\uff1av_rel = vpB - vpA",
    "proj": "\u771f\u6b63\u7ea6\u675f\u7684\u662f\u6295\u5f71 u = n \u00b7 v_rel",
    "miss": "\u6f0f\u6389 \u03c9 \u00d7 r\uff0c\u6b63\u649e\u4ecd\u53ef\u80fd\u78b0\u5de7\u5bf9\uff0c\u8fb9\u89d2\u78b0\u649e\u4f1a\u9519\u3002",
    "f5t": "\u56fe 9-6  \u7b2c 7.1 \u8282\uff1a\u504f\u5fc3\u843d\u5730\uff0c\u63a5\u89e6\u70b9\u505c\u4f4f\u4e0d\u7b49\u4e8e\u8d28\u5fc3\u505c\u4f4f",
    "f5s": "A \u9759\u6b62\uff1bB \u7684 m=1 kg\uff0cI=0.5\uff0crB=(0.5,-0.5) m\uff0cn=(0,1)\uff0c\u78b0\u524d v=(0,-4)\uff0c\u03c9=0\uff0ce=0\u3002",
    "hit": "\u78b0\u524d\uff1a\u89d2\u70b9\u7838\u5411\u5730\u9762",
    "calc": "\u8ba1\u7b97\uff1a\u6746\u81c2\u8ba9 K \u53d8\u5927",
    "after2": "\u78b0\u540e\uff1a\u89d2\u70b9\u505c\uff0c\u8d28\u5fc3\u8fd8\u5728\u52a8",
    "onlyc": "u = -4 m/s\uff0c\u53ea\u5728\u89d2\u70b9\u63a5\u89e6",
    "need": "\u8981\u6d88\u6389\u63a5\u8fd1\u901f\u5ea6\uff1a",
    "smaller": "\u6bd4\u6b63\u649e\u7684 4 N s \u66f4\u5c0f\uff1a\u7269\u4f53\u53ef\u4ee5\u8f6c\u7740\u8ba9\u5f00\u3002",
    "headon": "\u6b63\u649e\u65f6 r \u00d7 n = 0\uff0cK=1\uff0cm_eff=1 kg",
    "jrel": "\u548c Jacobian \u7684\u5173\u7cfb\uff1aK \u5c31\u662f\u5355\u4f4d\u51b2\u91cf\u80fd\u6539\u591a\u5c11\u7ea6\u675f\u901f\u5ea6",
    "onlyb": "\u672c\u4f8b A \u9759\u6b62\uff0c\u53ea\u7559\u4e0b B \u7684\u5e73\u52a8\u9879 1 \u548c\u8f6c\u52a8\u9879 0.5",
    "f6t": "\u56fe 9-7  \u7b2c 10 \u8282\uff1a\u4e00\u4e2a\u7bb1\u5b50\u4e24\u4e2a\u89d2\u540c\u65f6\u6491\u5730\uff0c\u51b2\u91cf\u4f1a\u4e92\u76f8\u5e72\u6270",
    "f6s": "\u9759\u6001\u5730\u9762\uff1b\u7bb1\u5b50 m=1 kg\uff0cI=0.5\uff1br1=(-0.5,-0.5)\uff0cr2=(0.5,-0.5)\uff0cn=(0,1)\uff1b\u78b0\u524d vy=-4\uff0c\u03c9=0\u3002",
    "onebody": "B \u4e00\u4e2a\u521a\u4f53\uff0c\u4e24\u4e2a\u63a5\u89e6\u70b9",
    "pt1": "\u70b9 1",
    "pt2": "\u70b9 2",
    "why": "\u4e3a\u4ec0\u4e48\u4e0d\u80fd\u5404\u7b97\u5404\u7684",
    "diag": "\u5bf9\u89d2 1.5\uff1a\u672c\u70b9\u51b2\u91cf\u6539\u672c\u70b9\u901f\u5ea6",
    "off": "\u975e\u5bf9\u89d2 0.5\uff1a\u70b9 2 \u7684\u51b2\u91cf\u4f1a\u8f6c\u52a8\u521a\u4f53\uff0c\u4ece\u800c\u6539\u70b9 1",
    "sim": "\u4e24\u8fb9\u90fd\u6d3b\u52a8\u65f6\u8054\u7acb\u89e3\uff1aL1 = L2 = 2 N s",
    "result": "\u4e8e\u662f vy=0\uff0c\u03c9=0",
    "gs": "\u987a\u5e8f\u6c42\u89e3\u4e3a\u4ec0\u4e48\u7b2c\u4e00\u904d\u626b\u4e0d\u5e72\u51c0",
    "gs1": "\u5148\u89e3\u70b9 1 \u5f97\u5230 8/3\uff0c\u521a\u4f53\u5df2\u7ecf\u5e26\u7740\u8f6c\u52a8\uff1b\u518d\u89e3\u70b9 2 \u5f97\u5230 16/9\uff0c\u70b9 1 \u7684\u6b8b\u5dee\u53c8\u88ab\u5e26\u8d77\u6765\u3002",
    "gs2": "\u6240\u4ee5\u8981\u591a\u626b\u51e0\u904d\uff0c\u5e76\u4e14\u5141\u8bb8\u8d1f\u589e\u91cf\u628a\u591a\u63a8\u7684\u51b2\u91cf\u64a4\u56de\u3002\u8fd9\u4e0d\u662f\u5438\u529b\uff0c\u53ea\u662f\u4fee\u6b63\u3002",
    "ground": "A \u5730\u9762",
    "f7t": "\u56fe 9-5  \u7b2c 6 \u8282\uff1aJacobian \u628a\u5df2\u7ecf\u63a8\u51fa\u7684\u7cfb\u6570\u6392\u6210\u4e00\u884c",
    "f7s": "\u5b83\u4e0d\u662f\u65b0\u7684\u7269\u7406\u5b9a\u5f8b\uff0c\u53ea\u662f\u628a u \u548c\u51b2\u91cf\u66f4\u65b0\u5199\u6210\u77e9\u9635\u5f62\u5f0f\u3002",
    "vel6": "\u516d\u4e2a\u5e7f\u4e49\u901f\u5ea6 V",
    "urow": "\u7ea6\u675f\u901f\u5ea6 u",
    "imp": "\u6807\u91cf\u51b2\u91cf lambda",
    "gimp": "\u5e7f\u4e49\u51b2\u91cf J^T lambda",
    "dvel": "\u901f\u5ea6\u66f4\u65b0 dV",
    "read": "\u600e\u4e48\u8bfb\uff1a\u5148\u7528 J \u8bfb\u51fa\u76f8\u5bf9\u901f\u5ea6\uff0c\u518d\u7528 J^T \u628a\u51b2\u91cf\u64ad\u56de\u4e24\u4e2a\u521a\u4f53",
}

S = {key: escape(value, quote=False) for key, value in S.items()}

STYLE = """
    <style>
      .title { font: 700 16px "Segoe UI","Microsoft YaHei","Noto Sans SC",sans-serif; fill:#111827; }
      .sub { font: 12px "Segoe UI","Microsoft YaHei","Noto Sans SC",sans-serif; fill:#4b5563; }
      .lab { font: 700 13px "Segoe UI","Microsoft YaHei","Noto Sans SC",sans-serif; fill:#111827; }
      .small { font: 12px "Segoe UI","Microsoft YaHei","Noto Sans SC",sans-serif; fill:#374151; }
      .eq { font: 12px "Consolas","Segoe UI","Microsoft YaHei",sans-serif; fill:#1f2937; }
    </style>
    <defs>
      <marker id="n" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 10 5 0 10z" fill="#1d4ed8"/></marker>
      <marker id="v" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 10 5 0 10z" fill="#047857"/></marker>
      <marker id="p" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 10 5 0 10z" fill="#dc2626"/></marker>
      <marker id="r" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 10 5 0 10z" fill="#7c3aed"/></marker>
      <marker id="k" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 10 5 0 10z" fill="#1f2937"/></marker>
      <marker id="o" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 10 5 0 10z" fill="#b45309"/></marker>
    </defs>
"""


def svg(name, w, h, title, desc, body):
    text = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img">
  <title>{title}</title>
  <desc>{desc}</desc>
  {STYLE}
  <rect width="{w}" height="{h}" fill="#ffffff"/>
  {body}
</svg>
"""
    path = OUT / name
    path.write_text(text, encoding="utf-8", newline="\n")
    print("wrote", path.name, path.stat().st_size)


def fig1():
    svg(
        "fig-09-01-normal-relative-velocity.svg",
        880,
        400,
        S["f1t"],
        S["f1s"],
        f"""
  <text x="440" y="28" text-anchor="middle" class="title">{S['f1t']}</text>
  <text x="440" y="50" text-anchor="middle" class="sub">{S['f1s']}</text>
  <rect x="16" y="64" width="416" height="320" rx="10" fill="#f8fafc" stroke="#e5e7eb"/>
  <text x="224" y="88" text-anchor="middle" class="lab">{S['f1a']}</text>
  <line x1="60" y1="210" x2="380" y2="210" stroke="#d1d5db" stroke-dasharray="5 4"/>
  <circle cx="130" cy="210" r="38" fill="#bfdbfe" stroke="#1d4ed8" stroke-width="2"/>
  <circle cx="310" cy="210" r="38" fill="#fed7aa" stroke="#c2410c" stroke-width="2"/>
  <text x="130" y="206" text-anchor="middle" class="lab">A</text>
  <text x="130" y="224" text-anchor="middle" class="small">{S['rigidA']}</text>
  <text x="310" y="206" text-anchor="middle" class="lab">B</text>
  <text x="310" y="224" text-anchor="middle" class="small">{S['rigidB']}</text>
  <line x1="176" y1="210" x2="264" y2="210" stroke="#1d4ed8" stroke-width="2.4" marker-end="url(#n)"/>
  <text x="220" y="198" text-anchor="middle" class="small" fill="#1d4ed8">n</text>
  <line x1="100" y1="150" x2="168" y2="150" stroke="#047857" stroke-width="2.2" marker-end="url(#v)"/>
  <text x="134" y="140" text-anchor="middle" class="small" fill="#047857">vA</text>
  <line x1="340" y1="150" x2="272" y2="150" stroke="#047857" stroke-width="2.2" marker-end="url(#v)"/>
  <text x="306" y="140" text-anchor="middle" class="small" fill="#047857">vB</text>
  <text x="224" y="268" text-anchor="middle" class="eq">u = (vB - vA) · n</text>
  <text x="224" y="292" text-anchor="middle" class="small">{S['u_neg']}</text>
  <text x="224" y="316" text-anchor="middle" class="sub">{S['u_sign']}</text>
  <text x="224" y="360" text-anchor="middle" class="sub">{S['goal']}</text>
  <rect x="448" y="64" width="416" height="320" rx="10" fill="#f8fafc" stroke="#e5e7eb"/>
  <text x="656" y="88" text-anchor="middle" class="lab">{S['f1b']}</text>
  <line x1="500" y1="300" x2="812" y2="300" stroke="#6b7280" stroke-width="8"/>
  <text x="520" y="328" class="small">{S['groundA']}</text>
  <rect x="606" y="168" width="100" height="112" fill="#fed7aa" stroke="#c2410c" stroke-width="2"/>
  <circle cx="656" cy="224" r="4" fill="#111827"/>
  <text x="668" y="220" class="small">{S['com']}</text>
  <text x="656" y="252" text-anchor="middle" class="lab">B</text>
  <line x1="656" y1="292" x2="656" y2="236" stroke="#1d4ed8" stroke-width="2.4" marker-end="url(#n)"/>
  <text x="670" y="260" class="small" fill="#1d4ed8">n=(0,1)</text>
  <line x1="656" y1="200" x2="656" y2="248" stroke="#047857" stroke-width="2.2" marker-end="url(#v)"/>
  <text x="590" y="230" class="small" fill="#047857">{S['vbdown']}</text>
  <circle cx="656" cy="292" r="3.5" fill="#111827"/>
  <text x="656" y="352" text-anchor="middle" class="small">{S['boxfall']}</text>
  <text x="656" y="372" text-anchor="middle" class="sub">{S['nup']}</text>
""",
    )


def fig2():
    svg(
        "fig-09-02-head-on-collision.svg",
        920,
        560,
        S["f2t"],
        S["f2s"],
        f"""
  <text x="460" y="28" text-anchor="middle" class="title">{S['f2t']}</text>
  <text x="460" y="50" text-anchor="middle" class="sub">{S['f2s']}</text>
  <rect x="16" y="64" width="288" height="300" rx="10" fill="#f8fafc" stroke="#e5e7eb"/>
  <text x="160" y="90" text-anchor="middle" class="lab">{S['before']}</text>
  <circle cx="86" cy="190" r="34" fill="#bfdbfe" stroke="#1d4ed8" stroke-width="2"/>
  <circle cx="234" cy="190" r="40" fill="#fed7aa" stroke="#c2410c" stroke-width="2"/>
  <text x="86" y="186" text-anchor="middle" class="lab">A</text>
  <text x="86" y="202" text-anchor="middle" class="small">2 kg</text>
  <text x="234" y="186" text-anchor="middle" class="lab">B</text>
  <text x="234" y="202" text-anchor="middle" class="small">3 kg</text>
  <line x1="126" y1="190" x2="186" y2="190" stroke="#1d4ed8" stroke-width="2.2" marker-end="url(#n)"/>
  <text x="156" y="178" text-anchor="middle" class="small" fill="#1d4ed8">n</text>
  <line x1="50" y1="132" x2="130" y2="132" stroke="#047857" stroke-width="2.4" marker-end="url(#v)"/>
  <text x="90" y="122" text-anchor="middle" class="small" fill="#047857">vA- = 3 m/s</text>
  <line x1="270" y1="132" x2="190" y2="132" stroke="#047857" stroke-width="2.4" marker-end="url(#v)"/>
  <text x="230" y="122" text-anchor="middle" class="small" fill="#047857">vB- = -1 m/s</text>
  <text x="160" y="262" text-anchor="middle" class="eq">u- = vB- - vA-</text>
  <text x="160" y="284" text-anchor="middle" class="eq">= -1 - 3 = -4 m/s</text>
  <text x="160" y="312" text-anchor="middle" class="sub">{S['neg_close']}</text>
  <text x="160" y="348" text-anchor="middle" class="sub">{S['target_u']}</text>
  <rect x="316" y="64" width="288" height="300" rx="10" fill="#fff7ed" stroke="#fdba74"/>
  <text x="460" y="90" text-anchor="middle" class="lab">{S['impulse']}</text>
  <circle cx="386" cy="190" r="34" fill="#bfdbfe" stroke="#1d4ed8" stroke-width="2"/>
  <circle cx="534" cy="190" r="40" fill="#fed7aa" stroke="#c2410c" stroke-width="2"/>
  <text x="386" y="194" text-anchor="middle" class="lab">A</text>
  <text x="534" y="194" text-anchor="middle" class="lab">B</text>
  <line x1="454" y1="190" x2="400" y2="190" stroke="#dc2626" stroke-width="3" marker-end="url(#p)"/>
  <line x1="466" y1="190" x2="520" y2="190" stroke="#dc2626" stroke-width="3" marker-end="url(#p)"/>
  <text x="460" y="168" text-anchor="middle" class="small" fill="#dc2626">lambda = 7.2 N s</text>
  <text x="400" y="226" text-anchor="middle" class="small" fill="#dc2626">-lambda n</text>
  <text x="520" y="226" text-anchor="middle" class="small" fill="#dc2626">+lambda n</text>
  <text x="460" y="262" text-anchor="middle" class="eq">K = 1/2 + 1/3 = 5/6 /kg</text>
  <text x="460" y="284" text-anchor="middle" class="eq">m_eff = 1/K = 1.2 kg</text>
  <text x="460" y="312" text-anchor="middle" class="eq">lambda = -(1+e) u- / K</text>
  <text x="460" y="334" text-anchor="middle" class="eq">= -1.5 * (-4) / (5/6) = 7.2</text>
  <text x="460" y="356" text-anchor="middle" class="sub">{S['k_note']}</text>
  <rect x="616" y="64" width="288" height="300" rx="10" fill="#ecfdf5" stroke="#6ee7b7"/>
  <text x="760" y="90" text-anchor="middle" class="lab">{S['after']}</text>
  <circle cx="686" cy="190" r="34" fill="#bfdbfe" stroke="#1d4ed8" stroke-width="2"/>
  <circle cx="834" cy="190" r="40" fill="#fed7aa" stroke="#c2410c" stroke-width="2"/>
  <text x="686" y="186" text-anchor="middle" class="lab">A</text>
  <text x="686" y="202" text-anchor="middle" class="small">{S['push_back']}</text>
  <text x="834" y="186" text-anchor="middle" class="lab">B</text>
  <text x="834" y="202" text-anchor="middle" class="small">{S['push_fwd']}</text>
  <line x1="746" y1="132" x2="666" y2="132" stroke="#047857" stroke-width="2.4" marker-end="url(#v)"/>
  <text x="706" y="122" text-anchor="middle" class="small" fill="#047857">vA+ = -0.6</text>
  <line x1="794" y1="132" x2="874" y2="132" stroke="#047857" stroke-width="2.4" marker-end="url(#v)"/>
  <text x="834" y="122" text-anchor="middle" class="small" fill="#047857">vB+ = 1.4</text>
  <text x="760" y="262" text-anchor="middle" class="eq">dvA = -7.2 / 2 = -3.6</text>
  <text x="760" y="284" text-anchor="middle" class="eq">dvB = +7.2 / 3 = +2.4</text>
  <text x="760" y="312" text-anchor="middle" class="eq">u+ = 1.4 - (-0.6) = 2</text>
  <text x="760" y="334" text-anchor="middle" class="eq">{S['du_rel']}</text>
  <text x="760" y="356" text-anchor="middle" class="sub">= K * lambda = (5/6)*7.2</text>
  <rect x="16" y="380" width="888" height="164" rx="10" fill="#f3f4f6"/>
  <text x="460" y="408" text-anchor="middle" class="lab">{S['check']}</text>
  <rect x="36" y="424" width="270" height="100" rx="8" fill="#ffffff" stroke="#e5e7eb"/>
  <text x="171" y="450" text-anchor="middle" class="lab">{S['rest']}</text>
  <text x="171" y="476" text-anchor="middle" class="eq">u+ = -e u-</text>
  <text x="171" y="500" text-anchor="middle" class="eq">2 = -0.5 * (-4)</text>
  <rect x="324" y="424" width="270" height="100" rx="8" fill="#ffffff" stroke="#e5e7eb"/>
  <text x="459" y="450" text-anchor="middle" class="lab">{S['mom']}</text>
  <text x="459" y="476" text-anchor="middle" class="eq">2*3 + 3*(-1) = 3</text>
  <text x="459" y="500" text-anchor="middle" class="eq">2*(-0.6) + 3*1.4 = 3</text>
  <rect x="612" y="424" width="270" height="100" rx="8" fill="#ffffff" stroke="#e5e7eb"/>
  <text x="747" y="450" text-anchor="middle" class="lab">{S['meff']}</text>
  <text x="747" y="476" text-anchor="middle" class="eq">du = u+ - u- = 6 m/s</text>
  <text x="747" y="500" text-anchor="middle" class="eq">lambda = 1.2 * 6 = 7.2 N s</text>
""",
    )


def fig3():
    svg(
        "fig-09-03-eccentric-torque.svg",
        880,
        430,
        S["f3t"],
        S["f3s"],
        f"""
  <text x="440" y="28" text-anchor="middle" class="title">{S['f3t']}</text>
  <text x="440" y="50" text-anchor="middle" class="sub">{S['f3s']}</text>
  <rect x="16" y="64" width="520" height="350" rx="10" fill="#f8fafc" stroke="#e5e7eb"/>
  <rect x="170" y="120" width="180" height="180" fill="#fed7aa" stroke="#c2410c" stroke-width="2.2"/>
  <circle cx="260" cy="210" r="5" fill="#111827"/>
  <text x="272" y="206" class="lab">c {S['com']}</text>
  <line x1="260" y1="210" x2="344" y2="294" stroke="#7c3aed" stroke-width="2.3" marker-end="url(#r)"/>
  <text x="272" y="262" class="small" fill="#7c3aed">r = (0.5, -0.5) m</text>
  <circle cx="350" cy="300" r="5" fill="#111827"/>
  <text x="362" y="322" class="small">{S['corner']}</text>
  <line x1="350" y1="300" x2="350" y2="168" stroke="#dc2626" stroke-width="3" marker-end="url(#p)"/>
  <text x="364" y="210" class="small" fill="#dc2626">P = (0, 2) N s</text>
  <path d="M214 168 A70 70 0 0 0 196 230" fill="none" stroke="#c2410c" stroke-width="2.2" marker-end="url(#k)"/>
  <text x="142" y="188" class="small" fill="#c2410c">dw = +2 rad/s</text>
  <text x="142" y="208" class="small" fill="#c2410c">{S['ccw']}</text>
  <text x="276" y="396" text-anchor="middle" class="sub">{S['lever']}</text>
  <rect x="552" y="64" width="312" height="350" rx="10" fill="#fff7ed" stroke="#fdba74"/>
  <text x="708" y="96" text-anchor="middle" class="lab">{S['what']}</text>
  <text x="572" y="136" class="eq">{S['ang']}</text>
  <text x="572" y="168" class="eq">r x P = 0.5*2 - (-0.5)*0</text>
  <text x="572" y="190" class="eq">= 1 kg m^2 / s</text>
  <text x="572" y="222" class="eq">I = 0.5 kg m^2</text>
  <text x="572" y="244" class="eq">dw = 1 / 0.5 = 2 rad/s</text>
  <line x1="572" y1="268" x2="844" y2="268" stroke="#e5e7eb"/>
  <text x="572" y="300" class="small">{S['ifcom']}</text>
  <text x="572" y="348" class="small">{S['needw']}</text>
""",
    )


def fig4():
    svg(
        "fig-09-04-contact-point-velocity.svg",
        880,
        430,
        S["f4t"],
        S["f4s"],
        f"""
  <text x="440" y="28" text-anchor="middle" class="title">{S['f4t']}</text>
  <text x="440" y="50" text-anchor="middle" class="sub">{S['f4s']}</text>
  <rect x="16" y="64" width="520" height="350" rx="10" fill="#f8fafc" stroke="#e5e7eb"/>
  <rect x="170" y="120" width="180" height="180" fill="#fed7aa" stroke="#c2410c" stroke-width="2.2"/>
  <circle cx="260" cy="210" r="5" fill="#111827"/>
  <text x="248" y="198" text-anchor="end" class="lab">c</text>
  <line x1="260" y1="210" x2="260" y2="268" stroke="#047857" stroke-width="2.4" marker-end="url(#v)"/>
  <text x="214" y="248" class="small" fill="#047857">v</text>
  <line x1="260" y1="210" x2="344" y2="294" stroke="#7c3aed" stroke-width="2.2" marker-end="url(#r)"/>
  <text x="278" y="250" class="small" fill="#7c3aed">r</text>
  <circle cx="350" cy="300" r="5" fill="#111827"/>
  <line x1="350" y1="300" x2="430" y2="220" stroke="#b45309" stroke-width="2.6" marker-end="url(#o)"/>
  <text x="390" y="248" class="small" fill="#b45309">w x r = (1, 1)</text>
  <path d="M214 168 A70 70 0 0 0 196 230" fill="none" stroke="#c2410c" stroke-width="2.2" marker-end="url(#k)"/>
  <text x="148" y="188" class="small" fill="#c2410c">w &gt; 0</text>
  <text x="148" y="208" class="small" fill="#c2410c">{S['ccw']}</text>
  <text x="276" y="396" text-anchor="middle" class="sub">{S['both']}</text>
  <rect x="552" y="64" width="312" height="350" rx="10" fill="#ecfdf5" stroke="#6ee7b7"/>
  <text x="708" y="96" text-anchor="middle" class="lab">{S['where']}</text>
  <text x="572" y="136" class="eq">{S['vp']}</text>
  <text x="572" y="164" class="eq">w x r = (-w ry, w rx)</text>
  <text x="572" y="186" class="eq">= (2*0.5, 2*0.5) = (1, 1)</text>
  <line x1="572" y1="208" x2="844" y2="208" stroke="#d1d5db"/>
  <text x="572" y="236" class="small">{S['vrel']}</text>
  <text x="572" y="270" class="small">{S['proj']}</text>
  <text x="572" y="320" class="small">{S['miss']}</text>
""",
    )


def fig5():
    svg(
        "fig-09-06-effective-mass.svg",
        920,
        520,
        S["f5t"],
        S["f5s"],
        f"""
  <text x="460" y="28" text-anchor="middle" class="title">{S['f5t']}</text>
  <text x="460" y="50" text-anchor="middle" class="sub">{S['f5s']}</text>
  <rect x="16" y="64" width="290" height="300" rx="10" fill="#f8fafc" stroke="#e5e7eb"/>
  <text x="161" y="90" text-anchor="middle" class="lab">{S['hit']}</text>
  <line x1="40" y1="300" x2="280" y2="300" stroke="#6b7280" stroke-width="8"/>
  <text x="48" y="322" class="small">{S['ground']}</text>
  <rect x="86" y="148" width="120" height="120" fill="#fed7aa" stroke="#c2410c" stroke-width="2"/>
  <circle cx="146" cy="208" r="4" fill="#111827"/>
  <text x="156" y="204" class="small">c</text>
  <line x1="146" y1="208" x2="198" y2="260" stroke="#7c3aed" stroke-width="2.1" marker-end="url(#r)"/>
  <text x="186" y="228" class="small" fill="#7c3aed">rB</text>
  <circle cx="206" cy="268" r="4" fill="#111827"/>
  <line x1="206" y1="292" x2="206" y2="248" stroke="#1d4ed8" stroke-width="2.2" marker-end="url(#n)"/>
  <text x="216" y="268" class="small" fill="#1d4ed8">n</text>
  <line x1="146" y1="208" x2="146" y2="258" stroke="#047857" stroke-width="2.3" marker-end="url(#v)"/>
  <text x="88" y="240" class="small" fill="#047857">v = -4</text>
  <text x="161" y="348" text-anchor="middle" class="sub">{S['onlyc']}</text>
  <rect x="322" y="64" width="276" height="300" rx="10" fill="#fff7ed" stroke="#fdba74"/>
  <text x="460" y="90" text-anchor="middle" class="lab">{S['calc']}</text>
  <text x="340" y="124" class="eq">rB x n = 0.5 m</text>
  <text x="340" y="148" class="eq">K = 1/m + (r x n)^2 / I</text>
  <text x="340" y="172" class="eq">= 1 + 2*(0.5)^2 = 1.5 /kg</text>
  <text x="340" y="196" class="eq">m_eff = 1/K = 2/3 kg</text>
  <line x1="340" y1="212" x2="578" y2="212" stroke="#e5e7eb"/>
  <text x="340" y="238" class="eq">{S['need']}</text>
  <text x="340" y="262" class="eq">lambda = m_eff * 4 = 8/3 N s</text>
  <text x="340" y="294" class="small">{S['smaller']}</text>
  <text x="340" y="344" class="sub">{S['headon']}</text>
  <rect x="614" y="64" width="290" height="300" rx="10" fill="#ecfdf5" stroke="#6ee7b7"/>
  <text x="759" y="90" text-anchor="middle" class="lab">{S['after2']}</text>
  <line x1="638" y1="300" x2="878" y2="300" stroke="#6b7280" stroke-width="8"/>
  <rect x="708" y="148" width="120" height="120" fill="#fed7aa" stroke="#c2410c" stroke-width="2"/>
  <circle cx="768" cy="208" r="4" fill="#111827"/>
  <line x1="768" y1="208" x2="768" y2="248" stroke="#047857" stroke-width="2.3" marker-end="url(#v)"/>
  <text x="710" y="236" class="small" fill="#047857">vy=-4/3</text>
  <path d="M728 168 A52 52 0 0 0 716 214" fill="none" stroke="#c2410c" stroke-width="2.1" marker-end="url(#k)"/>
  <text x="668" y="188" class="small" fill="#c2410c">w=8/3</text>
  <circle cx="828" cy="268" r="4" fill="#111827"/>
  <line x1="828" y1="292" x2="828" y2="268" stroke="#dc2626" stroke-width="2.4" marker-end="url(#p)"/>
  <text x="759" y="336" text-anchor="middle" class="eq">u = vy + 0.5 w</text>
  <text x="759" y="356" text-anchor="middle" class="eq">= -4/3 + 4/3 = 0</text>
  <rect x="16" y="380" width="888" height="124" rx="10" fill="#f3f4f6"/>
  <text x="460" y="410" text-anchor="middle" class="lab">{S['jrel']}</text>
  <text x="460" y="438" text-anchor="middle" class="eq">du = J M^(-1) J^T lambda = K lambda</text>
  <text x="460" y="464" text-anchor="middle" class="eq">K = 1/mA + 1/mB + (rA x n)^2 / IA + (rB x n)^2 / IB</text>
  <text x="460" y="488" text-anchor="middle" class="sub">{S['onlyb']}</text>
""",
    )


def fig6():
    svg(
        "fig-09-07-two-contacts.svg",
        920,
        500,
        S["f6t"],
        S["f6s"],
        f"""
  <text x="460" y="28" text-anchor="middle" class="title">{S['f6t']}</text>
  <text x="460" y="50" text-anchor="middle" class="sub">{S['f6s']}</text>
  <rect x="16" y="64" width="520" height="300" rx="10" fill="#f8fafc" stroke="#e5e7eb"/>
  <line x1="48" y1="300" x2="500" y2="300" stroke="#6b7280" stroke-width="8"/>
  <text x="56" y="324" class="small">{S['ground']}</text>
  <rect x="188" y="148" width="180" height="140" fill="#fed7aa" stroke="#c2410c" stroke-width="2.2"/>
  <circle cx="278" cy="218" r="5" fill="#111827"/>
  <text x="288" y="214" class="lab">c</text>
  <line x1="278" y1="218" x2="208" y2="278" stroke="#7c3aed" stroke-width="2.1" marker-end="url(#r)"/>
  <line x1="278" y1="218" x2="348" y2="278" stroke="#7c3aed" stroke-width="2.1" marker-end="url(#r)"/>
  <text x="214" y="248" class="small" fill="#7c3aed">r1</text>
  <text x="328" y="248" class="small" fill="#7c3aed">r2</text>
  <circle cx="198" cy="288" r="4.5" fill="#111827"/>
  <circle cx="358" cy="288" r="4.5" fill="#111827"/>
  <text x="198" y="348" text-anchor="middle" class="small">{S['pt1']}</text>
  <text x="358" y="348" text-anchor="middle" class="small">{S['pt2']}</text>
  <line x1="198" y1="288" x2="198" y2="210" stroke="#dc2626" stroke-width="2.8" marker-end="url(#p)"/>
  <line x1="358" y1="288" x2="358" y2="210" stroke="#dc2626" stroke-width="2.8" marker-end="url(#p)"/>
  <text x="168" y="200" class="small" fill="#dc2626">L1=2</text>
  <text x="366" y="200" class="small" fill="#dc2626">L2=2</text>
  <line x1="278" y1="218" x2="278" y2="268" stroke="#047857" stroke-width="2.3" marker-end="url(#v)"/>
  <text x="288" y="252" class="small" fill="#047857">vy=-4</text>
  <text x="276" y="122" text-anchor="middle" class="lab">{S['onebody']}</text>
  <rect x="552" y="64" width="352" height="300" rx="10" fill="#fff7ed" stroke="#fdba74"/>
  <text x="728" y="96" text-anchor="middle" class="lab">{S['why']}</text>
  <text x="572" y="128" class="eq">Kij = 1/m + (ri x n)(rj x n)/I</text>
  <text x="572" y="156" class="eq">K = [ 1.5   0.5 ]</text>
  <text x="572" y="178" class="eq">    [ 0.5   1.5 ]</text>
  <text x="572" y="210" class="small">{S['diag']}</text>
  <text x="572" y="240" class="small">{S['off']}</text>
  <line x1="572" y1="270" x2="880" y2="270" stroke="#e5e7eb"/>
  <text x="572" y="296" class="eq">{S['sim']}</text>
  <text x="572" y="328" class="eq">{S['result']}</text>
  <rect x="16" y="380" width="888" height="104" rx="10" fill="#f3f4f6"/>
  <text x="460" y="410" text-anchor="middle" class="lab">{S['gs']}</text>
  <text x="460" y="438" text-anchor="middle" class="small">{S['gs1']}</text>
  <text x="460" y="464" text-anchor="middle" class="sub">{S['gs2']}</text>
""",
    )


def fig7():
    svg(
        "fig-09-05-jacobian.svg",
        920,
        360,
        S["f7t"],
        S["f7s"],
        f"""
  <text x="460" y="28" text-anchor="middle" class="title">{S['f7t']}</text>
  <text x="460" y="50" text-anchor="middle" class="sub">{S['f7s']}</text>
  <rect x="40" y="80" width="200" height="70" rx="8" fill="#dbeafe" stroke="#1d4ed8"/>
  <text x="140" y="108" text-anchor="middle" class="lab">{S['vel6']}</text>
  <text x="140" y="132" text-anchor="middle" class="eq">V = (vA, wA, vB, wB)</text>
  <line x1="240" y1="115" x2="310" y2="115" stroke="#1d4ed8" stroke-width="2.2" marker-end="url(#n)"/>
  <text x="275" y="104" text-anchor="middle" class="small" fill="#1d4ed8">J</text>
  <rect x="310" y="80" width="200" height="70" rx="8" fill="#ecfdf5" stroke="#047857"/>
  <text x="410" y="108" text-anchor="middle" class="lab">{S['urow']}</text>
  <text x="410" y="132" text-anchor="middle" class="eq">u = J V</text>
  <rect x="40" y="190" width="200" height="70" rx="8" fill="#fee2e2" stroke="#dc2626"/>
  <text x="140" y="218" text-anchor="middle" class="lab">{S['imp']}</text>
  <text x="140" y="242" text-anchor="middle" class="eq">lambda</text>
  <line x1="240" y1="225" x2="310" y2="225" stroke="#dc2626" stroke-width="2.2" marker-end="url(#p)"/>
  <text x="275" y="214" text-anchor="middle" class="small" fill="#dc2626">J^T</text>
  <rect x="310" y="190" width="200" height="70" rx="8" fill="#fff7ed" stroke="#c2410c"/>
  <text x="410" y="218" text-anchor="middle" class="lab">{S['gimp']}</text>
  <text x="410" y="242" text-anchor="middle" class="eq">A: -n    B: +n</text>
  <line x1="510" y1="225" x2="580" y2="225" stroke="#1f2937" stroke-width="2.2" marker-end="url(#k)"/>
  <text x="545" y="214" text-anchor="middle" class="small">M^(-1)</text>
  <rect x="580" y="190" width="200" height="70" rx="8" fill="#f3f4f6" stroke="#4b5563"/>
  <text x="680" y="218" text-anchor="middle" class="lab">{S['dvel']}</text>
  <text x="680" y="242" text-anchor="middle" class="eq">dV = M^(-1) J^T lambda</text>
  <rect x="580" y="80" width="300" height="70" rx="8" fill="#f8fafc" stroke="#e5e7eb"/>
  <text x="730" y="108" text-anchor="middle" class="lab">K = J M^(-1) J^T</text>
  <text x="730" y="132" text-anchor="middle" class="eq">du = K lambda ,  m_eff = 1/K</text>
  <text x="460" y="310" text-anchor="middle" class="small">{S['read']}</text>
  <text x="460" y="338" text-anchor="middle" class="sub">A \u53d7 -lambda n\uff0cB \u53d7 +lambda n\uff1b\u8f6c\u52a8\u5217\u518d\u4e58\u4e0a r \u00d7 n\u3002</text>
""",
    )


if __name__ == "__main__":
    fig1()
    fig2()
    fig3()
    fig4()
    fig5()
    fig6()
    fig7()
    for p in sorted(OUT.glob("fig-09-*.svg")):
        t = p.read_text(encoding="utf-8")
        assert "\u56fe 9-" in t, p.name
        print("utf8 ok", p.name)
