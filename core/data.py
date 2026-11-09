"""데이터: 파일 경로 · CSV 읽기(캐시) · 이야기 구간 · 외부 사실 · 선수 출신 집계"""
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "clean"
EXTERNAL = ROOT / "data" / "external"
RAW = ROOT / "data" / "raw"

# 이야기 구간 (정규시즌 순위 기준으로 나눔 — 작업노트 '결정 기록' 참고)
PHASES = [
    ("왕조", 2010, 2015, "#dde3ea"),   # 종이 위 옅은 블루
    ("암흑기", 2016, 2023, "#e6e0d0"),  # 종이보다 한 톤 어둡게
    ("탈출", 2024, 2026, "#f6e7a6"),    # 옅은 노랑
]


@st.cache_data
def load_team() -> pd.DataFrame:
    return pd.read_csv(DATA / "team_season.csv")


@st.cache_data
def load_samsung() -> pd.DataFrame:
    t = load_team()
    return t[t["Team"] == "삼성"].set_index("Season").sort_index()


@st.cache_data
def load_ks() -> pd.DataFrame:
    """한국시리즈 · 1위 결정전 · 슬로건 (정규시즌 데이터 밖 사실, 기사 출처 포함)"""
    k = pd.read_csv(EXTERNAL / "samsung_korean_series.csv", dtype=str, keep_default_na=False)  # ".500" 같은 표기를 그대로
    return k.assign(season=k.season.astype(int)).set_index("season")


@st.cache_data
def load_batters() -> pd.DataFrame:
    return pd.read_csv(DATA / "samsung_batters.csv")


@st.cache_data
def load_pitchers() -> pd.DataFrame:
    return pd.read_csv(DATA / "samsung_pitchers.csv")


def phase_of(year: int) -> str:
    for name, a, b, _ in PHASES:
        if a <= year <= b:
            return name
    return "-"


# 데이터(정규시즌)에 없는 사실 — 외부 CSV에서 읽음 {연도: "한국시리즈 우승"}
CHAMPIONS = {int(y): "한국시리즈 우승" for y, r in
             pd.read_csv(EXTERNAL / "samsung_korean_series.csv").set_index("season")["result"].items()
             if r in ("우승", "통합우승")}

ORIGINS = ["삼성 육성", "돌아온 선수", "외부 이적", "외국인"]
IP_TO_PA = 4.3  # 1이닝 ≈ 4.3타석 (리그 평균 근사치)


def origin_share(bat: pd.DataFrame, pit: pd.DataFrame) -> pd.Series:
    """한 시즌 출전(타석 + 이닝×4.3) 중 '온 경로'별 몫"""
    pa = bat.groupby("origin")["PA"].sum().reindex(ORIGINS, fill_value=0)
    ip = pit.groupby("origin")["IP_num"].sum().reindex(ORIGINS, fill_value=0)
    return (pa + ip * IP_TO_PA) / (pa.sum() + ip.sum() * IP_TO_PA)


@st.cache_data
def departures() -> tuple[pd.DataFrame, pd.DataFrame]:
    """삼성에서 Y년(2014~2022)을 뛰고 Y+1년에 다른 팀에서 뛴 주축 (타자, 투수)
    타자: 300타석 이상 또는 10홈런 이상 · 투수: 8승 · 10세이브 · 10홀드 이상"""
    def pick(df):
        sam = df[df.Team == "삼성"]
        nxt = df[["Id", "Season", "Team"]].assign(Season=lambda d: d.Season - 1).rename(columns={"Team": "next_team"})
        m = sam.merge(nxt, on=["Id", "Season"])
        return m[(m.next_team != "삼성") & m.Season.between(2014, 2022)]
    b = pick(pd.read_csv(RAW / "kbo_batting_stats_season_1982-2026.csv"))
    p = pick(pd.read_csv(RAW / "kbo_pitching_stats_season_1982-2026.csv"))
    return b[(b.PA >= 300) | (b.HR >= 10)], p[(p.W >= 8) | (p.SV >= 10) | (p.HLD >= 10)]
