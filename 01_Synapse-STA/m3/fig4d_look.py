"""M3-1: Fig4d 네 쌍을 그림으로 보며 검출 규칙을 눈으로 익힌다.

왼쪽(Pre, 출발 뉴런): 원신호 + 기준선(2000샘플 이동평균, 주황).
  회색 세로선 = 0.2초(1,883샘플) 칸 경계, 빨간 짧은 선 = 칸 평균 + 0.3 mV.
  빨간 점 = 그 칸의 최대값이 0.3 mV 선을 넘은 후보 (기울기 등 나머지 규칙은 아직 안 씀).
오른쪽(Post, 도착 뉴런): 기준선 뺀 신호 + 평균 +1 mV(빨강), 평균 -0.25 mV(파랑) 선.
  이 선을 넘는 창은 STA 평균에서 빠진다.

실행: ~/.venvs/biocomp/bin/python fig4d_look.py
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from common.data import load_fig4d  # noqa: E402

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

FS = 1205120 / 128          # 9415 Hz
WIN = int(0.2 * FS)         # 칸 크기 1883샘플
BASE = 2000                 # 기준선 이동평균 길이
EDGE = 15                   # 칸 경계에서 이 안쪽이면 버림


def baseline(x):
    return np.convolve(x, np.ones(BASE) / BASE, mode="same")


fig, axes = plt.subplots(4, 2, figsize=(14, 11))
for row, sheet in enumerate(["EPSP", "IPSP", "AP_EPSP", "AP"]):
    pre, post = load_fig4d(sheet)
    t = np.arange(len(pre)) / FS
    pre_c = pre - baseline(pre)
    post_c = post - baseline(post)

    # 왼쪽: Pre
    ax = axes[row, 0]
    ax.plot(t, pre, lw=0.4, color="0.3")
    ax.plot(t, baseline(pre), lw=1.2, color="orange")
    n_cand = 0
    for s in range(0, len(pre) - WIN + 1, WIN):
        w = pre_c[s:s + WIN]
        ax.axvline(s / FS, color="0.8", lw=0.6, zorder=0)
        thr = w.mean() + 0.3
        ax.hlines(thr + baseline(pre)[s + WIN // 2], s / FS, (s + WIN) / FS,
                  color="red", lw=0.8)
        k = int(np.argmax(w))
        ok = (w[k] > thr and w.min() < 0 and abs(w.min()) < 0.6 * w[k]
              and EDGE <= k < WIN - EDGE)
        if ok:
            n_cand += 1
            ax.plot((s + k) / FS, pre[s + k], "o", color="red", ms=4)
    ax.set_ylabel(f"{sheet}\nPre (mV)")
    ax.set_title(f"{sheet} · Pre — 칸 {len(pre) // WIN}개 중 후보 {n_cand}개", fontsize=10)

    # 오른쪽: Post
    ax = axes[row, 1]
    m = post_c.mean()
    ax.plot(t, post_c, lw=0.4, color="0.3")
    ax.axhline(m + 1.0, color="red", ls="--", lw=1)
    ax.axhline(m - 0.25, color="tab:blue", ls="--", lw=1)
    over = (post_c >= m + 1.0).mean() * 100
    ax.set_title(f"{sheet} · Post — 최대 {post_c.max():.2f} mV, 최소 {post_c.min():.2f} mV",
                 fontsize=10)
    ax.set_ylabel("Post (mV, 기준선 뺌)")
    print(f"{sheet}: Pre 후보 {n_cand}개 / Post 최대 {post_c.max():.2f}, "
          f"최소 {post_c.min():.2f}, +1mV 넘는 샘플 {over:.2f}%")

for ax in axes[-1]:
    ax.set_xlabel("시간 (초)")
fig.suptitle("왼쪽 Pre: 주황 = 기준선, 회색 세로선 = 0.2초 칸, 빨간 선 = 칸 평균+0.3 mV, 빨간 점 = 후보\n"
             "오른쪽 Post: 빨강 = 평균+1 mV, 파랑 = 평균-0.25 mV (넘으면 그 창은 STA 평균에서 제외)",
             fontsize=10)
fig.tight_layout(rect=(0, 0, 1, 0.96))
out = Path(__file__).parent / "figs" / "fig4d_look.png"
fig.savefig(out, dpi=120)
print("저장:", out)
