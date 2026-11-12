"""A 결과 그림: 가짜 STA 중 EPSP 통과의 지연 분포 vs Fig4g EPSP 지연 분포, 끝에 걸린 가짜 STA 예시.

실행: ~/.venvs/biocomp/bin/python 01_Synapse-STA/gap2/plot_null.py   (null_sta.py 먼저)
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "common"))
from data import FS, load_fig4g  # noqa: E402
from fig6a import load_trace  # noqa: E402
from null_sta import PERIODS, null_stas  # noqa: E402
import null_sta  # noqa: E402

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False


def wilson(k, n, zc=1.96):
    p = k / n
    c = (p + zc**2 / (2 * n)) / (1 + zc**2 / n)
    h = zc * np.sqrt(p * (1 - p) / n + zc**2 / (4 * n**2)) / (1 + zc**2 / n)
    return c - h, c + h


d = pd.read_csv(HERE / "null_sta.csv")
g = load_fig4g()
fig_e = g.loc[g.type == 1, "delay" if "delay" in g else "peak"].to_numpy()
bins = np.arange(170, 476, 10)

print("구간별 비율          Fig4g EPSP   가짜(창500)   가짜(창100)")
for lo, hi in [(170, 300), (300, 400), (400, 440), (440, 460), (460, 469)]:
    row = [((fig_e >= lo) & (fig_e <= hi)).mean()]
    for n in (500, 100):
        e = d[(d.n_win == n) & (d.label == "EPSP")].delay
        row.append(((e >= lo) & (e <= hi)).mean())
    print(f"  {lo}~{hi}:        " + "   ".join(f"{v:9.1%}" for v in row))
for n in (500, 100):
    e = d[(d.n_win == n) & (d.label == "EPSP")].delay
    k = int(((e >= 460) & (e <= 469)).sum())
    lo, hi = wilson(k, len(e))
    print(f"창{n}: 460~469 = {k}/{len(e)} = {k / len(e):.1%} (95% 구간 {lo:.1%}~{hi:.1%}), "
          f"출처: " + ", ".join(f"trace{t} {p[:5]} {c}" for (t, p), c in
                                d[(d.n_win == n) & (d.label == 'EPSP')].groupby(['trace', 'period']).size().items()))

fig, axes = plt.subplots(1, 3, figsize=(16, 4.2))
ax = axes[0]
ax.hist(fig_e, bins=bins, density=True, histtype="step", lw=2, color="k", label=f"Fig4g EPSP ({len(fig_e):,}쌍)")
for n, c in [(500, "C3"), (100, "C0")]:
    e = d[(d.n_win == n) & (d.label == "EPSP")].delay
    ax.hist(e, bins=bins, density=True, histtype="step", lw=1.5, color=c, label=f"가짜 STA, 창 {n} ({len(e)}개 통과)")
ax.axvspan(460, 470, color="orange", alpha=0.25, label="460~469 (마지막 1ms)")
ax.axvline(470, color="gray", ls="--", lw=1)
ax.set_xlabel("지연 (샘플, 235 = 출발 스파이크, 470 = 정렬 범위 끝)")
ax.set_title("EPSP로 통과한 것들의 지연 분포 (높이는 비율)")
ax.legend(fontsize=8, loc="upper left")

# 끝에 걸린 가짜 STA 예시: 같은 시드로 trace3 씻은 뒤를 다시 만들어 고른다
null_sta.RNG = np.random.default_rng(0)
x3 = None
for i in range(1, 4):
    x = load_trace(i)
    for name, (t0, t1) in PERIODS.items():
        st, _ = null_stas(x, t0, t1, 500)
        if i == 3 and name.startswith("씻은"):
            x3 = st
sel = d[(d.n_win == 500) & (d.trace == 3) & (d.period.str.startswith("씻은")) & (d.label == "EPSP")]
sel = sel.assign(k=sel.index - sel.index.min() + 0)
base = d[(d.n_win == 500) & (d.trace == 3) & (d.period.str.startswith("씻은"))].index.min()
t = (np.arange(705) - 235) / FS * 1000
ax = axes[1]
late = sel[sel.delay >= 460]
for j, (ix, r) in enumerate(late.head(5).iterrows()):
    s = x3[ix - base]
    s = (s - s.min()) / (s.max() - s.min())
    ax.plot(t, s + j * 0.0, lw=0.8, label=f"지연 {int(r.delay)}, PCC {r.pcc:.2f}")
ax.axvline(0, color="k", lw=0.8)
ax.axvline((470 - 235) / FS * 1000, color="gray", ls="--", lw=1)
ax.set_title("지연 460~469로 EPSP 통과한 가짜 STA (0~1 정규화)")
ax.set_xlabel("출발 시점 기준 시간 (ms)")
ax.legend(fontsize=7)

ax = axes[2]
for n, c in [(500, "C3"), (100, "C0")]:
    dd = d[d.n_win == n]
    ax.hist(dd.peak, bins=np.arange(0, 706, 15), density=True, histtype="step", color=c, label=f"모든 가짜 STA 최대 위치 (창 {n})")
ax.axvspan(240, 470, color="green", alpha=0.08, label="정렬 범위 240~470")
ax.set_title("판정 전: 가짜 STA 최대 위치 (전체 24,000개씩)")
ax.set_xlabel("STA 최대 위치 (샘플)")
ax.legend(fontsize=8)
fig.tight_layout()
out = HERE / "figs" / "null_delay.png"
fig.savefig(out, dpi=120)
print(f"그림: {out}")
