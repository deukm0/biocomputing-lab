# biocomputing-lab

공개 데이터로 하는 바이오컴퓨팅 개인 실험. 살아있는 뉴런이 계산을 하려면 무엇을 알아야 하는지, 노트북만으로 하나씩 확인한다.

## 실험

| 폴더 | 질문 | 상태 |
|---|---|---|
| [01_Synapse-STA](01_Synapse-STA/) | 세포 내 기록에서 시냅스 연결을 어떻게 판정하나? (하버드 iMEA 논문 STA 템플릿 매칭 재현) | 완료 (2026-11-12) |

## 실행

```bash
python3 -m venv ~/.venvs/biocomp
~/.venvs/biocomp/bin/pip install -r requirements.txt
```

데이터는 [DATA.md](DATA.md)를 보고 받아 `dataverse_files/`에 두거나 `BIOCOMP_DATA_DIR`로 경로를 지정한다.

## 문서

- [DATA.md](DATA.md): 데이터 출처·라이선스·형식
- 각 실험 폴더: `README.md`(질문 → 방법 → 결과 → 한계), `BRIEF.md`(실험 전에 정한 가설·판정 기준), `WORKLOG.md`(실험 일지), `CONCEPTS.md`(개념 노트)
