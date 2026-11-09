import plotly.graph_objects as go
import streamlit as st

from core.data import ORIGINS, load_batters, load_pitchers, origin_share
from core.deep_ui import deep_page, footer, scorebook
from core.theme import BLUE, GOLD, style

deep_page("members")

ORDER = ORIGINS
COLOR = {"삼성 육성": BLUE, "돌아온 선수": "#4f86c6", "외부 이적": "#b7ae98", "외국인": GOLD}

year = st.select_slider("시즌", options=list(range(2014, 2027)), value=2026)
b = load_batters().query("Season == @year")
p = load_pitchers().query("Season == @year")

pa = b.groupby("origin")["PA"].sum().reindex(ORDER, fill_value=0)
ip = p.groupby("origin")["IP_num"].sum().reindex(ORDER, fill_value=0)
home_share = origin_share(b, p)["삼성 육성"]  # 이닝 ≈ 4.3타석으로 환산 (core/data.py)

st.caption(f"{year} 삼성 라이온즈 · 선수는 어디서 왔나")
st.title(f"{year}년 출전의 {home_share:.0%}는 삼성이 직접 키운 선수였다")
st.markdown("타석(타자)과 이닝(투수)을 **선수가 삼성에 온 경로**별로 나눴습니다. "
            "출전 몫이 클수록 그 해 팀을 끌고 간 선수들입니다.")

fig = go.Figure()
for o in ORDER:
    fig.add_trace(go.Bar(
        name=o, y=["타석 (타자)", "이닝 (투수)"],
        x=[pa[o] / pa.sum() * 100, ip[o] / ip.sum() * 100], orientation="h", marker_color=COLOR[o],
        text=[f"{pa[o] / pa.sum():.0%}", f"{ip[o] / ip.sum():.0%}"], textposition="inside",
        hovertemplate=f"{o}<br>%{{x:.1f}}%<extra></extra>",
    ))
fig.update_layout(barmode="stack")
fig.update_xaxes(title="출전 몫 (%)", range=[0, 100])
st.plotly_chart(style(fig, 260), width="stretch")

st.subheader("주요 선수")
l, r = st.columns(2)
bt = b[b.PA >= 250].sort_values("PA", ascending=False)
pt = p[p.IP_num >= 50].sort_values("IP_num", ascending=False)
with l:
    scorebook(title="타자", note="250타석 이상", fmt={"타율": "{:.3f}", "출루율": "{:.3f}", "장타율": "{:.3f}"}, df=bt[["Player", "origin", "PA", "HR", "AVG", "OBP", "SLG", "first_samsung"]].rename(columns={
        "Player": "선수", "origin": "온 경로", "PA": "타석", "HR": "홈런", "AVG": "타율", "OBP": "출루율",
        "SLG": "장타율", "first_samsung": "삼성 첫 시즌"}))
with r:
    scorebook(title="투수", note="50이닝 이상", fmt={"ERA": "{:.2f}"}, df=pt[["Player", "origin", "IP", "W", "SV", "HLD", "ERA", "first_samsung"]].rename(columns={
        "Player": "선수", "origin": "온 경로", "IP": "이닝", "W": "승", "SV": "세이브", "HLD": "홀드",
        "first_samsung": "삼성 첫 시즌"}))

with st.expander("'온 경로'는 이렇게 나눴습니다"):
    st.markdown(
        "- **삼성 육성**: 다른 KBO 팀 기록 없이 삼성에서 시작한 선수 (해외에서 돌아온 경우 포함)\n"
        "- **돌아온 선수**: 삼성에서 뛰다가 다른 팀에 갔다가 다시 온 선수\n"
        "- **외부 이적**: 다른 KBO 팀에서 뛰다 온 선수 (FA · 트레이드 · 방출 후 영입 구분 없음)\n"
        "- **외국인**: 드래프트 정보가 '자유선발(2010년 이후)' 또는 '외국인'인 선수 — 문자열로 추정한 것이라 틀릴 수 있습니다\n"
        "- 투수 이닝은 타석과 합치려고 1이닝 ≈ 4.3타석으로 환산했습니다 (리그 평균 근사치)."
    )
footer()
