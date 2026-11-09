# 데이터

이 폴더의 데이터 파일과 출처를 정리한다. 정규시즌 기록은 Kaggle 데이터셋에서 받았고, 정규시즌 기록에 없는 포스트시즌 사실은 언론 기사에서 모았다.

## raw: Kaggle 원본

2026-11-09에 `kagglehub`로 받았다.

| 파일 | 출처 | 범위 | 라이선스 | 용도 |
|---|---|---|---|---|
| `kbo_batting_stats_season_1982-2026.csv` | [KBO Player Stats 1982–2026](https://www.kaggle.com/datasets/netsong/kbo-player-stats-19822025) (netsong, version 7, 2026-10-13 갱신). 원 출처는 [KBO 기록실](https://www.koreabaseball.com) | 1982~2026, 선수 × 시즌, 정규시즌 타격 | CC BY-NC-SA 4.0 | 메인 |
| `kbo_pitching_stats_season_1982-2026.csv` | 위와 같음 | 1982~2026, 선수 × 시즌, 정규시즌 투구 | CC BY-NC-SA 4.0 | 메인 |
| `kbobattingdata.csv` | [KBO Batting Data 1982–2021](https://www.kaggle.com/datasets/mattop/baseball-kbo-batting-data-1982-2021) (mattop) | 1982~2021, 팀 × 시즌 타격 | CC0 | 검산 |
| `kbopitchingdata.csv` | [Korean Baseball Pitching Data 1982–2021](https://www.kaggle.com/datasets/mattop/korean-baseball-pitching-data-1982-2021) (mattop) | 1982~2021, 팀 × 시즌 투구 | CC0 | 검산 |

netsong 원본에는 KBO 기록실에 공개된 선수 정보(생년월일, 키 · 몸무게, 출신 학교, 드래프트)가 들어 있다. 페이지에는 이 중 나이와 드래프트에서 추정한 입단 경로만 쓴다.

## clean: 집계 결과

`scripts/clean.py`가 `raw/`의 netsong 원본으로 만든다. 집계 방식과 검산 결과는 [METHODS.md](METHODS.md)에 있다.

| 파일 | 내용 |
|---|---|
| `team_season.csv` | 팀 × 시즌 집계. 승패, 득실점, 팀 타격 · 투구 지표, 리그 평균 대비 지표(`R_plus`, `ERA_plus`), 순위 |
| `samsung_batters.csv` | 삼성 타자 × 시즌. 삼성에 온 경로(`origin`) 포함 |
| `samsung_pitchers.csv` | 삼성 투수 × 시즌. 삼성에 온 경로(`origin`) 포함 |

## external: 언론 기사에서 모은 값

각 행의 `source` 칸에 출처 기사 링크를 함께 적었다.

### `samsung_korean_series.csv`

삼성의 한국시리즈 결과, 2021년 1위 결정전, 2026년 포스트시즌 슬로건을 담는다.

| 내용 | 출처 |
|---|---|
| 한국시리즈 우승 연도 1985(전후기 통합우승), 2002, 2005, 2006, 2011~2014 | [경북매일, 2014-11-12](https://kbmaeil.com/article/201411120114505) |
| 2021 1위 결정전 KT전 0-1 패배 | [스포츠경향](https://sports.khan.co.kr/article/202605181538003) |
| 2024 한국시리즈 준우승(KIA전 1승 4패) | [전북일보, 2024-10-29](https://www.jjan.kr/articleAmp/20241029580003) |
| 2026 한국시리즈 우승(KT전 4승 1패, 5차전 12-1, 대구 삼성라이온즈파크), MVP 구자욱 기록 | [머니투데이, 2026-11-08](https://www.mt.co.kr/sports/2026/11/08/2026110817592781571) |
| 2026 포스트시즌 슬로건 VAMOS | [머니투데이, 2026-10-26](https://www.mt.co.kr/sports/2026/10/26/2026102618275730894) |

### `ks2026_g5_linescore.csv`

2026 한국시리즈 5차전 삼성의 이닝별 득점이다. 메인 페이지 위 전광판에 쓴다.

| 이닝 | 득점 | 출처 |
|---|---|---|
| 3회 | 3 | [미디어펜](https://www.mediapen.com/news/view/1136064) |
| 5회 | 8 | [재경일보](https://news.jkn.co.kr/post/1078306) |
| 8회 | 1 | [경북매일, 2026-11-08](https://www.kbmaeil.com/article/20261108500566) |

1, 2, 4, 6, 7회의 0은 기사에 적혀 있지 않다. 이닝 합계가 최종 점수 12와 맞는다는 점으로 추론했다. 9회말은 홈팀 삼성이 앞서 있어 열리지 않았으므로 `X`로 적었다. 메인 페이지는 이닝 합계가 최종 점수와 다르면 오류를 낸다.

### `rank_overrides.csv`

승률로 매긴 순위를 공식 순위로 바로잡는 값이다. 2021년 삼성과 KT는 76승 59패 9무로 동률이었고, 1위 결정전에서 KT가 1-0으로 이겨 KT가 1위, 삼성이 2위가 됐다. 출처는 [스포츠경향](https://sports.khan.co.kr/article/202605181538003)이다.

## 페이지에만 표기한 출처

[뉴시스, 2026-11-09](https://www.newsis.com/view/NISI20261109_0002286205)의 2026 한국시리즈 결과 그래픽 기사는 CSV에 넣은 값은 없고, 메인 페이지 맨 아래 출처에만 적었다.

## 라이선스

netsong 데이터가 CC BY-NC-SA 4.0이라 이 데이터로 만든 결과물은 비상업적으로만 쓰고, 출처를 표기하며, 같은 조건으로 공유한다. mattop 데이터는 CC0다. 기사에서 모은 값은 결과 숫자와 사실만 적었고 기사 문장은 옮기지 않았다.
