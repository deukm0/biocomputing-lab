"""M1: 논문 코드로 만든 템플릿이 Fig4a_templates.xlsx와 같은지 비교한다.

실행: ~/.venvs/biocomp/bin/python 01_Synapse-STA/m1/compare_templates.py
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "common"))
from data import TEMPLATE_NAMES, load_templates  # noqa: E402
from templates import ap_epsp_template, base_templates  # noqa: E402

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

paper = load_templates()
code = base_templates()
# AP+EPSP는 기본형이 없으니, 파일의 피크 위치에 맞춰 만든다 (argmax는 rise의 마지막 = peak-1)
code["AP+EP"] = ap_epsp_template(peak=int(np.argmax(paper["AP+EP"])) + 1)

print(f"{'템플릿':8} {'파일 최대위치':>12} {'코드 최대위치':>12} {'최대 오차':>10}")
for name in TEMPLATE_NAMES:
    p, c = paper[name], code[name]
    print(f"{name:8} {p.argmax():>12} {c.argmax():>12} {np.abs(p - c).max():>10.2e}")
print(f"IPSP 최소: 위치 {paper['IPSP'].argmin()}, 값 {paper['IPSP'].min():.4f}")

fig, axes = plt.subplots(1, 4, figsize=(16, 3.5), sharey=True)
for ax, name in zip(axes, TEMPLATE_NAMES):
    ax.plot(paper[name], "k-", lw=3, alpha=0.35, label="Fig4a 파일")
    ax.plot(code[name], "r--", lw=1.2, label="논문 코드")
    ax.set_title(f"{name}  (최대 오차 {np.abs(paper[name] - code[name]).max():.1e})")
    ax.set_xlabel("샘플")
axes[0].legend()
out = Path(__file__).with_name("figs") / "templates_vs_code.png"
out.parent.mkdir(exist_ok=True)
fig.tight_layout()
fig.savefig(out, dpi=130)
print(f"그림: {out}")
