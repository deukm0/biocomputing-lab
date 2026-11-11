"""그림: 종류별 FP rate vs PCC 임계값. 회색 = 대조 접시 10개, 검정 = 평균, 빨강 점선 = 10%."""
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd

OUT = Path(__file__).parent
m = pd.read_csv(OUT / "fp_rate_vs_paper.csv")
HEAD = {"EPSP": 0.80, "AP": 0.80, "AP+EPSP": 0.80, "IPSP": 0.89}
fig, axes = plt.subplots(1, 4, figsize=(16, 4.2))
for ax, t in zip(axes, ["EPSP", "AP", "AP+EPSP", "IPSP"]):
    s = m[m.type == t]
    for g, sg in s.groupby("group"):
        over = (sg[sg.theta == HEAD[t]].fp > 10).any()
        ax.plot(sg.theta, sg.fp, color="tab:orange" if over else "0.7", lw=1.4 if over else 1,
                label=None)
        if over:
            v = sg[sg.theta == HEAD[t]].fp.iloc[0]
            ax.annotate(f"dish {g}", (HEAD[t], min(v, 60)), fontsize=8, color="tab:orange",
                        xytext=(4, 0), textcoords="offset points")
    mean = s.groupby("theta").fp.mean()
    ax.plot(mean.index, mean.values, "k-o", ms=3, lw=2, label="mean of 10")
    ax.axhline(10, color="r", ls="--", lw=1, label="10% rule")
    ax.axvline(HEAD[t], color="b", ls=":", lw=1, label=f"paper θ={HEAD[t]}")
    ax.set_title(f"{t}: mean {mean[HEAD[t]]:.1f}% at θ={HEAD[t]}")
    ax.set_xlabel("PCC threshold θ")
    ax.set_ylim(0, 60 if t == "IPSP" else (15 if t == "EPSP" else 5))
axes[0].set_ylabel("paper 'FP rate' (%) = cross count / actual count")
axes[0].legend(fontsize=8)
fig.suptitle("M4: cross-dish FP rate recomputed from published PCCs (orange = dish over 10% at paper θ; IPSP dish 2 at θ=0.80 is 280%, off scale)")
fig.tight_layout()
fig.savefig(OUT / "figs" / "m4_fp_rate.png", dpi=130)
print("saved")
