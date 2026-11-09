import plotly.graph_objects as go
import streamlit as st

from core.data import departures, load_samsung
from core.deep_ui import deep_page, footer, scorebook
from core.theme import BLUE, INK2, RED, add_phase_bands, style

deep_page("fall")

s = load_samsung().loc[2010:2026]

bat_out, pit_out = departures()  # core/data.py — 메인 페이지 2회와 같은 기준

st.caption("2014–2022 · 왕조의 해체")
total_hr = int(bat_out.HR.sum())
total_w = int(pit_out.W.sum())
st.title(f"떠난 주축이 남긴 빈자리: {total_hr}홈런, {total_w}승")
st.markdown("삼성에서 한 시즌을 뛰고 **다음 시즌 다른 팀 유니폼**을 입은 주축 선수를 데이터로 뽑았습니다. "
            "(타자: 300타석 이상 또는 10홈런 이상 · 투수: 8승 · 10세이브 · 10홀드 이상)")

l, r = st.columns(2)
with l:
    scorebook(title="떠난 타자", note="BATTERS", fmt={"타율": "{:.3f}", "장타율": "{:.3f}", "OPS": "{:.3f}"}, df=
        bat_out.sort_values("Season")[["Season", "Player", "HR", "AVG", "OPS" if "OPS" in bat_out else "SLG", "next_team"]]
        .rename(columns={"Season": "삼성 마지막 시즌", "Player": "선수", "HR": "홈런", "AVG": "타율",
                         "SLG": "장타율", "next_team": "다음 팀"}),
    )
with r:
    scorebook(title="떠난 투수", note="PITCHERS", fmt={"ERA": "{:.2f}"}, df=
        pit_out.sort_values("Season")[["Season", "Player", "W", "SV", "HLD", "ERA", "next_team"]]
        .rename(columns={"Season": "삼성 마지막 시즌", "Player": "선수", "W": "승", "SV": "세이브", "HLD": "홀드",
                         "next_team": "다음 팀"}),
    )
st.caption("이적 사유(FA · 트레이드 · 방출 등)는 데이터에 없습니다. 소속팀이 바뀐 사실만 보여 줍니다.")

st.divider()
worst_era = s.loc[2016:2023, "ERA_plus"].idxmin()
st.subheader(f"무너진 건 마운드가 먼저였다 — {worst_era}년 실점 억제 {s.loc[worst_era, 'ERA_plus']:.0f} (리그=100)")
fig = go.Figure()
add_phase_bands(fig)
fig.add_hline(y=100, line_dash="dot", line_color=INK2, annotation_text="리그 평균",
              annotation_position="bottom right")
fig.add_trace(go.Scatter(x=s.index, y=s.R_plus, name="득점력 R+ (타격)", mode="lines+markers",
                         line=dict(color=BLUE, width=3)))
fig.add_trace(go.Scatter(x=s.index, y=s.ERA_plus, name="실점 억제 ERA+ (투수)", mode="lines+markers",
                         line=dict(color=RED, width=3)))
fig.update_yaxes(title="리그 평균 = 100 (높을수록 좋음)")
fig.update_xaxes(dtick=1)
st.plotly_chart(style(fig, 440), width="stretch")

dyn, dark = s.loc[2011:2015], s.loc[2016:2023]
d_r = dark.R_plus.mean() - dyn.R_plus.mean()
d_e = dark.ERA_plus.mean() - dyn.ERA_plus.mean()
a, b = st.columns(2)
a.metric("득점력 변화 (왕조 → 암흑기 평균)", f"{dark.R_plus.mean():.0f}", f"{d_r:+.1f}")
b.metric("실점 억제 변화 (왕조 → 암흑기 평균)", f"{dark.ERA_plus.mean():.0f}", f"{d_e:+.1f}")
st.markdown(
    f"**사실** — 왕조(2011\\~2015) 대비 암흑기(2016\\~2023) 평균이 득점력은 {d_r:+.1f}, 실점 억제는 {d_e:+.1f} 변했습니다.  \n"
    "**해석** — 타선도 약해졌지만 리그 평균 근처를 지켰고, 마운드는 리그 평균 아래로 떨어진 시즌이 더 많습니다. "
    "주축 투수 이탈과 겹치지만, 이적이 원인이라고 단정할 수는 없습니다.  \n"
    "**그래서** — 탈출하려면 마운드부터 돌아와야 했습니다. 탈출의 열쇠에서 확인합니다."
)
st.page_link("views/deep/key.py", label="탈출의 열쇠 보기 →")  # HTML 링크는 배포 iframe에서 주소창을 못 바꿔서 page_link 사용
footer()
