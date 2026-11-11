"""M3-3: Fig4d에서 만든 STA를 M2 판정 함수(common/judge.py)로 판정한다.

AP·AP_EPSP는 STA에 쓴 창이 0개라 판정할 수 없다 (detect_fig4d.py 참고).
EPSP는 가짜 봉우리가 섞였으므로, 참고용으로 '높이 1 mV 이상 스파이크만' 쓴 STA도 판정한다.
실행: ~/.venvs/biocomp/bin/python 01_Synapse-STA/m3/judge_fig4d.py
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "common"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common.data import load_fig4d  # noqa: E402
from judge import THRESHOLDS, judge  # noqa: E402
from templates import base_templates  # noqa: E402
from detect import FS, detect, sta  # noqa: E402

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

cases = []
for sheet in ["EPSP", "IPSP", "AP_EPSP", "AP"]:
    pre, post = load_fig4d(sheet)
    spikes, log, pre_c = detect(pre, skip_stuck=True)
    avg, n, _ = sta(post, spikes)
    cases.append((sheet, avg, n))
    if sheet == "EPSP":
        real = [p for p in spikes if pre_c[p] >= 1.0]  # 가짜 봉우리(< 1 mV) 제거
        avg_r, n_r, _ = sta(post, real)
        cases.append(("EPSP (진짜만, 참고)", avg_r, n_r))

tmpl = base_templates()
print(f"임계값: {THRESHOLDS}")
fig, axes = plt.subplots(1, 3, figsize=(15, 4.2))
k = 0
for name, avg, n in cases:
    if n == 0:
        print(f"\n{name}: STA에 쓴 창 0개 → 판정 불가")
        continue
    label, best, c = judge(avg)
    print(f"\n{name}: 창 {n}개")
    print("  " + "  ".join(f"{t} {v:+.3f}" for t, v in c.items()))
    print(f"  → 최대 {max(c, key=c.get)} {best:.3f} / 판정: {label or '연결 아님'}")

    x = avg - avg.min()
    x = x / x.max()
    t_ms = (np.arange(len(x)) - 235) / FS * 1000
    ax = axes[k]
    k += 1
    want = name.split()[0]
    ax.plot(t_ms, x, color="0.2", lw=1, label=f"STA (창 {n}개, 0~1 정규화)")
    ax.plot(t_ms, tmpl[want], color="tab:red", lw=1.5, alpha=0.8, label=f"{want} 템플릿")
    ax.axvline(0, color="0.6", ls=":", lw=0.8)
    ax.set_title(f"{name}\n{want} 상관 {c[want]:.2f} (기준 {THRESHOLDS[want]}) → "
                 f"{label or '연결 아님'}", fontsize=10)
    ax.set_xlabel("Pre 스파이크 기준 시간 (ms)")
    ax.legend(fontsize=8, loc="best")

fig.suptitle("Fig4d로 직접 만든 STA vs 템플릿 (AP·AP_EPSP는 창 0개라 판정 불가)", fontsize=11)
fig.tight_layout(rect=(0, 0, 1, 0.94))
out = Path(__file__).parent / "figs" / "judge_fig4d.png"
fig.savefig(out, dpi=130)
print(f"\n저장: {out}")
