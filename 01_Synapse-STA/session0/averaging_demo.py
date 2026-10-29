"""세션 0-A: 평균을 내면 잡음이 줄어드는 것을 가짜 데이터로 확인한다.

설정
- 진짜 신호: 높이 1짜리 작은 봉우리(EPSP 흉내). 75ms 창 안, 앞 1/3 지점 조금 뒤에 있다.
- 잡음: 표준편차 10. 즉 잡음이 신호보다 10배 크다. 한 번만 보면 봉우리가 안 보인다.
- 같은 봉우리 + 매번 다른 잡음인 조각을 N개 만들어 평균을 낸다 (= STA가 하는 일).

실행: ~/.venvs/biocomp/bin/python averaging_demo.py
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter, NullFormatter

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["mathtext.fontset"] = "dejavusans"

FS = 1205120 / 128          # 샘플링 주파수 ≈ 9,415 Hz (논문 코드와 같음)
WIN = 705                   # STA 창 길이 (약 75ms)
PRE = 235                   # 출발 스파이크 피크 앞쪽 샘플 수 (창의 1/3)
NOISE_SD = 10.0
NS = [1, 10, 100, 1000, 10000]

rng = np.random.default_rng(0)
t_ms = (np.arange(WIN) - PRE) / FS * 1000   # 0ms = 출발 뉴런 스파이크 순간

# EPSP 모양: 빠르게 오르고 천천히 내려가는 봉우리, 스파이크 후 약 3ms에 시작
onset = PRE + int(0.003 * FS)
k = np.arange(WIN) - onset
bump = np.where(k > 0, np.exp(-k / 80) - np.exp(-k / 15), 0.0)
bump /= bump.max()

fig, axes = plt.subplots(len(NS) + 1, 1, figsize=(8, 11))
residual_sd = []
for ax, n in zip(axes, NS):
    trials = bump + rng.normal(0, NOISE_SD, size=(n, WIN))
    sta = trials.mean(axis=0)
    residual_sd.append((sta - bump).std())
    ax.plot(t_ms, sta, lw=0.8, color="tab:blue", label=f"N={n} 평균")
    ax.plot(t_ms, bump, lw=1.5, color="tab:red", label="진짜 신호")
    ax.axvline(0, color="gray", ls=":", lw=1)
    ax.set_ylabel("전압 (임의 단위)")
    ax.legend(loc="upper right", fontsize=8)

ax = axes[-1]
ax.loglog(NS, residual_sd, "o-", label="평균 후 남은 잡음 (측정)")
ax.loglog(NS, NOISE_SD / np.sqrt(NS), "--", label="10 / √N (이론)")
ax.axhline(1, color="tab:red", lw=1, label="신호 높이")
for axis in (ax.xaxis, ax.yaxis):   # 로그축 눈금을 10^-1 대신 0.1처럼 표시
    axis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))
    axis.set_minor_formatter(NullFormatter())
ax.set_xlabel("평균 낸 조각 수 N")
ax.set_ylabel("남은 잡음 크기")
ax.legend(fontsize=8)
axes[-2].set_xlabel("출발 스파이크 기준 시간 (ms)")

fig.tight_layout()
out = Path(__file__).parent / "figs" / "averaging_demo.png"
fig.savefig(out, dpi=130)
for n, s in zip(NS, residual_sd):
    print(f"N={n:>6}: 남은 잡음 {s:.3f}  (이론 {NOISE_SD / np.sqrt(n):.3f})")
print("저장:", out)
