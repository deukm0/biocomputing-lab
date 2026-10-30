"""STA 판정용 템플릿. 논문 코드 CNEALib_Mapping.py의 함수를 그대로 옮겼다.

템플릿 = [평평한 앞부분(pre)] + [올라가는 부분(rise)] + [지수 감쇠(decay)], 길이 705샘플.
"""
import numpy as np


def template_ap(width_total=705, width_pre=35, width_rise=200, rise_factor=3,
                decay_factor=100, offset=0):
    """원본 Template_AP: 세제곱 곡선으로 오르고 지수로 감쇠."""
    t_decay = np.arange(0, width_total - width_pre - width_rise)
    template_decay = np.exp(-1 * t_decay / decay_factor)
    t_pre = np.linspace(0, (1 - offset) ** (1 / rise_factor), width_rise)
    template_rise = t_pre**3 + offset
    template_pre = np.zeros(width_pre) + offset
    return np.concatenate([template_pre, template_rise, template_decay])


def template_psp(width_total=705, width_pre=235, width_rise=110, decay_factor=200,
                 offset=0.25):
    """원본 Template_PSP: 사인 곡선 1/4로 오르고 지수로 감쇠."""
    t_decay = np.arange(0, width_total - width_pre - width_rise)
    template_decay = np.exp(-1 * t_decay / decay_factor)
    t = np.linspace(0, 1, width_rise)
    template_rise = offset + np.sin(t * np.pi / 2) * (1 - offset)
    template_pre = np.zeros(width_pre) + offset
    return np.concatenate([template_pre, template_rise, template_decay])


def base_templates() -> dict[str, np.ndarray]:
    """판정 코드(CNEALib_Mapping.py 2404~2406행)가 쓰는 기본 템플릿."""
    epsp = template_psp(width_pre=235, width_rise=110, decay_factor=250, offset=0.25)
    return {
        "AP": template_ap(width_pre=35, width_rise=200, rise_factor=3, decay_factor=100, offset=0),
        "EPSP": epsp,
        "IPSP": 1 - epsp,
    }


def ap_epsp_template(peak: int) -> np.ndarray:
    """AP+EPSP 템플릿. 코드에 기본형이 없고, STA 피크 위치(peak)에 맞춰 매번 만든다 (2559행)."""
    return template_psp(width_pre=peak - 40, width_rise=40, decay_factor=90, offset=0.15)
