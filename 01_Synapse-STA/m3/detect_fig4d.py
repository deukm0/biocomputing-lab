"""M3-2: Fig4d 네 쌍에 검출 + STA 창 제외 규칙을 끝까지 적용한다.

실행: ~/.venvs/biocomp/bin/python detect_fig4d.py
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common.data import load_fig4d  # noqa: E402
from detect import FS, PRE, STA_LEN, detect, sta  # noqa: E402

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

SHEETS = ["EPSP", "IPSP", "AP_EPSP", "AP"]
fig, axes = plt.subplots(4, 2, figsize=(14, 11), gridspec_kw=dict(width_ratios=[2.2, 1]))
for row, sheet in enumerate(SHEETS):
    pre, post = load_fig4d(sheet)
    spikes, log, pre_c = detect(pre, skip_stuck=True)  # Fig4d는 다듬은 신호라 멈춤 검사 끔
    wins = [r for r in log if isinstance(r, dict)]
    avg, n, reasons = sta(post, spikes)

    print(f"\n===== {sheet} =====")
    cand = [r for r in wins if r["height"] and r["shape"]]
    print(f"높이+모양 통과 칸 {len(cand)}개 → 최종 스파이크 {len(spikes)}개")
    for r in cand:
        tag = "최종" if r["final"] else ("경계라 탈락" if not r["not_edge"]
                                       else "기울기 탈락")
        print(f"  {r['peak'] / FS:5.2f}s  높이 {r['amp']:5.2f}  경계까지 {r['edge_dist']:4d}샘플  "
              f"slow={r['slow']!s:5} big={r['big']!s:5} → {tag}")
    for r in log:
        if not isinstance(r, dict):
            print("  [20초 창]", r[2])
    print(f"STA: {len(spikes)}개 창 중 {n}개 사용")
    for p, why in zip(spikes, reasons):
        if why != "사용":
            print(f"  {p / FS:5.2f}s 창 제외: {why}")

    # 왼쪽: 기준선 뺀 Pre + 최종 스파이크
    t = np.arange(len(pre)) / FS
    ax = axes[row, 0]
    ax.plot(t, pre_c, lw=0.4, color="0.3")
    fake = [r for r in cand if not r["final"]]
    ax.plot([r["peak"] / FS for r in fake], [pre_c[r["peak"]] for r in fake], "x",
            color="0.5", ms=7, mew=1.5, label="후보였다가 탈락")
    used = [p for p, w in zip(spikes, reasons) if w == "사용"]
    drop = [p for p, w in zip(spikes, reasons) if w not in ("사용", "창이 신호 밖")]
    edge = [p for p, w in zip(spikes, reasons) if w == "창이 신호 밖"]
    ax.plot(np.array(used) / FS, pre_c[used], "o", color="tab:green", ms=5,
            label="스파이크 · STA에 사용")
    ax.plot(np.array(drop) / FS, pre_c[drop], "o", mfc="none", mec="red", ms=7, mew=1.5,
            label="스파이크 · Post 때문에 창 제외")
    ax.plot(np.array(edge) / FS, pre_c[edge], "s", mfc="none", mec="tab:orange", ms=7, mew=1.5,
            label="스파이크 · 창이 신호 끝을 넘음")
    ax.set_title(f"{sheet} · Pre: 스파이크 {len(spikes)}개 중 STA 사용 {n}개", fontsize=10)
    ax.set_ylabel(f"{sheet}\nPre (mV)")
    if row == 0:
        ax.legend(fontsize=7, loc="upper left", ncol=4)

    # 오른쪽: STA
    ax = axes[row, 1]
    ms = (np.arange(STA_LEN) - PRE) / FS * 1000
    ax.plot(ms, avg - avg[:PRE].mean(), color="tab:purple")
    ax.axvline(0, color="gray", ls=":")
    ax.set_title(f"{sheet} · STA (N={n})" + ("  ← 창 0개, 평평" if n == 0 else ""), fontsize=10)
    ax.set_ylabel("Post 평균 (mV)")

axes[-1, 0].set_xlabel("시간 (초)")
axes[-1, 1].set_xlabel("출발 스파이크 기준 시간 (ms)")
fig.tight_layout()
out = Path(__file__).parent / "figs" / "detect_fig4d.png"
fig.savefig(out, dpi=120)
print("\n저장:", out)
