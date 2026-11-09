"""원본(선수 × 시즌) → 팀 × 시즌 집계 + 삼성 선수 표

입력: data/raw/kbo_batting_stats_season_1982-2026.csv, data/raw/kbo_pitching_stats_season_1982-2026.csv
출력: data/clean/team_season.csv, data/clean/samsung_batters.csv, data/clean/samsung_pitchers.csv
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent  # 프로젝트 루트 (어디서 실행해도 같은 data/)

RAW = f"{ROOT}/data/raw"
bat = pd.read_csv(f"{RAW}/kbo_batting_stats_season_1982-2026.csv")
pit = pd.read_csv(f"{RAW}/kbo_pitching_stats_season_1982-2026.csv")
n_bat, n_pit = len(bat), len(pit)


def parse_ip(s) -> float:
    """'221 2/3' → 221.667, '57' → 57.0, '2/3' → 0.667"""
    total = 0.0
    for part in str(s).split():
        if "/" in part:
            a, b = part.split("/")
            total += int(a) / int(b)
        else:
            total += float(part)
    return total


pit["IP_num"] = pit["IP"].map(parse_ip)
# 숨은 결측: ERA · WPCT의 '-' → NaN (팀 지표는 합계로 다시 계산하므로 선수 ERA는 표시용으로만 씀)
pit["ERA"] = pd.to_numeric(pit["ERA"].replace("-", np.nan))
pit["WPCT"] = pd.to_numeric(pit["WPCT"].replace("-", np.nan))
for c in ["AVG", "OBP", "SLG"]:  # 타수 0인 타자는 '-'
    bat[c] = pd.to_numeric(bat[c].replace("-", np.nan))

# ── 팀 × 시즌 ──────────────────────────────────────────────
b = bat.groupby(["Season", "Team"]).agg(
    G=("G", "max"),  # 팀 경기 수 ≈ 가장 많이 나온 타자의 경기 수 (verify.py에서 공식 기록과 비교)
    PA=("PA", "sum"), AB=("AB", "sum"), R=("R", "sum"), H=("H", "sum"),
    D2=("2B", "sum"), D3=("3B", "sum"), HR=("HR", "sum"), TB=("TB", "sum"),
    BB=("BB", "sum"), HBP=("HBP", "sum"), SO=("SO", "sum"), SF=("SF", "sum"), SB=("SB", "sum"),
)
p = pit.groupby(["Season", "Team"]).agg(
    W=("W", "sum"), L=("L", "sum"), SV=("SV", "sum"),
    IP=("IP_num", "sum"), RA=("R", "sum"), ER=("ER", "sum"),
    H_allowed=("H", "sum"), HR_allowed=("HR", "sum"), BB_allowed=("BB", "sum"),
    HBP_allowed=("HBP", "sum"), SO_pitch=("SO", "sum"), TBF=("TBF", "sum"),
)
team = b.join(p, how="outer").reset_index()
# 팀 경기 수: 같은 시즌 팀들은 경기 수가 같으므로 시즌 일정 = 그 시즌 '가장 많이 나온 타자'의 경기 수 최댓값
# (팀별 max G는 전 경기 출장 선수가 없으면 작게 나와서 쓰지 않음 — verify.py 참고)
team["G"] = team.groupby("Season")["G"].transform("max")

# 비율 지표는 선수 값을 평균 내지 않고 합계로 다시 계산 (분모 문제)
team["T"] = (team["G"] - team["W"] - team["L"]).clip(lower=0)          # 무승부 (추정)
team["win_pct"] = team["W"] / (team["W"] + team["L"])
team["R_per_G"] = team["R"] / team["G"]
team["RA_per_G"] = team["RA"] / team["G"]
team["run_diff_per_G"] = team["R_per_G"] - team["RA_per_G"]
team["AVG"] = team["H"] / team["AB"]
team["OBP"] = (team["H"] + team["BB"] + team["HBP"]) / (team["AB"] + team["BB"] + team["HBP"] + team["SF"])
team["SLG"] = team["TB"] / team["AB"]
team["OPS"] = team["OBP"] + team["SLG"]
team["HR_per_G"] = team["HR"] / team["G"]
team["ERA"] = team["ER"] * 9 / team["IP"]
team["WHIP"] = (team["H_allowed"] + team["BB_allowed"]) / team["IP"]
team["BB9"] = team["BB_allowed"] * 9 / team["IP"]
team["SO9"] = team["SO_pitch"] * 9 / team["IP"]
team["HR9"] = team["HR_allowed"] * 9 / team["IP"]

# 리그 평균(그 시즌 전체 합계 기준) 대비 차이 — 시대별 타고투저를 걷어내기 위해
league = team.groupby("Season")[["R", "RA", "G", "H", "BB", "HBP", "AB", "SF", "TB", "ER", "IP"]].sum()
lg = pd.DataFrame({
    "lg_R_per_G": league["R"] / league["G"],
    "lg_OPS": (league["H"] + league["BB"] + league["HBP"]) / (league["AB"] + league["BB"] + league["HBP"] + league["SF"])
              + league["TB"] / league["AB"],
    "lg_ERA": league["ER"] * 9 / league["IP"],
})
team = team.merge(lg, left_on="Season", right_index=True)
team["R_plus"] = team["R_per_G"] / team["lg_R_per_G"] * 100       # 100 = 리그 평균, 높을수록 좋음
team["ERA_plus"] = team["lg_ERA"] / team["ERA"] * 100              # 100 = 리그 평균, 높을수록 좋음
team["OPS_plus_simple"] = team["OPS"] / team["lg_OPS"] * 100

team["rank"] = team.groupby("Season")["win_pct"].rank(ascending=False, method="min").astype(int)
team["n_teams"] = team.groupby("Season")["Team"].transform("size")

# 공식 순위 덮어쓰기 (data/external/rank_overrides.csv)
# 위 순위는 '선수 합계 승률'만으로 매긴 값이라 동률 뒤 순위 결정전 같은 공식 절차를 모름.
# 예: 2021 삼성은 선수 합계로 76승 59패 승률 1위지만, 공식으로는 KT와 76승 59패 9무 동률 후
#     1위 결정전 0-1 패배로 2위 (스포츠경향). 그래서 공식 순위를 따로 적어 두고 덮어쓴다.
overrides = pd.read_csv(f"{ROOT}/data/external/rank_overrides.csv")
for o in overrides.itertuples():
    hit = (team["Season"] == o.season) & (team["Team"] == o.team)
    team.loc[hit, "rank"] = o.rank
    print(f"순위 덮어쓰기: {o.season} {o.team} → {o.rank}위 ({o.source})")

team = team.round(4)
team.to_csv(f"{ROOT}/data/clean/team_season.csv", index=False)

# ── 삼성 선수 ──────────────────────────────────────────────
keep_b = ["Id", "Player", "Age", "Position", "Draft", "Season", "Team", "G", "PA", "AB", "R", "H", "2B", "HR", "RBI",
          "SB", "BB", "SO", "AVG", "OBP", "SLG"]
keep_p = ["Id", "Player", "Age", "Draft", "Season", "Team", "G", "W", "L", "SV", "HLD", "IP", "IP_num", "ER", "SO", "BB",
          "HR", "ERA"]

# 선수별 '삼성 첫 시즌'과 '삼성 전 소속팀' — 우승 멤버가 어디서 왔는지 보기 위함
def first_samsung(df):
    allp = df[["Id", "Season", "Team"]].sort_values(["Id", "Season"])
    sam = allp[allp["Team"] == "삼성"].groupby("Id")["Season"].min().rename("first_samsung")
    before = allp.merge(sam, on="Id")
    before = before[before["Season"] < before["first_samsung"]].groupby("Id")["Team"].last().rename("prev_team")
    return sam.to_frame().join(before)

def returned(df):
    """삼성에서 뛰다가 다른 팀에 갔다가 다시 돌아온 시즌이면 True"""
    allp = df[["Id", "Season", "Team"]].sort_values(["Id", "Season"])
    left_before = allp.assign(sam=allp["Team"].eq("삼성"))
    left_before["was_sam"] = left_before.groupby("Id")["sam"].cummax().shift(fill_value=False) \
        & left_before["Id"].eq(left_before["Id"].shift())
    left_before["away_after_sam"] = (left_before["was_sam"] & ~left_before["sam"])
    left_before["ever_away"] = left_before.groupby("Id")["away_after_sam"].cummax()
    return left_before.set_index(["Id", "Season"])["ever_away"]


def origin(row):
    """선수가 삼성에 어떻게 왔나 — 드래프트 문자열 기반 추정 (외국인 판별은 휴리스틱)"""
    draft = str(row["Draft"])
    yy = draft[:2]
    if ("외국인" in draft) or ("자유선발" in draft and yy.isdigit() and int(yy) < 80 and int(yy) >= 10):
        return "외국인"
    if row["returned"]:
        return "돌아온 선수"
    if pd.notna(row["prev_team"]):
        return "외부 이적"
    return "삼성 육성"


for df, keep, out in [(bat, keep_b, "samsung_batters"), (pit, keep_p, "samsung_pitchers")]:
    s = df[df["Team"] == "삼성"][keep].merge(first_samsung(df), left_on="Id", right_index=True, how="left")
    s["returned"] = s.set_index(["Id", "Season"]).index.map(returned(df))
    s["origin"] = s.apply(origin, axis=1)
    s.to_csv(f"{ROOT}/data/clean/{out}.csv", index=False)

print(f"원본 타자 {n_bat}행 · 투수 {n_pit}행 → 팀 × 시즌 {len(team)}행 ({team.Season.min()}~{team.Season.max()})")
print("IP 변환 실패:", pit["IP_num"].isna().sum(), "· ERA '-'→NaN:", pit["ERA"].isna().sum())
print(team[team.Team == "삼성"].set_index("Season").loc[2014:, ["W", "L", "T", "win_pct", "rank", "R_plus", "ERA_plus"]].to_string())
