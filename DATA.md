# 데이터

## 출처

| 항목 | 내용 |
|---|---|
| 데이터셋 | Synaptic-connectivity mapping amongst thousands of neurons via parallelized intracellular recording with a microhole electrode array |
| 위치 | Harvard Dataverse, [doi:10.7910/DVN/S4B1ES](https://doi.org/10.7910/DVN/S4B1ES) (버전 6.1, 공개 2025-01-26) |
| 논문 | Wang et al., *Nat. Biomed. Eng.* 2025 (함돈희 랩), [doi:10.1038/s41551-025-01352-5](https://doi.org/10.1038/s41551-025-01352-5) |
| 분석 코드 원본 | [JunWISN/CNEA_Intracellular_Shared](https://github.com/JunWISN/CNEA_Intracellular_Shared) (`CNEALib_Mapping.py`). 로컬 클론: `external/CNEA_Intracellular_Shared` (커밋 안 함) |
| 라이선스 | **CC0 1.0** (Dataverse API로 확인, 2026-10-29) |
| 받은 날짜 | 2026-10-27, 34개 파일, 약 8.7GB |

## 위치와 설정

원본은 `dataverse_files/`에 두고 **커밋하지 않는다.** 다른 곳에 두면 환경변수로 알려준다. 읽을 때는 `common/data.py`의 로더를 쓴다.

```bash
export BIOCOMP_DATA_DIR=/path/to/dataverse_files
```

## 실험 1에서 쓰는 파일

| 파일 | 구조 |
|---|---|
| `Fig4a_templates.xlsx` | 헤더 `AP, AP+EP, EPSP, IPSP`, 705샘플 × 4 (템플릿) |
| `Fig4c.xlsx` | 4,096 × 705. **출발 픽셀 5106**(SI Fig 11) 기준, 도착 픽셀 4,096개 각각의 STA (행 우선, 5106 자신 포함). 값이 -22 근처라 DC 오프셋이 있다. 5106은 Fig4f·Fig4g에 없다 |
| `Fig4d.xlsx` | 시트 `AP`, `AP_EPSP`, `EPSP`, `IPSP`, 열 `Pre`, `Post`. 종류별 연결 쌍 하나의 원신호 5~8초. 평균 0 근처, 스파이크가 위쪽(부호 반전 이미 적용된 것으로 보임) |
| `Fig4g.xlsx` | 최종 연결 71,127행: 출발 픽셀, 도착 픽셀, 상관계수, 종류(1=EPSP, 0.5=AP+EPSP, 0=AP/전기 시냅스, -1=IPSP), 피크 위치(샘플) |
| `Fig4b_Actual_STA.txt`, `Fig4b_Cross-dish_STA_10_groups.txt` | 상관계수 값만 (파형 아님). 실제 vs 다른 접시 대조군. Actual = 가장 활발한 출발 1,000개 × 4,096, EPSP 템플릿 |
| `ED_FIG2b.txt` | 위와 같은 4,096,000쌍의 4개 템플릿 PCC (열 AP, APEP, EPSP, IPSP) |
| `Fig4e.xlsx`, `ED_FIG4.xlsx`, `Fig4f.xlsx` | 20분 구간 지도 6장·4장(4열, 피크 없음), 정제 전 합친 지도 72,887행 |
| Supplementary Information (Nature, 수동 다운로드) | `01_Synapse-STA/41551_2025_1352_MOESM1_ESM.pdf`. SI Fig 11 = Fig4c의 판정 라벨. 커밋 안 함 |

- 픽셀 번호 = 행×100 + 열 (1부터, 예: 5258 = 52행 58열). 칩 64×64, 픽셀 간격 20μm.
- 종류별 개수: EPSP 63,574 / AP+EPSP 4,065 / AP 3,008 / IPSP 480 (논문과 일치).

## 주의사항

- 원시 신호에 샘플마다 약 0.0325 단위의 계단형 디지털 잡음이 있다. 창 9 미디안 필터로 제거된다(ED_FIG6a에서 확인).
- Dataverse 파일이 원시 값인지 mV 변환 값인지는 아직 확인하지 않았다 (`01_Synapse-STA/METHOD.md` 참고).
