"""세션 0-C: '남은 잡음'과 '신호가 잡음의 몇 배'를 그림에 직접 표시한다.

- 회색 띠: 잡음이 보통 흔들리는 폭 (±1 표준편차). 이게 '남은 잡음'.
- 빨간 화살표: 진짜 신호(봉우리)의 높이. 항상 1.
- 제목의 'S/N': 신호 높이 ÷ 남은 잡음 = 봉우리가 잡음 띠보다 몇 배 높은가.

실행: ~/.venvs/biocomp/bin/python snr_explained.py
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

FS = 1205120 / 128
WIN, PRE = 705, 235
NOISE_SD = 10.0
NS = [1, 100, 1000, 10000]

rng = np.random.default_rng(0)
t_ms = (np.arange(WIN) - PRE) / FS * 1000
k = np.arange(WIN) - (PRE + int(0.003 * FS))
bump = np.where(k > 0, np.exp(-k / 80) - np.exp(-k / 15), 0.0)
bump /= bump.max()
peak_t = t_ms[np.argmax(bump)]

fig, axes = plt.subplots(len(NS), 1, figsize=(8, 10))
for ax, n in zip(axes, NS):
    sta = (bump + rng.normal(0, NOISE_SD, size=(n, WIN))).mean(axis=0)
    noise = NOISE_SD / np.sqrt(n)
    ax.fill_between(t_ms, -noise, noise, color="gray", alpha=0.3, label=f"남은 잡음 ±{noise:.2f}")
    ax.plot(t_ms, sta, lw=0.7, color="tab:blue", label="평균 낸 결과")
    ax.plot(t_ms, bump, lw=1.5, color="tab:red", label="진짜 신호 (높이 1)")
    ax.annotate("", xy=(peak_t, 1), xytext=(peak_t, 0),
                arrowprops=dict(arrowstyle="<->", color="tab:red", lw=2))
    ax.set_title(f"N={n}:  잡음 10/√{n} = {noise:.2f}  →  S/N = 1 ÷ {noise:.2f} = {1 / noise:.1f}배")
    ax.set_ylim(-max(3 * noise, 1.5), max(3 * noise, 1.5))
    ax.legend(loc="upper right", fontsize=8)
axes[-1].set_xlabel("출발 스파이크 기준 시간 (ms)")
fig.tight_layout()
out = Path(__file__).parent / "figs" / "snr_explained.png"
fig.savefig(out, dpi=130)
print("저장:", out)
