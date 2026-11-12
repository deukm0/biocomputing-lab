"""ED_FIG6a 원신호 로더. 텍스트(약 500MB)를 처음 한 번 읽어 .npy로 캐시한다."""
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "common"))
from data import data_dir  # noqa: E402

FS = 1205120 / 128
CACHE = Path(os.environ.get("BIOCOMP_CACHE", Path(__file__).resolve().parent / ".cache"))


def load_trace(i: int) -> np.ndarray:
    CACHE.mkdir(exist_ok=True)
    npy = CACHE / f"ED_FIG6a_trace{i}.npy"
    if not npy.exists():
        x = pd.read_csv(data_dir() / f"ED_FIG6a_trace{i}.txt", header=None,
                        engine="c", dtype=np.float32)[0].to_numpy()
        np.save(npy, x)
    return np.load(npy)
