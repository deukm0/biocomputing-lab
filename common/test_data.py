"""로더 테스트. 실행: ~/.venvs/biocomp/bin/python common/test_data.py"""
import numpy as np

from data import (FIG4D_SHEETS, STA_LEN, TEMPLATE_NAMES, load_fig4c, load_fig4d,
                  load_fig4g, load_templates, pixel_rc)


def test_templates():
    t = load_templates()
    assert tuple(t) == TEMPLATE_NAMES
    for v in t.values():
        assert v.shape == (STA_LEN,) and np.isfinite(v).all()


def test_fig4c():
    sta = load_fig4c()
    assert sta.shape == (64 * 64, STA_LEN) and np.isfinite(sta).all()


def test_fig4d():
    for sheet in FIG4D_SHEETS:
        pre, post = load_fig4d(sheet)
        assert pre.shape == post.shape and len(pre) > 0


def test_fig4g():
    g = load_fig4g()
    assert len(g) == 71127
    counts = g["type"].value_counts().to_dict()
    assert counts == {1: 63574, 0.5: 4065, 0: 3008, -1: 480}  # DATA.md, 논문과 같음


def test_pixel_rc():
    assert pixel_rc(5258) == (52, 58)
    assert pixel_rc(101) == (1, 1)


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print(f"통과: {name}")
