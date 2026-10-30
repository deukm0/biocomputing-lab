"""M2: Fig4g에서 AP로 판정된 쌍 3,008개의 STA 최대 위치 분포.

판정 코드의 AP 템플릿(최대 234번 = 0ms)을 썼다면 234 근처에,
Fig4a 그림의 AP 템플릿(최대 269번 = +3.6ms)을 썼다면 269 근처에 몰릴 것 (세션 3 예측).

실행: ~/.venvs/biocomp/bin/python 01_Synapse-STA/m2/ap_peak_hist.py
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "common"))
from data import FS, load_fig4g  # noqa: E402

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

g = load_fig4g()
names = {0: "AP", 0.5: "AP+EPSP", 1: "EPSP", -1: "IPSP"}
for t, name in names.items():
    pk = g.loc[g["type"] == t, "peak"]
    print(f"{name:8} {len(pk):6}쌍  최대 위치 중앙값 {pk.median():5.0f}  "
          f"범위(5~95%) {pk.quantile(.05):.0f}~{pk.quantile(.95):.0f}")
ap = g.loc[g["type"] == 0, "peak"].to_numpy()
for lo, hi in [(229, 239), (264, 274)]:
    print(f"AP 중 {lo}~{hi}번(±5): {((ap >= lo) & (ap <= hi)).mean():.1%}")

fig, axes = plt.subplots(1, 2, figsize=(13, 3.8))
bins = np.arange(0, 706, 5)
for t, name in names.items():
    axes[0].hist(g.loc[g["type"] == t, "peak"], bins=bins, histtype="step", lw=1.5,
                 density=True, label=name)
axes[0].set_title("종류별 STA 최대 위치 (Fig4g 전체, 높이는 비율)")
axes[0].legend()
axes[1].hist(ap, bins=np.arange(200, 320, 1), color="#555")
axes[1].set_title(f"AP 쌍 {len(ap):,}개만 확대")
for ax in axes:
    for x, c, lab in [(234, "r", "판정 코드 AP 최대 234"), (269, "b", "Fig4a 그림 AP 최대 269")]:
        ax.axvline(x, color=c, ls="--", lw=1, label=lab if ax is axes[1] else None)
    ax.set_xlabel("STA 최대 위치 (샘플, 235 = 출발 스파이크)")
axes[1].legend()
out = Path(__file__).with_name("figs") / "ap_peak_hist.png"
fig.tight_layout()
fig.savefig(out, dpi=130)
print(f"그림: {out}")
