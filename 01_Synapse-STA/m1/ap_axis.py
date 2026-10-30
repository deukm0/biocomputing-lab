"""M1 보조: AP 템플릿 두 개(판정 코드 vs Fig4a 그림)를 시간 축에 겹쳐 그린다.

실행: ~/.venvs/biocomp/bin/python 01_Synapse-STA/m1/ap_axis.py
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "common"))
from data import FS, load_templates  # noqa: E402
from templates import base_templates  # noqa: E402

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

code_ap = base_templates()["AP"]   # Template_AP(pre=35, rise=200, τ=100)
paper_ap = load_templates()["AP"]  # Template_AP(pre=150, rise=120, τ=80)과 같음
ms = (np.arange(len(code_ap)) - 235) / FS * 1000

fig, ax = plt.subplots(figsize=(10, 4))
for v, color, label, side, y_start in [
        (code_ap, "r", "판정 코드: pre 35 · rise 200 · τ 100", -1, 0.35),
        (paper_ap, "k", "Fig4a 그림: pre 150 · rise 120 · τ 80", 1, 0.15)]:
    ax.plot(ms, v, color=color, lw=2, label=label)
    i = int(v.argmax())
    ax.plot(ms[i], v[i], "o", color=color)
    ax.annotate(f"최대 {i}번 = {ms[i]:+.1f}ms", (ms[i], v[i]), xytext=(side * 10, -4),
                textcoords="offset points", color=color, ha="left" if side > 0 else "right")
    start = int(np.argmax(v > 0))
    ax.annotate(f"오르기 시작 {start}번 = {ms[start]:+.1f}ms", (ms[start], 0),
                xytext=(ms[start] - 1, y_start), textcoords="data", color=color, ha="right",
                arrowprops=dict(arrowstyle="->", color=color))
ax.axvline(0, color="gray", ls="--")
ax.text(0.5, 1.07, "출발 뉴런 스파이크 (0ms)", color="gray")
ax.set_ylim(-0.05, 1.15)
ax.set_xlabel("출발 스파이크 기준 시간 (ms)   ※ 샘플 1개 ≈ 0.106ms")
ax.set_ylabel("정규화 전압")
ax.set_title("AP 템플릿 두 개: 같은 함수, 다른 설정값")
ax.legend(loc="upper right")
out = Path(__file__).with_name("figs") / "ap_axis.png"
fig.tight_layout()
fig.savefig(out, dpi=130)
print(f"그림: {out}")
