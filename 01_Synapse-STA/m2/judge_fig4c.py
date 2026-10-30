"""M2: Fig4c(출발 픽셀 5106)의 STA 4,095개를 판정하고 SI Fig 11 라벨 23개와 비교한다.

판정 기준(BRIEF 덧붙임, 2026-10-30): 재현율·정밀도 둘 다 95% 이상이면 성공.
비교 조건: ① 코드 AP 템플릿 ② Fig4a 그림 AP 템플릿 ③ 정렬 끔
실행: ~/.venvs/biocomp/bin/python 01_Synapse-STA/m2/judge_fig4c.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "common"))
from data import load_fig4c, load_templates  # noqa: E402
from judge import judge  # noqa: E402

SOURCE = 5106
HERE = Path(__file__).parent

sta = load_fig4c()
pixels = [(i // 64 + 1) * 100 + i % 64 + 1 for i in range(len(sta))]
truth = pd.read_csv(HERE / "si_fig11_labels.csv", comment="#").set_index("pixel")

conditions = {
    "① 코드 AP": dict(),
    "② 그림 AP": dict(ap_template=load_templates()["AP"]),
    "③ 정렬 끔": dict(align=False),
}
rows = []
for name, kw in conditions.items():
    found = {}
    for p, s in zip(pixels, sta):
        if p == SOURCE:  # 자기 자신은 제외 (논문 코드: Pre_site != Post_site)
            continue
        label, pcc, _ = judge(s, **kw)
        if label:
            found[p] = (label, pcc)
    hit = [p for p in found if p in truth.index]
    same_type = [p for p in hit if found[p][0] == truth.loc[p, "type"]]
    recall, precision = len(hit) / len(truth), len(hit) / max(len(found), 1)
    rows.append(dict(조건=name, 판정수=len(found), 맞춘수=len(hit), 종류일치=len(same_type),
                     재현율=f"{recall:.1%}", 정밀도=f"{precision:.1%}"))
    if name == "① 코드 AP":
        detail = found
print(pd.DataFrame(rows).to_string(index=False))

print("\n[① 코드 AP] 쌍별 비교")
allp = sorted(set(truth.index) | set(detail))
for p in allp:
    t = f"{truth.loc[p, 'type']:5} {truth.loc[p, 'pcc']:.2f}" if p in truth.index else "  -       "
    o = f"{detail[p][0]:5} {detail[p][1]:.3f}" if p in detail else "  -"
    mark = "" if (p in truth.index and p in detail and truth.loc[p, "type"] == detail[p][0]) else "  ←"
    print(f"{p}: 논문 {t} | 우리 {o}{mark}")
