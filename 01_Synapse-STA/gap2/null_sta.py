"""틈 2 측정 A: 연결이 없는 가짜 STA를 판정기에 넣으면, EPSP로 통과한 것의 지연이 창 끝(460~469)에 몰리나?

가짜 STA = ED_FIG6a 원신호(도착 쪽 배경) 위의 무작위 시점 500개로 자른 창의 평균.
창 제외 규칙은 논문 코드 그대로(m3/detect.py의 sta와 같음: 위로 1 mV, 아래로 0.25 mV, 앞부분 흔들림 0.4 mV).
판정·지연은 논문 코드 Relation_Define_STA_v5(2536~2672행)와 같은 규칙:
  EPSP가 이기면 기본 템플릿이 이긴 경우 지연 = round((345 + 최대위치)/2), 옮긴 템플릿이면 최대위치(240<·<470, 아니면 355).

판정 기준 (실행 전, 2026-11-12 사용자 동의): 통과한 EPSP 중 지연 460~469 비율이 4.4%(=10/229)의 2배 이상이면
"창 끝이 잡음을 EPSP로 끌어들이는 구조가 있다". 주 결과는 창 500개.

실행: ~/.venvs/biocomp/bin/python 01_Synapse-STA/gap2/null_sta.py   (약 몇 분)
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "common"))
from fig6a import FS, load_trace  # noqa: E402
from templates import ap_epsp_template, base_templates, template_psp  # noqa: E402

L, PRE = 705, 235
PERIODS = {"약물 전 (0~10분)": (0.2, 10.0), "약물 중 (11~26분)": (11.0, 26.0), "씻은 뒤 (28~33분)": (28.0, 33.2)}
N_STA = 2000
RNG = np.random.default_rng(0)


def z(a):
    a = a - a.mean(-1, keepdims=True)
    return a / np.linalg.norm(a, axis=-1, keepdims=True)


B = base_templates()
ZB = {k: z(v) for k, v in B.items()}
ZE = {p: z(template_psp(width_pre=p - 110, width_rise=110, decay_factor=250, offset=0.25)) for p in range(241, 470)}
ZE[355] = z(template_psp(width_pre=245, width_rise=110, decay_factor=250, offset=0.25))
ZA = {p: z(ap_epsp_template(p)) for p in range(241, 470)}
ZA[355] = z(ap_epsp_template(355))
ZI = {q: z(1 - template_psp(width_pre=q - 110, width_rise=110, decay_factor=250, offset=0.25)) for q in range(351, 470)}
ZI[410] = z(1 - template_psp(width_pre=300, width_rise=110, decay_factor=250, offset=0.25))


def judge_rows(stas):
    """STA 여러 개 → DataFrame(종류, 최대 PCC, 지연, 최대위치, 최소위치, 4개 PCC)."""
    rows = []
    for s in stas:
        x = s - s.min()
        if x.max() != 0:
            x = x / x.max()
        pk, tr = int(x.argmax()), int(x.argmin())
        zx = z(x)
        p = pk if 240 < pk < 470 else 355
        q = tr if 350 < tr < 470 else 410
        c = {
            "AP": zx @ ZB["AP"], "AP+EP": zx @ ZA[p],
            "EPSP_base": zx @ ZB["EPSP"], "EPSP_roll": zx @ ZE[p],
            "IPSP_base": zx @ ZB["IPSP"], "IPSP_roll": zx @ ZI[q],
        }
        four = {"AP": c["AP"], "AP+EP": c["AP+EP"], "EPSP": max(c["EPSP_base"], c["EPSP_roll"]),
                "IPSP": max(c["IPSP_base"], c["IPSP_roll"])}
        best = max(four, key=four.get)
        thr = 0.89 if best == "IPSP" else 0.80
        label = best if four[best] > thr else None
        delay = np.nan
        if best == "EPSP":
            delay = round((345 + pk) / 2) if c["EPSP_base"] >= c["EPSP_roll"] else p
        elif best == "IPSP":
            delay = round((345 + tr) / 2) if c["IPSP_base"] >= c["IPSP_roll"] else q
        elif best == "AP+EP":
            delay = p
        rows.append(dict(label=label, best=best, pcc=four[best], delay=delay, peak=pk, trough=tr, **four))
    return pd.DataFrame(rows)


def null_stas(x, t0, t1, n_win):
    """구간 [t0, t1)분에서 무작위 시점 n_win개씩 N_STA번 → (STA 배열, 사용된 창 수)."""
    lo, hi = int(t0 * 60 * FS) + PRE, int(t1 * 60 * FS) - L
    out, used = np.empty((N_STA, L), np.float32), np.empty(N_STA, int)
    idx = np.arange(L) - PRE
    for k in range(N_STA):
        w = x[RNG.integers(lo, hi, n_win)[:, None] + idx]
        m = w.mean(1, keepdims=True)
        ok = (w.max(1) < m[:, 0] + 1.0) & (w.min(1) > m[:, 0] - 0.25) & (np.ptp(w[:, :PRE], 1) < 0.4)
        used[k] = ok.sum()
        out[k] = (w[ok].sum(0) + 1e-3) / (ok.sum() + 1e-3)
    return out, used


def main():
    res = []
    for n_win in (500, 100):
        for i in range(1, 5):
            x = load_trace(i)
            for name, (t0, t1) in PERIODS.items():
                stas, used = null_stas(x, t0, t1, n_win)
                d = judge_rows(stas)
                d["trace"], d["period"], d["n_win"], d["used"] = i, name, n_win, used
                res.append(d)
                e = d[d.label == "EPSP"]
                print(f"창{n_win} trace{i} {name}: 사용 창 중앙 {np.median(used):.0f}, "
                      f"EPSP 통과 {len(e)}/{N_STA}, 그중 지연 460~469 {((e.delay >= 460) & (e.delay <= 469)).mean():.1%}, "
                      f"IPSP 통과 {(d.label == 'IPSP').sum()}", flush=True)
    df = pd.concat(res, ignore_index=True)
    df.to_csv(HERE / "null_sta.csv", index=False)

    print("\n=== 판정 (창 500개, 전부 합침) ===")
    for n_win in (500, 100):
        e = df[(df.n_win == n_win) & (df.label == "EPSP")]
        frac = ((e.delay >= 460) & (e.delay <= 469)).mean()
        print(f"창 {n_win}: EPSP 통과 {len(e)}/{(df.n_win == n_win).sum()} ({len(e) / (df.n_win == n_win).sum():.1%}), "
              f"지연 460~469 비율 {frac:.1%} = 균등 4.4%의 {frac / (10 / 229):.1f}배")


if __name__ == "__main__":
    main()
