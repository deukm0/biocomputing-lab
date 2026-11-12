"""틈 2 측정 준비: ED_FIG6a 원신호 4개가 잡음 배경으로 쓸 만한지 본다.

ED_FIG6a = 약물(CNQX+APV) 투여 전·중·씻은 뒤 녹음 (약 33분, 픽셀·짝 정보 없음).
여기서는 Post 배경으로만 쓴다 (무작위 시점 → 가짜 STA).

실행: ~/.venvs/biocomp/bin/python 01_Synapse-STA/gap2/look_fig6a.py
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fig6a import FS, load_trace  # noqa: E402

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

fig, axes = plt.subplots(4, 2, figsize=(14, 9), gridspec_kw={"width_ratios": [3, 1]})
for i in range(1, 5):
    x = load_trace(i)
    sec = int(FS)
    n = len(x) // sec
    blk = x[: n * sec].reshape(n, sec)
    t = np.arange(n) / 60
    ax = axes[i - 1, 0]
    ax.fill_between(t, blk.min(1), blk.max(1), color="#bbb", lw=0, label="1초 최소~최대")
    ax.plot(t, np.median(blk, 1), color="k", lw=0.6, label="1초 중앙값")
    ax.set_ylabel(f"trace{i}")
    s = int(5 * 60 * FS)  # 5분 지점 2초
    seg = x[s : s + int(2 * FS)]
    axes[i - 1, 1].plot(np.arange(len(seg)) / FS * 1000, seg, lw=0.4)
    print(f"trace{i}: 1초 중앙값의 표준편차 {np.median(blk, 1).std():.3f}, "
          f"1초 안 표준편차 중앙 {np.median(blk.std(1)):.3f}, "
          f"0.3 넘는 1초 칸 비율 {(blk.max(1) - np.median(blk, 1) > 0.3).mean():.1%}")
axes[0, 0].legend(loc="upper right", fontsize=8)
axes[0, 0].set_title("전체 33분 (x: 분)")
axes[0, 1].set_title("5분 지점 2초 확대 (x: ms)")
fig.tight_layout()
out = Path(__file__).with_name("figs") / "fig6a_look.png"
fig.savefig(out, dpi=110)
print(f"그림: {out}")
