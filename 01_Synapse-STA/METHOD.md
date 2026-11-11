# 논문 코드에서 확인한 설정

출처: `CNEALib_Mapping.py` ([JunWISN/CNEA_Intracellular_Shared](https://github.com/JunWISN/CNEA_Intracellular_Shared)). 논문 본문과 다르면 **코드 기준**으로 맞춘다.

| 항목 | 값 | 메모 |
|---|---|---|
| 샘플링 | `F_sample = 1205120/128` ≈ 9,415 Hz | |
| STA 창 | 705샘플 (약 75ms) | 출발 스파이크 피크 기준 **앞 235샘플(약 25ms) + 뒤 470샘플**. 본문은 "50ms", Methods는 "25 ms before to 50 ms after" (코드와 같음) |
| 부호 | `Row_Data = -Row_Read(...)` | 신호를 뒤집어 읽는다 |
| 단위 | 원시 값 × 1000/30 = mV | 30은 증폭기 이득. STA에 ×33.33. Dataverse 파일이 어느 쪽인지 **미확인** |
| 기준선 제거 (선택) | `DC_flatten`: 2,000샘플 이동평균을 뺀다 | |
| 창 제외 | `amp_limit`, `amp_limit_pre` | 도착 신호 창 안에 큰 스파이크가 있거나 피크 앞 235샘플이 크게 흔들리면 평균에서 뺀다 |
| 정규화 | `STA - min(STA)` 후 최대값으로 나눔 → 0~1 | 템플릿 비교 전 |
| **템플릿 (기본)** | AP `Template_AP(pre=35, rise=200, τ=100)` → 최대 234번(0ms). EPSP `Template_PSP(pre=235, rise=110, τ=250, offset=0.25)` → 최대 344번. IPSP = 1 − EPSP | 2404~2406행. decay 길이 = 705 − pre − rise. **Fig4a의 AP는 (pre=150, rise=120, τ=80)으로 코드와 다름** (세션 2) |
| **템플릿 정렬** | EPSP·AP+EP: STA 최대가 240~470번이면 그 위치로 옮김, 아니면 355번. IPSP: STA 최소가 350~470번이면 그 위치, 아니면 410번. EPSP·IPSP는 기본·이동 중 큰 상관, AP+EP는 이동 버전만, **AP는 이동 없음** | 2557~2627행. AP+EP = `Template_PSP(pre=peak−40, rise=40, τ=90, offset=0.15)`. 빼면 상관계수가 크게 낮아진다 (정렬 없이 Fig4c 계산 시 0.8 초과 21개뿐) |
| 지연 | ≈ (피크 − 235) / F_sample | `Fig4g` 다섯째 열이 이 피크 위치로 보임 |
| 판정 규칙 | 4개 PCC(AP 고정, AP+EP 이동, EPSP·IPSP 기본/이동 중 큰 값) 중 **최대**를 고르고, 그 템플릿의 임계값을 넘으면 그 종류. 자기 자신은 제외 | 2633~2672행. `common/judge.py` |
| 판정 임계값 | EPSP·AP·AP+EPSP 0.80, IPSP 0.89 | 0.89는 공개 코드에 없고 **SI Fig 11 설명**에 있음. 코드 기본은 하나의 `corr_limit=0.8` |
| 거짓양성률 (논문) | EPSP 5.7 / AP 0.3 / AP+EPSP 1.3 / IPSP 9.5% | (다른 접시 PCC > θ 쌍 수) / (실제 접시 PCC > θ 쌍 수), 대조 접시 10개 평균. 실제 = SH4 활발한 출발 1,000 × 도착 4,096, 대조 = 같은 출발 × 다른 칩 4,096. Methods·Extended Data Fig 2. 공개 PCC로 640칸 재현 (세션 5) |
| 녹화 분할 | 100분 녹화 → 20분 구간 81개(1분씩 겹침)로 판정 후 합침 | |

## 확인된 사실 (세션 3)

- Fig4c.xlsx의 출발 픽셀 = **5106** (SI Fig 11 제목). 5106은 Fig4f·Fig4g·구간별 지도 어디에도 없다.
- 실제 판정에 쓴 AP 템플릿 = 코드 값(0ms). 근거: Fig4g AP 쌍 피크 중앙 235, SI Fig 11 라벨을 코드 AP로 23/23 재현(그림 AP는 정밀도 92%).
