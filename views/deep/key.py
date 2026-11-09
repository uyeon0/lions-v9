import plotly.graph_objects as go
import streamlit as st

from core.data import load_samsung, load_team
from core.deep_ui import deep_page, footer, scorebook
from core.theme import BLUE, GRAY, INK2, style

deep_page("key")

s = load_samsung()
team = load_team()

METRICS = {  # 이름: (칸, 리그 비교 방식, 높을수록 좋은가, 단위 설명)
    "득점력 (R+)": ("R_plus", None, True, "리그=100"),
    "실점 억제 (ERA+)": ("ERA_plus", None, True, "리그=100"),
    "OPS": ("OPS", "league", True, "출루율+장타율"),
    "경기당 홈런": ("HR_per_G", "league", True, "개"),
    "9이닝당 볼넷 허용": ("BB9", "league", False, "개"),
    "9이닝당 탈삼진": ("SO9", "league", True, "개"),
    "9이닝당 피홈런": ("HR9", "league", False, "개"),
    "WHIP": ("WHIP", "league", False, "이닝당 출루 허용"),
}

st.caption("바닥 vs 지금")
c1, c2 = st.columns(2)
years = list(range(2010, 2027))
y0 = c1.selectbox("비교 기준 시즌", years, index=years.index(2017))
y1 = c2.selectbox("비교 시즌", years, index=years.index(2026))


def vs_league(col: str, year: int) -> float:
    """리그 전체(그 시즌 모든 팀) 대비 몇 % 좋은지. 지표 방향을 맞춰 +면 좋아진 것"""
    lg = team[team.Season == year]
    w = lg["IP"] if col in ("BB9", "SO9", "HR9", "WHIP") else lg["G"]
    lg_val = (lg[col] * w).sum() / w.sum()
    return s.loc[year, col] / lg_val * 100


rows = []
for name, (col, how, higher, unit) in METRICS.items():
    a = s.loc[y0, col] if how is None else vs_league(col, y0)
    b = s.loc[y1, col] if how is None else vs_league(col, y1)
    gain = (b - a) if higher else (a - b)
    rows.append((name, a, b, gain, col))
rows.sort(key=lambda r: r[3], reverse=True)
best = rows[0]

st.title(f"{y0} → {y1}, 가장 크게 좋아진 건 '{best[0]}'")
st.markdown("모든 지표를 **그 시즌 리그 평균 = 100**으로 맞춰서 비교했습니다. "
            "볼넷 · 피홈런 · WHIP처럼 낮을수록 좋은 지표는 방향을 뒤집어서, **오른쪽(+)이면 좋아진 것**입니다.")

fig = go.Figure(go.Bar(
    y=[r[0] for r in rows][::-1], x=[r[3] for r in rows][::-1], orientation="h",
    marker_color=[BLUE if r[3] > 0 else GRAY for r in rows][::-1],
    text=[f"{r[1]:.0f} → {r[2]:.0f}" for r in rows][::-1], textposition="outside",
    hovertemplate="%{y}<br>개선 폭 %{x:+.1f}<extra></extra>",
))
fig.add_vline(x=0, line_color=INK2)
fig.update_xaxes(title=f"개선 폭 (리그=100 기준 점수 차이, {y0} → {y1})", zeroline=False)
st.plotly_chart(style(fig, 460), width="stretch")
st.caption("막대 끝 숫자: 리그 평균=100 기준 점수 (비교 기준 시즌 → 비교 시즌)")

st.divider()
st.subheader("직접 세어 보기")
d = s.loc[[y0, y1]]
show = d[["W", "L", "rank", "R", "RA", "HR", "ERA", "BB_allowed", "SO_pitch", "HR_allowed"]].T
show.index = ["승", "패", "순위", "득점", "실점", "홈런", "팀 ERA", "볼넷 허용", "탈삼진", "피홈런"]
scorebook(show, index=True)
footer()
