"""M1 보조: '샘플'이 시간이라는 것을 EPSP 템플릿 위에 표시한다.

실행: ~/.venvs/biocomp/bin/python 01_Synapse-STA/m1/sample_axis.py
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "common"))
from data import FS  # noqa: E402
from templates import base_templates  # noqa: E402

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

epsp = base_templates()["EPSP"]
ms = (np.arange(len(epsp)) - 235) / FS * 1000  # 출발 스파이크 피크(235번 샘플)를 0ms로

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(ms, epsp, "k-", lw=2)
for (a, b), color, label in [((0, 235), "#ddd", "pre 235샘플 = 25ms\n(스파이크 전, 평평)"),
                             ((235, 345), "#fcc", "rise 110샘플 = 11.7ms\n(전압이 오름)"),
                             ((345, 705), "#cdf", "decay 360샘플 = 38ms\n(천천히 가라앉음)")]:
    ax.axvspan(ms[a], ms[b - 1], color=color, alpha=0.6)
    ax.text((ms[a] + ms[b - 1]) / 2, 0.06, label, ha="center", fontsize=9)
ax.axvline(0, color="r", ls="--")
ax.text(0.5, 1.05, "출발 뉴런 스파이크 (0ms)", color="r")
ax.set_xlabel("출발 스파이크 기준 시간 (ms)   ※ 샘플 1개 = 1/9,415초 ≈ 0.106ms")
ax.set_ylabel("정규화 전압")
ax.set_ylim(0, 1.12)
ax.set_title("EPSP 템플릿: 705샘플 = 약 75ms 창")
out = Path(__file__).with_name("figs") / "sample_axis.png"
fig.tight_layout()
fig.savefig(out, dpi=130)
print(f"그림: {out}")
