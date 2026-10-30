"""공개 데이터(Harvard Dataverse, doi:10.7910/DVN/S4B1ES) 로더.

데이터 위치: 환경변수 BIOCOMP_DATA_DIR, 없으면 <저장소>/dataverse_files.
파일별 구조는 DATA.md 참고.
"""
import os
from pathlib import Path

import numpy as np
import pandas as pd

FS = 1205120 / 128  # 샘플링 주파수 (Hz), 논문 코드 F_sample
STA_LEN = 705       # STA 창 길이 (샘플)
FIG4D_SHEETS = ("AP", "AP_EPSP", "EPSP", "IPSP")
TEMPLATE_NAMES = ("AP", "AP+EP", "EPSP", "IPSP")


def data_dir() -> Path:
    env = os.environ.get("BIOCOMP_DATA_DIR")
    path = Path(env) if env else Path(__file__).resolve().parents[1] / "dataverse_files"
    if not path.is_dir():
        raise FileNotFoundError(f"데이터 폴더가 없다: {path} (BIOCOMP_DATA_DIR 확인)")
    return path


def load_templates() -> dict[str, np.ndarray]:
    """Fig4a 템플릿 4개. {이름: 705샘플 배열}"""
    df = pd.read_excel(data_dir() / "Fig4a_templates.xlsx")
    return {name: df[name].to_numpy(dtype=float) for name in TEMPLATE_NAMES}


def load_fig4c() -> np.ndarray:
    """출발 픽셀 하나 기준, 도착 픽셀 4,096개의 STA. shape (4096, 705)"""
    return pd.read_excel(data_dir() / "Fig4c.xlsx", header=None).to_numpy(dtype=float)


def load_fig4d(sheet: str) -> tuple[np.ndarray, np.ndarray]:
    """연결 종류별 쌍 하나의 원신호. (pre, post)"""
    if sheet not in FIG4D_SHEETS:
        raise ValueError(f"시트는 {FIG4D_SHEETS} 중 하나: {sheet}")
    df = pd.read_excel(data_dir() / "Fig4d.xlsx", sheet_name=sheet)
    return df["Pre"].to_numpy(dtype=float), df["Post"].to_numpy(dtype=float)


def load_fig4g() -> pd.DataFrame:
    """최종 연결 목록 71,127행. 종류: 1=EPSP, 0.5=AP+EPSP, 0=AP, -1=IPSP"""
    return pd.read_excel(
        data_dir() / "Fig4g.xlsx", header=None,
        names=["pre", "post", "corr", "type", "peak"],
    )


def pixel_rc(pixel: int) -> tuple[int, int]:
    """픽셀 번호 → (행, 열). 번호 = 행×100 + 열, 1부터. 예: 5258 → (52, 58)"""
    return pixel // 100, pixel % 100
