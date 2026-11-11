"""논문 코드의 스파이크 검출과 STA를 Fig4d(이미 mV 단위)에 맞게 옮긴 것.

원본: external/CNEA_Intracellular_Shared/CNEALib_Mapping.py
  - Spike_Index_Gen_Intra_v2 (1060~1228행)
  - Generate_STA_Intra_PSP  (1647~1768행)
원본은 원시 값(V, 이득 30)을 받아 -1을 곱하고 /30*1000으로 mV로 바꾼다.
Fig4d는 이미 부호가 바로잡힌 mV라서 그 두 단계만 뺐다. 임계값도 mV로 환산:
  amp_limit 30e-3 → 1.0 mV, amp_limit_pre 6e-3 → 0.2 mV (전 구간 진폭 한계는 그 2배 = 0.4 mV)

주의: Fig4d는 10샘플 이동평균으로 다듬은 신호다 (스펙트럼에 941.5 Hz = 9415/10 배수에서
골이 있음. 논문 그림 코드의 Moving_Average(…, 10)과 일치). 그래서 2차 차분이 원신호보다 훨씬 작아
'앰프 멈춤' 검사(2차 차분 표준편차 < 0.013)에 전부 걸린다. Fig4d에서는 skip_stuck=True로 끈다.
기울기 규칙(0.28, 0.15)도 원신호 기준이라, 다듬어진 신호에서는 더 느슨하게 작동한다.
"""
import math

import numpy as np

FS = 1205120 / 128
WIN = int(0.2 * FS)          # 1883
BIG = int(20 * FS)           # 20초 큰 창
STA_LEN, PRE = 705, 705 // 3  # 705, 235


def moving_average(x, w=2000):
    """원본 Moving_Average와 같은 방식(양 끝을 신호 일부로 덧대기)."""
    return np.convolve(np.concatenate((x[: w // 2], x, x[-w + w // 2 + 1:])),
                       np.ones(w), "valid") / w


def detect(sig_mV, threshold=0.3, skip_stuck=False):
    """칸마다 규칙을 통과한 스파이크 위치(샘플 번호)와 칸별 판정 기록을 돌려준다."""
    x = sig_mV - moving_average(sig_mV)
    spikes, log = [], []
    for s0 in range(0, len(x), BIG):
        data = x[s0:s0 + BIG]
        n = len(data)

        # 앰프 멈춤 검사: 1/10칸(188샘플)마다 2차 차분의 표준편차
        cj = np.copy(data)
        cj.resize((math.ceil(n / (WIN / 10)), int(WIN / 10)))
        if not skip_stuck and np.min(np.std(np.diff(cj, n=2, axis=1), axis=1)) < 0.013:
            log.append(("big", s0, "앰프 멈춤으로 건너뜀"))
            continue

        nw = math.ceil(n / WIN)
        d = np.copy(data)
        d.resize((nw, WIN))   # 모자란 끝은 0으로 채움 (원본과 동일)
        mean, mx, mn = d.mean(1), d.max(1), d.min(1)
        k = d.argmax(1)
        not_edge = (k > 15) & (WIN - k > 15)
        height = mx > mean + threshold
        shape = (np.abs(mn) < 0.6 * np.abs(mx)) & (mn < 0) & (mx > 0)
        pos = height & shape & not_edge

        dd = np.diff(d, axis=1)
        d2 = np.diff(dd, axis=1)
        dmax, dmin = dd.max(1), dd.min(1)
        slow = (np.abs(dmax) < 0.28) & (np.abs(dmin) < 0.15)
        big = ((np.abs(dmin) < 0.35 * np.abs(dmax)) & (np.abs(d2.max(1)) < 0.35 * np.abs(dmax))
               & (np.abs(d2.min(1)) < 0.35 * np.abs(dmax)))
        if not np.any(np.abs(dmax) > 0.28):
            big = np.zeros(nw, bool)
        final = (pos & slow) | big if pos.any() else pos

        for i in range(nw):
            log.append(dict(win=i, peak=s0 + i * WIN + k[i], height=bool(height[i]),
                            shape=bool(shape[i]), not_edge=bool(not_edge[i]),
                            slow=bool(slow[i]), big=bool(big[i]), final=bool(final[i]),
                            edge_dist=int(min(k[i], WIN - k[i])), amp=float(mx[i])))
        if final.sum() > 3:
            spikes += [s0 + i * WIN + k[i] for i in np.where(final)[0]]
        else:
            log.append(("big", s0, f"스파이크 {final.sum()}개뿐이라 버림"))
    return np.array(spikes, int), log, x


def sta(post_mV, spikes, amp=1.0, amp_pre=0.2):
    """창마다 제외 규칙을 적용해 평균. 각 창의 판정 이유도 돌려준다.
    원본은 DC_flatten=False가 기본이라 Post는 기준선을 빼지 않고 쓴다."""
    acc, n, reasons = np.zeros(STA_LEN), 0, []
    for p in spikes:
        w = post_mV[p - PRE:p + STA_LEN - PRE]
        if p - PRE < 0 or len(w) != STA_LEN:
            reasons.append("창이 신호 밖")
            continue
        m = w.mean()
        why = []
        if w.max() >= m + amp:
            why.append(f"위로 +{w.max() - m:.2f}")
        if w.min() <= m - amp / 4:
            why.append(f"아래로 -{m - w.min():.2f}")
        if np.ptp(w[:PRE]) >= amp_pre * 2:
            why.append(f"앞부분 흔들림 {np.ptp(w[:PRE]):.2f}")
        if why:
            reasons.append(", ".join(why))
        else:
            acc += w
            n += 1
            reasons.append("사용")
    avg = (acc + 1e-3) / (n + 1e-3)  # 원본처럼 0/0 방지. n=0이면 전부 1.0
    return avg, n, reasons
