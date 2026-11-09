import streamlit as st

from core.data import CHAMPIONS, load_batters, load_pitchers, load_samsung, phase_of
from core.deep_ui import deep_page, footer

deep_page("timemachine")

s = load_samsung()
year = st.select_slider("시즌을 고르십시오", options=list(range(1982, 2027)), value=2014)
row = s.loc[year]
b = load_batters().query("Season == @year").sort_values("PA", ascending=False).head(9)
p = load_pitchers().query("Season == @year").sort_values("IP_num", ascending=False).head(6)

badge = f" · 🏆 {CHAMPIONS[year]}*" if year in CHAMPIONS else ""
st.caption(f"{phase_of(year)}{badge}")
st.title(f"{year} 삼성 라이온즈 — {int(row.W)}승 {int(row.L)}패, {int(row.n_teams)}팀 중 {int(row['rank'])}위")

c1, c2, c3, c4 = st.columns(4)
c1.metric("승률", f"{row.win_pct:.3f}")
c2.metric("득점력 (리그=100)", f"{row.R_plus:.0f}")
c3.metric("실점 억제 (리그=100)", f"{row.ERA_plus:.0f}")
c4.metric("팀 홈런", f"{int(row.HR)}개")

st.subheader("타석을 가장 많이 받은 9명")
cols = st.columns(3)
for i, (_, r) in enumerate(b.iterrows()):
    with cols[i % 3].container(border=True):
        st.markdown(f"**{r.Player}** · {r.Position if isinstance(r.Position, str) else ''} · {int(r.Age)}세")
        st.markdown(f"{int(r.PA)}타석 · {int(r.HR)}홈런 · 타율 {r.AVG:.3f}")
        st.caption(r.origin if "origin" in r else "")

st.subheader("가장 많이 던진 6명")
cols = st.columns(3)
for i, (_, r) in enumerate(p.iterrows()):
    with cols[i % 3].container(border=True):
        st.markdown(f"**{r.Player}** · {int(r.Age)}세")
        era = f"{r.ERA:.2f}" if r.ERA == r.ERA else "-"
        st.markdown(f"{r.IP}이닝 · {int(r.W)}승 {int(r.L)}패 · ERA {era}")
        st.caption(r.origin)

if year in CHAMPIONS:
    st.caption("* 우승은 정규시즌 데이터에 없는 사실이라 언론 기사에서 따로 모았습니다.")
footer()
