"""M1 보조: '템플릿을 STA 최대 위치로 옮긴다'는 게 무슨 뜻인지 가짜 STA로 보여 준다.

가짜 STA = 최대가 385번 샘플(스파이크 후 15.9ms)에 있는 EPSP + 잡음.
(Fig4g 첫 행 5258→6321의 피크 위치가 385)

실행: ~/.venvs/biocomp/bin/python 01_Synapse-STA/m1/roll_demo.py
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import pearsonr

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "common"))
from data import FS  # noqa: E402
from templates import base_templates, template_psp  # noqa: E402

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

rng = np.random.default_rng(0)
true_peak = 385
sta = template_psp(width_pre=true_peak - 110, width_rise=110, decay_factor=250, offset=0.25)
sta = sta + rng.normal(0, 0.02, sta.size)
sta = (sta - sta.min()) / (sta - sta.min()).max()  # 논문 코드처럼 0~1 정규화

peak = int(sta.argmax())
base = base_templates()["EPSP"]                                                   # 344번에 고정
rolled = template_psp(width_pre=peak - 110, width_rise=110, decay_factor=250, offset=0.25)  # STA 최대로 이동
r_base, r_roll = pearsonr(sta, base)[0], pearsonr(sta, rolled)[0]
print(f"STA 최대 위치: {peak}번 ({(peak - 235) / FS * 1000:+.1f}ms)")
print(f"고정 템플릿 상관 {r_base:.3f} / 옮긴 템플릿 상관 {r_roll:.3f} → 큰 값 {max(r_base, r_roll):.3f} 사용")

ms = (np.arange(sta.size) - 235) / FS * 1000
fig, axes = plt.subplots(1, 2, figsize=(13, 3.8), sharey=True)
for ax, tmpl, title, r in [(axes[0], base, "① 고정 템플릿 (최대 344번 = +11.6ms)", r_base),
                           (axes[1], rolled, f"② STA 최대({peak}번)로 옮긴 템플릿", r_roll)]:
    ax.plot(ms, sta, color="#999", lw=1, label="STA (가짜, 잡음 포함)")
    ax.plot(ms, tmpl, "r-", lw=2, label="EPSP 템플릿")
    ax.axvline(ms[peak], color="k", ls=":", lw=1)
    ax.axvline(ms[tmpl.argmax()], color="r", ls=":", lw=1)
    ax.axvline(0, color="gray", ls="--", lw=1)
    ax.set_title(f"{title}\n피어슨 상관 = {r:.3f}")
    ax.set_xlabel("출발 스파이크 기준 시간 (ms)")
axes[0].legend(loc="lower right")
out = Path(__file__).with_name("figs") / "roll_demo.png"
fig.tight_layout()
fig.savefig(out, dpi=130)
print(f"그림: {out}")
