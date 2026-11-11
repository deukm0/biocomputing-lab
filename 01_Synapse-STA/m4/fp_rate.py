"""M4: 다른 접시(cross-dish) 대조군으로 FP rate 다시 계산.

논문 정의 (Extended Data Fig 2e):
    FP rate(θ) = (다른 접시 PCC > θ 개수) / (실제 접시 PCC > θ 개수)
그룹별로 계산하고 10그룹 평균. 분모가 고정이라 평균 순서는 상관없다.
결과: m4/fp_rate_ours.csv (그룹별·평균, > 와 ≥ 둘 다)
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from common.data import data_dir  # noqa: E402

D = data_dir()
OUT = Path(__file__).parent
TYPES = {"AP": "AP", "AP+EPSP": "APEP", "EPSP": "EPSP", "IPSP": "IPSP"}
CROSS = {"AP": "ED_FIG2c_d_AP.txt", "AP+EPSP": "ED_FIG2c_d_AP_EPSP.txt",
         "EPSP": "ED_FIG2c_d_EPSP.txt", "IPSP": "ED_FIG2c_d_IPSP.txt"}
N_PAIR = 4_096_000
THETAS = np.round(np.arange(0.80, 0.951, 0.01), 2)


def count_above(x, thetas, strict=True):
    """임계값마다 넘는 개수. 정렬 후 이분 탐색."""
    s = np.sort(x[~np.isnan(x)])
    side = "right" if strict else "left"   # > : 같은 값 제외, ≥ : 포함
    return len(s) - np.searchsorted(s, thetas, side=side)


def main():
    actual = pd.read_csv(D / "ED_FIG2b.txt", sep="\t")
    rows = []
    for t, col in TYPES.items():
        a = actual[col].to_numpy()
        cross = pd.read_csv(D / CROSS[t], header=None, engine="c")[0].to_numpy()
        assert len(cross) == 10 * N_PAIR
        print(t, "NaN actual", np.isnan(a).sum(), "cross", np.isnan(cross).sum())
        for strict in (True, False):
            n_act = count_above(a, THETAS, strict)
            for g in range(10):
                n_cr = count_above(cross[g * N_PAIR:(g + 1) * N_PAIR], THETAS, strict)
                for th, na, nc in zip(THETAS, n_act, n_cr):
                    rows.append(dict(type=t, op=">" if strict else ">=", theta=th, group=g + 1,
                                     n_actual=na, n_cross=nc, fp=100 * nc / na))
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "fp_rate_ours.csv", index=False)
    print("saved", len(df))


if __name__ == "__main__":
    main()
