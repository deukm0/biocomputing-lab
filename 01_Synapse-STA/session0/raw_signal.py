"""세션 0-B: 진짜 데이터(Fig4d)의 출발(Pre)·도착(Post) 원신호를 눈으로 본다.

Fig4d.xlsx에는 연결 종류별(AP, AP_EPSP, EPSP, IPSP)로 연결된 픽셀 쌍 하나의
Pre, Post 신호가 들어 있다. 여기서는 EPSP 쌍을 그린다.

실행: ~/.venvs/biocomp/bin/python raw_signal.py [시트이름]
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

FS = 1205120 / 128
DATA = Path(__file__).resolve().parents[2] / "dataverse_files" / "Fig4d.xlsx"
sheet = sys.argv[1] if len(sys.argv) > 1 else "EPSP"

df = pd.read_excel(DATA, sheet_name=sheet)
pre, post = df["Pre"].to_numpy(), df["Post"].to_numpy()
t = np.arange(len(pre)) / FS
print(f"[{sheet}] {len(pre)}샘플 = {len(pre) / FS:.2f}초")
print(f"Pre  표준편차 {pre.std():.3f}, 최대 {pre.max():.3f}")
print(f"Post 표준편차 {post.std():.3f}, 최대 {post.max():.3f}")

# 전체 구간 + Pre 최대 피크 주변 확대
peak = int(np.argmax(pre))
lo, hi = max(peak - 235, 0), min(peak + 470, len(pre))

fig, axes = plt.subplots(2, 2, figsize=(12, 6), sharex="col")
for row, (sig, name) in enumerate([(pre, "Pre (출발 뉴런)"), (post, "Post (도착 뉴런)")]):
    axes[row, 0].plot(t, sig, lw=0.4)
    axes[row, 0].axvspan(t[lo], t[hi - 1], color="orange", alpha=0.3)
    axes[row, 0].set_ylabel(name)
    axes[row, 1].plot((np.arange(lo, hi) - peak) / FS * 1000, sig[lo:hi], lw=0.8)
    axes[row, 1].axvline(0, color="gray", ls=":")
axes[0, 0].set_title(f"{sheet} 쌍 전체 (주황 = 오른쪽 확대 구간)")
axes[0, 1].set_title("Pre에서 가장 큰 스파이크 주변 75ms")
axes[1, 0].set_xlabel("시간 (초)")
axes[1, 1].set_xlabel("스파이크 기준 시간 (ms)")
fig.tight_layout()
out = Path(__file__).parent / "figs" / f"raw_signal_{sheet}.png"
fig.savefig(out, dpi=130)
print("저장:", out)
