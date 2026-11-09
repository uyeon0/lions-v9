# 다시, 정상

삼성 라이온즈가 2014년 한국시리즈 우승 뒤 암흑기(2016~2023)를 지나 2026년 한국시리즈에서 다시 우승하기까지를 KBO 정규시즌 기록으로 보여 주는 Streamlit 페이지다. 이야기를 9이닝으로 나눈 메인 페이지와, 분석 페이지 4개("더 깊이 보기")로 이뤄져 있다. 삼성 라이온즈 구단과 무관하게 학습용으로 만들었다.

## 실행

```bash
pip install -r requirements.txt
streamlit run app.py
```

`data/clean/`이 레포에 들어 있어서 바로 실행된다. 원본에서 다시 만들려면 아래 순서로 실행한다.

```bash
python scripts/clean.py      # data/raw → data/clean
python scripts/verify.py     # 집계 결과를 공식 팀 기록과 비교 (선택)
```

`views/deep/fall.py`와 메인 페이지 2회는 이적 선수를 찾으려고 `data/raw/`의 원본도 읽는다.

## 파일 구조

```
.
├── app.py                  # st.navigation으로 페이지 목록 정의
├── core/
│   ├── data.py             # 데이터 불러오기, 구간(PHASES), 우승 시즌(CHAMPIONS), 선수 출신 집계
│   ├── theme.py            # 색, 차트 스타일
│   └── deep_ui.py          # 더 깊이 보기 공통 화면 (상단 바, 출처, 기록지 표)
├── views/
│   ├── main.py             # 메인 페이지 (9이닝 스크롤 페이지)
│   └── deep/               # 더 깊이 보기
│       ├── fall.py         # 어떻게 무너졌나
│       ├── key.py          # 탈출의 열쇠
│       ├── members.py      # 2026 멤버는 어디서 왔나
│       └── timemachine.py  # 타임머신
├── assets/
│   ├── main.css            # 메인 페이지 스타일
│   └── deep.css            # 더 깊이 보기 스타일
├── scripts/
│   ├── clean.py            # 선수 × 시즌 원본 → 팀 × 시즌 집계, 삼성 선수 표
│   └── verify.py           # 집계 결과를 공식 팀 기록과 비교
├── data/
│   ├── README.md           # 파일별 출처와 라이선스
│   ├── METHODS.md          # 집계 방식과 검산 결과
│   ├── raw/                # Kaggle 원본
│   ├── clean/              # scripts/clean.py가 만든 집계 결과
│   └── external/           # 언론 기사에서 모은 값
└── 작업노트.md              # 결정 기록과 진행 상황
```

## 데이터

정규시즌 숫자는 KBO 기록실 선수 기록을 모은 Kaggle 데이터셋 [KBO Player Stats 1982–2026](https://www.kaggle.com/datasets/netsong/kbo-player-stats-19822025)(netsong, CC BY-NC-SA 4.0)을 팀 단위로 합쳐 계산한다. 한국시리즈 결과, 5차전 이닝별 득점, 2021년 순위 정정, 포스트시즌 슬로건은 정규시즌 데이터에 없어서 언론 기사에서 따로 모았다.

- 파일별 출처 링크와 라이선스: [data/README.md](data/README.md)
- 집계 방식과 공식 기록 검산 결과: [data/METHODS.md](data/METHODS.md)

메인 데이터가 CC BY-NC-SA 4.0이라 이 프로젝트도 비상업적으로만 쓰고, 출처를 표기하며, 같은 조건으로 공유한다.

## 한계

- 원본은 정규시즌만 담는다. 한국시리즈 결과와 5차전 이닝별 득점은 기사에서 모은 값이고, 기사에 득점이 없는 이닝의 0은 합계로 추론했다.
- 주축 선수 이탈과 성적 하락이 같은 시기에 일어났다는 것을 보여 줄 뿐, 이탈이 원인이라고 단정하지 않는다.
- 왕조 · 암흑기 · 탈출 구간은 정규시즌 순위를 보고 직접 정했다.
