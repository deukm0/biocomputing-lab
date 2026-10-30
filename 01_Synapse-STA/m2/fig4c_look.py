"""M2: Fig4c의 STA가 실제로 어떻게 생겼는지 본다.

위: 진폭(최대−최소)이 큰 줄 / 아래: EPSP 템플릿 상관이 높은 줄. 칩 위 위치도 함께.
실행: ~/.venvs/biocomp/bin/python 01_Synapse-STA/m2/fig4c_look.py
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "common"))
from data import FS, load_fig4c  # noqa: E402
from templates import base_templates, template_psp  # noqa: E402

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False


def epsp_corr(row):
    """판정 코드와 같은 방식: 0~1 정규화, 기본·이동 EPSP 템플릿 중 큰 상관."""
    x = row - row.min()
    x = x / x.max()
    pk = int(x.argmax())
    pk = pk if 240 < pk < 470 else 355
    rolled = template_psp(width_pre=pk - 110, width_rise=110, decay_factor=250, offset=0.25)
    return max(np.corrcoef(x, base_templates()["EPSP"])[0, 1], np.corrcoef(x, rolled)[0, 1])


sta = load_fig4c()
amp = sta.max(1) - sta.min(1)
corr = np.array([epsp_corr(r) for r in sta])
ms = np.arange(sta.shape[1]) / FS * 1000 - 25
pix = lambda i: (i // 64 + 1) * 100 + i % 64 + 1  # noqa: E731

fig = plt.figure(figsize=(15, 7))
for k, (title, idx) in enumerate([("진폭 상위 4줄", np.argsort(amp)[::-1][:4]),
                                  ("EPSP 상관 상위 4줄", np.argsort(corr)[::-1][:4])]):
    for j, i in enumerate(idx):
        ax = fig.add_subplot(2, 5, k * 5 + j + 1)
        ax.plot(ms, sta[i] - sta[i].mean(), lw=0.7)
        ax.axvline(0, color="r", ls="--", lw=0.7)
        ax.set_title(f"{title if j == 0 else ''}\n픽셀 {pix(i)}: 진폭 {amp[i]:.3f}, 상관 {corr[i]:.2f}", fontsize=8)
        ax.tick_params(labelsize=7)
ax = fig.add_subplot(2, 5, 5)
im = ax.imshow(amp.reshape(64, 64), cmap="viridis")
ax.set_title("칩 위 진폭", fontsize=9)
fig.colorbar(im, ax=ax, fraction=0.046)
ax = fig.add_subplot(2, 5, 10)
im = ax.imshow(corr.reshape(64, 64), cmap="RdBu_r", vmin=-1, vmax=1)
ax.set_title("칩 위 EPSP 상관", fontsize=9)
fig.colorbar(im, ax=ax, fraction=0.046)
fig.supxlabel("출발 스파이크 기준 시간 (ms)")
out = Path(__file__).with_name("figs") / "fig4c_look.png"
fig.tight_layout()
fig.savefig(out, dpi=120)
print(f"진폭 중앙값 {np.median(amp):.4f}, 상관>0.8 {np.sum(corr > 0.8)}줄, 그림: {out}")
