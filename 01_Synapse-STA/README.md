# 실험 1: 시냅스 연결 판정 재현 (STA 템플릿 매칭)

하버드 iMEA 논문(Wang et al., *Nat. Biomed. Eng.* 2025)이 4,096개 전극의 세포 내 기록에서 시냅스 연결 71,127개를 판정한 방법을 공개 데이터로 다시 해 본다.

## 질문

처음 해 보는 생물 분야를 논문 재현으로 이해하고, 공개 데이터로 직접 구현한 뒤, 그 방법에 틈이나 개선점이 있는지 찾는다. 판정 기준은 실험 전에 [BRIEF.md](BRIEF.md)에 적어 두었다.

## 방법

출발 뉴런이 스파이크를 칠 때마다 도착 뉴런의 전압을 75ms씩(스파이크 전 25ms + 후 50ms) 잘라 평균(STA)을 내고, 연결 종류별 템플릿 4개(EPSP, IPSP, AP, AP+EPSP)와 피어슨 상관계수로 비교한다. 설정값은 [METHOD.md](METHOD.md).

## 결과

_(M2~M4 후 작성)_

## 한계와 다음 질문

_(정리 단계에서 작성)_

## 실행

```bash
~/.venvs/biocomp/bin/python 01_Synapse-STA/session0/averaging_demo.py
~/.venvs/biocomp/bin/python 01_Synapse-STA/session0/raw_signal.py EPSP
~/.venvs/biocomp/bin/python 01_Synapse-STA/session0/snr_explained.py

# 공통 코드 테스트
cd common && ~/.venvs/biocomp/bin/python test_data.py && cd ..

# M1 템플릿 재생성
~/.venvs/biocomp/bin/python 01_Synapse-STA/m1/compare_templates.py

# M2 판정 재현
~/.venvs/biocomp/bin/python 01_Synapse-STA/m2/ap_peak_hist.py
~/.venvs/biocomp/bin/python 01_Synapse-STA/m2/judge_fig4c.py
~/.venvs/biocomp/bin/python 01_Synapse-STA/m2/threshold_curve.py
```

## 문서

[BRIEF.md](BRIEF.md) · [STATE.md](STATE.md) · [BACKLOG.md](BACKLOG.md) · [WORKLOG.md](WORKLOG.md) · [CONCEPTS.md](CONCEPTS.md) · [METHOD.md](METHOD.md) · [FIGURES.md](FIGURES.md) (그림과 설명)
