"""M3-4: 판정 실패 진단. 상관값이 우연 범위인지, IPSP 반응이 언제 오는지 확인한다.

① 무작위 시점 대조군: Pre 스파이크와 무관한 시점을 같은 개수만큼 골라 STA → 판정 상관 (500번)
② IPSP 쌍의 시간대별 Post 변화 (창마다 앞부분 평균을 뺌)
③ [내 아이디어에서 나온 검사] IPSP 템플릿을 정렬 범위(12~25ms) 밖으로도 옮기면? 같은 자유도를 준 무작위 대조군과 비교
결과를 보고 나서 정한 검사다(쌍 하나). 가설로만 쓴다.
실행: ~/.venvs/biocomp/bin/python 01_Synapse-STA/m3/sta_null_check.py
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "common"), str(Path(__file__).resolve().parent)]
from common.data import load_fig4d  # noqa: E402
from judge import judge  # noqa: E402
from templates import template_psp  # noqa: E402
from detect import FS, PRE, STA_LEN, detect, sta  # noqa: E402

rng = np.random.default_rng(0)
ms = lambda s: s / FS * 1000  # noqa: E731


def windows(post, ps):
    return np.array([post[p - PRE:p - PRE + STA_LEN] for p in ps])


def random_times(post, n):
    return rng.integers(PRE, len(post) - STA_LEN + PRE, n)


def used_spikes(post, spikes):
    _, _, why = sta(post, spikes)
    return [p for p, w in zip(spikes, why) if w == "사용"]


print("① 무작위 시점 대조군")
for sheet, key, real_only in [("EPSP", "EPSP", False), ("EPSP", "EPSP", True), ("IPSP", "IPSP", False)]:
    pre, post = load_fig4d(sheet)
    spikes, _, pre_c = detect(pre, skip_stuck=True)
    if real_only:
        spikes = [p for p in spikes if pre_c[p] >= 1.0]
    used = used_spikes(post, spikes)
    real = judge(windows(post, used).mean(0))[2][key]
    null = np.array([judge(windows(post, random_times(post, len(used))).mean(0))[2][key]
                     for _ in range(500)])
    tag = f"{sheet}{' (진짜만)' if real_only else ''}"
    print(f"  {tag:12s} 창 {len(used):2d}: 실제 {real:+.3f} / 무작위 중앙 {np.median(null):+.3f}, "
          f"상위 5% {np.percentile(null, 95):+.3f}, 실제 이상 비율 {np.mean(null >= real):.2f}")

print("\n② IPSP 시간대별 Post 변화 (앞부분 평균 대비)")
pre, post = load_fig4d("IPSP")
spikes, _, _ = detect(pre, skip_stuck=True)
used = used_spikes(post, spikes)
W = windows(post, used)
base = W[:, :PRE].mean(1)
for lo, hi in [(0, 10), (10, 20), (20, 30), (30, 50)]:
    r = W[:, PRE + int(lo * FS / 1000):PRE + int(hi * FS / 1000)].mean(1) - base
    print(f"  {lo:2d}-{hi:2d}ms: 평균 {r.mean():+.4f} mV, 내려간 창 {np.sum(r < 0)}/{len(r)}")


def late(ps):
    X = windows(post, ps)
    return (X[:, PRE + int(30 * FS / 1000):].mean(1) - X[:, :PRE].mean(1)).mean()


null = np.array([late(random_times(post, len(used))) for _ in range(2000)])
print(f"  30-50ms 하강이 무작위로 나올 비율: {np.mean(null <= late(used)):.3f}")

print("\n③ IPSP 템플릿을 늦게 옮기면")
avg = W.mean(0)
x = (avg - avg.min()) / (avg.max() - avg.min())
print(f"  STA 최저점: {ms(np.argmin(avg[PRE:])):.1f}ms (코드 정렬 허용 {ms(350 - PRE):.1f}~{ms(470 - PRE):.1f}ms)")
ipsp = lambda q: 1 - template_psp(width_pre=q - 110, width_rise=110, decay_factor=250, offset=0.25)  # noqa: E731
for q in [410, 470, 550, 600, 650, 704]:
    print(f"  골 {ms(q - PRE):5.1f}ms: 상관 {np.corrcoef(x, ipsp(q))[0, 1]:+.3f}")
T = [ipsp(q) for q in range(350, 705, 5)]


def best(a):
    y = (a - a.min()) / (a.max() - a.min())
    return max(np.corrcoef(y, t)[0, 1] for t in T)


null = np.array([best(windows(post, random_times(post, len(used))).mean(0)) for _ in range(500)])
print(f"  12~50ms 어디든 허용: 실제 {best(avg):.3f} / 무작위 중앙 {np.median(null):.3f}, "
      f"상위 5% {np.percentile(null, 95):.3f}, 0.89 넘는 무작위 비율 {np.mean(null > 0.89):.2f}")
