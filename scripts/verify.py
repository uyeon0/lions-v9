"""검산: 선수 기록을 합친 팀 기록(scripts/clean.py) vs 공식 팀 기록(mattop, 1982~2021)"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent  # 프로젝트 루트 (어디서 실행해도 같은 data/)

mine = pd.read_csv(f"{ROOT}/data/clean/team_season.csv")
ob = pd.read_csv(f"{ROOT}/data/raw/kbobattingdata.csv")
op = pd.read_csv(f"{ROOT}/data/raw/kbopitchingdata.csv")

# mattop 영문 팀명 → netsong 한글 팀명 (시즌별 이름 그대로)
NAME = {"Samsung Lions": "삼성", "Lotte Giants": "롯데", "LG Twins": "LG", "MBC Blue Dragons": "MBC",
        "Doosan Bears": "두산", "OB Bears": "OB", "Haitai Tigers": "해태", "Kia Tigers": "KIA",
        "Hanwha Eagles": "한화", "Binggre Eagles": "빙그레", "SK Wyverns": "SK", "SSG Landers": "SSG",
        "Sammi Superstars": "삼미", "Chungbo Pintos": "청보", "Pacific Dolphins": "태평양",
        "Hyundai Unicorns": "현대", "Ssangbangwool Raiders": "쌍방울", "Woori Heroes": "우리",
        "Nexen Heroes": "넥센", "Kiwoom Heroes": "키움", "NC Dinos": "NC", "KT Wiz": "KT"}
off = ob.assign(Team=ob.team.map(NAME), Season=ob.year)[["Season", "Team", "games", "runs", "homeruns", "OPS"]] \
    .merge(op.assign(Team=op.team.map(NAME), Season=op.year)[["Season", "Team", "wins", "losses", "ERA"]], on=["Season", "Team"])
print("팀 이름 매핑 실패:", off.Team.isna().sum())

m = mine.merge(off, on=["Season", "Team"], how="inner")
import sys
if len(sys.argv) > 1:
    m = m[m.Season >= int(sys.argv[1])]
print(f"비교한 팀 × 시즌: {len(m)}행 (공식 {len(off)}행)")
checks = {"경기 수": ("G", "games"), "득점": ("R", "runs"), "홈런": ("HR", "homeruns"),
          "승": ("W", "wins"), "패": ("L", "losses"), "OPS": ("OPS_x", "OPS_y"), "ERA": ("ERA_x", "ERA_y")}
for name, (a, b) in checks.items():
    diff = (m[a] - m[b]).abs()
    tol = 0.006 if name in ("OPS", "ERA") else 0
    bad = m[diff > tol]
    print(f"- {name}: 일치 {len(m) - len(bad)}/{len(m)} · 최대 차이 {diff.max():.3f}")
    if len(bad):
        print(bad[["Season", "Team", a, b]].head(5).to_string(index=False))

s = m[m.Team == "삼성"]
print("\n삼성만:", "모두 일치" if ((s.W == s.wins) & (s.L == s.losses) & (s.R == s.runs)).all() else "차이 있음")
