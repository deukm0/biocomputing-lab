"""A에서 본 '0ms 뒤 오르막'이 창 제외 규칙에서 생기는지 확인.

무작위 시점이면 평균은 평평해야 한다. 그런데 규칙은 앞부분(0~235)만 조용하길 요구하고(흔들림 < 0.4 mV)
뒷부분은 +1 mV까지 허용한다 → 남은 창은 '앞은 조용, 뒤는 스파이크 가능' → 평균이 뒤로 갈수록 올라갈 수 있다.
같은 무작위 시점으로 규칙 켬/끔/앞부분 규칙만 끔을 비교한다.

실행: ~/.venvs/biocomp/bin/python 01_Synapse-STA/gap2/rule_effect.py
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from fig6a import FS, load_trace  # noqa: E402
from null_sta import L, PERIODS, PRE  # noqa: E402

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False
rng = np.random.default_rng(1)
idx = np.arange(L) - PRE
t = idx / FS * 1000

fig, axes = plt.subplots(4, 3, figsize=(15, 10), sharex=True)
for i in range(1, 5):
    x = load_trace(i)
    for j, (name, (t0, t1)) in enumerate(PERIODS.items()):
        lo, hi = int(t0 * 60 * FS) + PRE, int(t1 * 60 * FS) - L
        w = x[rng.integers(lo, hi, 100_000)[:, None] + idx]
        m = w.mean(1)
        up = w.max(1) < m + 1.0
        down = w.min(1) > m - 0.25
        pre = np.ptp(w[:, :PRE], 1) < 0.4
        ax = axes[i - 1, j]
        for mask, lab, c in [(np.ones(len(w), bool), "규칙 끔", "k"), (up & down & pre, "규칙 켬 (논문)", "C3"),
                             (up & down, "앞부분 규칙만 끔", "C0")]:
            a = w[mask].mean(0)
            ax.plot(t, a - a[:PRE].mean(), color=c, lw=1, label=f"{lab} ({mask.mean():.0%} 남음)")
        ax.axvline(0, color="gray", lw=0.6)
        ax.axvline((470 - PRE) / FS * 1000, color="gray", ls="--", lw=0.6)
        ax.set_title(f"trace{i} {name}", fontsize=9)
        ax.legend(fontsize=6)
        a_on = w[up & down & pre].mean(0)
        print(f"trace{i} {name}: 규칙 켬 → 뒤 25ms 평균 − 앞 25ms 평균 = "
              f"{a_on[-235:].mean() - a_on[:PRE].mean():+.4f} mV, 규칙 끔 → "
              f"{w.mean(0)[-235:].mean() - w.mean(0)[:PRE].mean():+.4f} mV")
for ax in axes[-1]:
    ax.set_xlabel("무작위 시점 기준 시간 (ms)")
fig.suptitle("무작위 시점 10만 개 평균 (앞 25ms 평균을 0으로). 점선 = 정렬 범위 끝(470)")
fig.tight_layout()
out = HERE / "figs" / "rule_effect.png"
fig.savefig(out, dpi=110)
print(f"그림: {out}")
