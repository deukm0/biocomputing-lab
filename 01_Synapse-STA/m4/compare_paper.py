"""우리 FP rate vs 논문 ED_FIG2e. 기준 1(재현)·3(견고성) 판정 출력."""
import sys
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from common.data import data_dir  # noqa: E402

OUT = Path(__file__).parent
COLS = ["AP", "AP+EPSP", "EPSP", "IPSP"]
PAPER_HEADLINE = {"EPSP": (0.80, 5.7), "AP": (0.80, 0.3), "AP+EPSP": (0.80, 1.3), "IPSP": (0.89, 9.5)}


def load_paper():
    x = pd.read_excel(data_dir() / "ED_FIG2e.xlsx", header=None)
    rows, theta, g = [], None, 0
    for _, r in x.iloc[2:].iterrows():
        if pd.notna(r[0]):
            theta, g = round(float(r[0]), 2), 0
        elif r[1] == "average":
            continue
        else:
            g += 1
            for i, t in enumerate(COLS):
                rows.append(dict(type=t, theta=theta, group=g, fp_paper=float(r[2 + i])))
    return pd.DataFrame(rows)


def main():
    ours = pd.read_csv(OUT / "fp_rate_ours.csv")
    paper = load_paper()
    for op in (">", ">="):
        m = ours[ours.op == op].merge(paper, on=["type", "theta", "group"])
        print(f"[{op}] 그룹별 최대 차이(%p): {np.abs(m.fp - m.fp_paper).max():.2e}")
    m = ours[ours.op == ">"].merge(paper, on=["type", "theta", "group"])
    m.to_csv(OUT / "fp_rate_vs_paper.csv", index=False)

    print("\n기준 1 (재현): θ에서 10그룹 평균, 소수 첫째 자리")
    ok1 = True
    for t, (th, val) in PAPER_HEADLINE.items():
        s = m[(m.type == t) & (m.theta == th)]
        mean = s.fp.mean()
        same = round(mean, 1) == val
        ok1 &= same
        print(f"  {t:8s} θ={th}: 우리 {mean:.3f}% → {round(mean,1)} / 논문 {val}  {'일치' if same else '불일치'}"
              f"  (분모 {s.n_actual.iloc[0]:,}, 분자 평균 {s.n_cross.mean():.1f})")
    print("  →", "성공" if ok1 else "실패")

    print("\n기준 3 (견고성): 같은 θ에서 그룹별 FP rate, 10% 초과 그룹")
    for t, (th, _) in PAPER_HEADLINE.items():
        s = m[(m.type == t) & (m.theta == th)].sort_values("group")
        over = s[s.fp > 10]
        print(f"  {t:8s} θ={th}: " + " ".join(f"{v:.1f}" for v in s.fp)
              + f" | 평균 {s.fp.mean():.1f} ± {s.fp.std(ddof=0):.1f} (sd), 범위 {s.fp.min():.1f}~{s.fp.max():.1f}"
              + f" | 10% 초과 {len(over)}개 (그룹 {over.group.tolist()})")

    print("\n참고: 그룹별로 10% 이하가 되는 최소 θ (0.01 간격, 0.80부터)")
    for t in COLS:
        need = []
        for g in range(1, 11):
            s = m[(m.type == t) & (m.group == g)].sort_values("theta")
            ok = s[(s.fp <= 10)]
            need.append(f"{ok.theta.min():.2f}" if len(ok) else ">0.95")
        mean_curve = m[m.type == t].groupby("theta").fp.mean()
        print(f"  {t:8s} 평균곡선 기준 {mean_curve[mean_curve <= 10].index.min():.2f} | 그룹별: {' '.join(need)}")

    print("\n참고: IPSP 그룹별 분자(다른 접시 넘은 개수) vs 분모, θ=0.80 / 0.89")
    for th in (0.80, 0.89):
        s = m[(m.type == "IPSP") & (m.theta == th)].sort_values("group")
        print(f"  θ={th}: 분모 {s.n_actual.iloc[0]}, 분자 {s.n_cross.tolist()}")


if __name__ == "__main__":
    main()
