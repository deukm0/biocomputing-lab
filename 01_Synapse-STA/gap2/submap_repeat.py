"""틈 2 측정 B: Fig4g EPSP 중 지연이 창 끝(460~469)인 쌍은 중간(300~400)인 쌍보다 구간 지도에 덜 반복해서 나오나?

구간 지도 = Fig4e 6장 (81개 20분 구간 중 6개, 1장은 0~20분. 나머지 시점은 논문에 없음).
상관값이 높을수록 원래 잘 반복되므로 Fig4g 상관값 구간별로 비교한다.

판정 기준 (실행 전, 2026-11-12 사용자 동의): 같은 상관값 구간에서 끝 지연 쌍의 평균 등장 장수가
중간 지연 쌍의 70% 이하이면 "끝 지연 연결은 덜 반복된다".

실행: ~/.venvs/biocomp/bin/python 01_Synapse-STA/gap2/submap_repeat.py
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "common"))
from data import data_dir, load_fig4g  # noqa: E402

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

sheets = pd.read_excel(data_dir() / "Fig4e.xlsx", sheet_name=None, header=None)
sets = [set(zip(v[0].astype(int), v[1].astype(int))) for v in sheets.values()]
g = load_fig4g()
e = g[g.type == 1].copy()
e["n_sub"] = [sum((p, q) in s for s in sets) for p, q in zip(e.pre.astype(int), e.post.astype(int))]
e["bin"] = pd.cut(e.peak, [0, 299, 400, 459, 469], labels=["~299", "300~400", "401~459", "460~469"])
e["cbin"] = pd.cut(e["corr"], [0.80, 0.82, 0.85, 0.90, 1.0])
print(f"Fig4g EPSP {len(e):,}쌍 중 6장 중 한 장이라도 나온 비율 {(e.n_sub > 0).mean():.1%}")
tab = e.groupby(["cbin", "bin"], observed=True).n_sub.agg(["mean", "size"]).unstack("bin")
print("\n평균 등장 장수 (0~6) / 쌍 수")
print(tab.round(2).to_string())

print("\n=== 판정: 끝(460~469) ÷ 중간(300~400) ===")
ratios = []
for cb, sub in e.groupby("cbin", observed=True):
    mid = sub[sub.bin == "300~400"].n_sub
    end = sub[sub.bin == "460~469"].n_sub
    r = end.mean() / mid.mean()
    ratios.append(r)
    print(f"상관 {cb}: 중간 {mid.mean():.2f} ({len(mid)}쌍), 끝 {end.mean():.2f} ({len(end)}쌍) → {r:.0%}")
w = e[e.bin.isin(["300~400", "460~469"])]
# 상관값 구간 가중치를 끝 쌍 분포에 맞춘 전체 비율
wt = w[w.bin == "460~469"].cbin.value_counts(normalize=True)
mid_adj = sum(wt[c] * w[(w.bin == "300~400") & (w.cbin == c)].n_sub.mean() for c in wt.index)
end_m = w[w.bin == "460~469"].n_sub.mean()
print(f"상관값 분포를 맞춘 전체: 끝 {end_m:.2f} / 중간 {mid_adj:.2f} = {end_m / mid_adj:.0%}  (기준: 70% 이하)")

fig, axes = plt.subplots(1, 2, figsize=(13, 4))
for b, c in zip(["~299", "300~400", "401~459", "460~469"], ["C2", "C0", "C1", "C3"]):
    m = e[e.bin == b].groupby("cbin", observed=True).n_sub.mean()
    axes[0].plot(range(len(m)), m.values, "o-", color=c, label=f"지연 {b}")
axes[0].set_xticks(range(4), [str(c) for c in e.cbin.cat.categories])
axes[0].set_xlabel("Fig4g 상관값 구간")
axes[0].set_ylabel("구간 지도 6장 중 평균 등장 장수")
axes[0].set_title("지연별 반복 등장 (상관값 구간별)")
axes[0].legend()
for b, c in [("300~400", "C0"), ("460~469", "C3")]:
    v = e[e.bin == b].n_sub.value_counts(normalize=True).sort_index()
    axes[1].bar(v.index + (0.2 if b == "460~469" else -0.2), v.values, width=0.4, color=c, label=f"지연 {b}")
axes[1].set_xlabel("6장 중 등장 장수")
axes[1].set_title("등장 장수 분포 (상관값 구분 없이)")
axes[1].legend()
fig.tight_layout()
out = HERE / "figs" / "submap_repeat.png"
fig.savefig(out, dpi=120)
print(f"그림: {out}")
