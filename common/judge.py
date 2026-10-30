"""STA 하나를 템플릿 4개와 비교해 연결 종류를 판정한다.

논문 코드 CNEALib_Mapping.py 2533~2672행(Relation_Define_STA_v5)을 옮겼다.
임계값은 SI Fig 11 설명을 따른다: 최대 PCC를 낸 템플릿이 AP·AP+EP·EPSP면 0.80, IPSP면 0.89.
"""
import numpy as np

from templates import ap_epsp_template, base_templates, template_psp

TYPES = ("AP", "AP+EP", "EPSP", "IPSP")
THRESHOLDS = {"AP": 0.80, "AP+EP": 0.80, "EPSP": 0.80, "IPSP": 0.89}


def _pcc(a, b):
    return float(np.corrcoef(a, b)[0, 1])


def correlations(sta, ap_template=None, align=True) -> dict[str, float]:
    """STA와 템플릿 4개의 피어슨 상관. align=False면 템플릿을 옮기지 않는다(비교용)."""
    base = base_templates()
    ap = base["AP"] if ap_template is None else ap_template

    x = sta - sta.min()  # 0~1 정규화
    if x.max() != 0:
        x = x / x.max()
    peak, trough = int(x.argmax()), int(x.argmin())

    # EPSP·AP+EP: STA 최대 위치로 옮김 (범위 밖이면 355)
    p = peak if (align and 240 < peak < 470) else 355
    epsp_roll = template_psp(width_pre=p - 110, width_rise=110, decay_factor=250, offset=0.25)
    # IPSP: STA 최소 위치로 옮김 (범위 밖이면 410)
    q = trough if (align and 350 < trough < 470) else 410
    ipsp_roll = 1 - template_psp(width_pre=q - 110, width_rise=110, decay_factor=250, offset=0.25)

    return {
        "AP": _pcc(x, ap),                      # AP는 옮기지 않는다
        "AP+EP": _pcc(x, ap_epsp_template(p)),  # AP+EP는 옮긴 버전만
        "EPSP": max(_pcc(x, base["EPSP"]), _pcc(x, epsp_roll)) if align else _pcc(x, base["EPSP"]),
        "IPSP": max(_pcc(x, base["IPSP"]), _pcc(x, ipsp_roll)) if align else _pcc(x, base["IPSP"]),
    }


def judge(sta, ap_template=None, align=True, thresholds=THRESHOLDS) -> tuple[str | None, float, dict]:
    """(판정 종류 또는 None, 최대 PCC, 4개 PCC)"""
    c = correlations(sta, ap_template, align)
    best = max(c, key=c.get)
    label = best if c[best] > thresholds[best] else None
    return label, c[best], c
