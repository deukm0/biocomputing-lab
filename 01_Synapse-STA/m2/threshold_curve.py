"""M2: 출발 픽셀 5106의 판정 분포(종류별 개수·칩 위 위치)와 임계값별 연결 수 곡선.

곡선은 임계값 하나를 네 종류에 똑같이 적용한다 (실제 규칙은 IPSP만 0.89).
세션 3 사용자 예측: 0.90 → 12개, 0.70 → 50~60개.
실행: ~/.venvs/biocomp/bin/python 01_Synapse-STA/m2/threshold_curve.py
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "common"))
from data import load_fig4c  # noqa: E402
from judge import TYPES, correlations, judge  # noqa: E402

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False
SOURCE = 5106
COLORS = {"AP": "#7b3fbf", "AP+EP": "#1f5fbf", "EPSP": "#d62728", "IPSP": "#2ca02c"}

sta = load_fig4c()
pix = np.array([(i // 64 + 1) * 100 + i % 64 + 1 for i in range(len(sta))])
keep = pix != SOURCE
corr = {a: np.array([[correlations(s, align=a)[t] for t in TYPES] for s in sta[keep]]) for a in (True, False)}
labels = [judge(s)[0] for s in sta[keep]]

ths = np.round(np.arange(0.50, 0.96, 0.01), 2)
curves = {}
for align, C in corr.items():
    best, bmax = C.argmax(1), C.max(1)
    curves[align] = {t: np.array([((bmax > th) & (best == k)).sum() for th in ths]) for k, t in enumerate(TYPES)}
for th in (0.70, 0.80, 0.90):
    i = list(ths).index(th)
    total = sum(c[i] for c in curves[True].values())
    print(f"임계값 {th:.2f}: 연결 {total}개  " + ", ".join(f"{t} {curves[True][t][i]}" for t in TYPES))

fig, axes = plt.subplots(1, 3, figsize=(17, 4.6), gridspec_kw=dict(width_ratios=[1, 1.2, 1.6]))
# ① 종류별 개수 (실제 규칙)
cnt = [labels.count(t) for t in TYPES]
axes[0].bar(TYPES, cnt, color=[COLORS[t] for t in TYPES])
for i, n in enumerate(cnt):
    axes[0].text(i, n + 0.2, str(n), ha="center")
axes[0].set_title(f"① 종류별 판정 (출발 {SOURCE}, 총 {sum(cnt)}개)")
# ② 칩 위 위치
ax = axes[1]
ax.add_patch(plt.Rectangle((0.5, 0.5), 64, 64, fill=False, lw=0.5))
for p, l in zip(pix[keep], labels):
    if l:
        ax.plot(p % 100, p // 100, "o", color=COLORS[l], ms=6)
ax.plot(SOURCE % 100, SOURCE // 100, "k*", ms=14, label=f"출발 {SOURCE}")
for t in TYPES:
    ax.plot([], [], "o", color=COLORS[t], label=t)
ax.set_xlim(0, 65); ax.set_ylim(65, 0); ax.set_aspect("equal")
ax.set_xlabel("열"); ax.set_ylabel("행"); ax.legend(fontsize=7, loc="lower right")
ax.set_title("② 칩 위 위치 (64×64, 픽셀 간격 20μm)")
# ③ 임계값별 연결 수
ax = axes[2]
for align, ls, tag in [(True, "-", "정렬 켬"), (False, ":", "정렬 끔")]:
    total = sum(curves[align].values())
    ax.plot(ths, total, "k" + ls, lw=2, label=f"전체 ({tag})")
    if align:
        for t in TYPES:
            ax.plot(ths, curves[align][t], ls, color=COLORS[t], lw=1.2, label=t)
ax.axvline(0.80, color="gray", ls="--", lw=1)
ax.set_yscale("log")
ax.set_xlabel("임계값 (네 종류에 똑같이 적용)"); ax.set_ylabel("연결 수 (로그 눈금)")
ax.set_title("③ 임계값별 연결 수")
ax.legend(fontsize=7, ncol=2)
out = Path(__file__).with_name("figs") / "threshold_curve.png"
fig.tight_layout()
fig.savefig(out, dpi=120)
print(f"그림: {out}")
