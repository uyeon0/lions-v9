"""테마: 색 · 글꼴 · 기록지 종이 톤 차트 스타일"""
import plotly.graph_objects as go

from core.data import PHASES

# 색: 삼성 블루 1개 + 비교용 회색, 우승 표시만 금색
BLUE = "#074CA1"       # 삼성 블루 (사용자 지정)
GRAY = "#9aa3ae"
INK = "#141a22"
GOLD = "#FACA09"       # 노랑 (사용자 지정) — 우승 · 강조에만
RED = "#d0342c"
PAPER = "#f3efe4"
INK2 = "#56606b"
RULE = "#cfc6ae"
FONT = "IBM Plex Sans KR, sans-serif"


def style(fig: go.Figure, height: int = 420) -> go.Figure:
    """기록지 종이 톤 차트"""
    fig.update_layout(
        height=height, margin=dict(t=30, b=20, l=10, r=10),
        paper_bgcolor=PAPER, plot_bgcolor=PAPER,
        font=dict(size=15, color=INK, family=FONT),
        hoverlabel=dict(font_size=14, font_family=FONT, bgcolor="#fbf9f3", bordercolor=INK),
        legend=dict(orientation="h", y=1.08, x=0, bgcolor="rgba(0,0,0,0)"),
    )
    fig.update_xaxes(showgrid=False, linecolor=INK, linewidth=1.5, ticks="outside", tickcolor=INK,
                     title_font=dict(color=INK2, size=13))
    fig.update_yaxes(gridcolor=RULE, griddash="dot", zeroline=False, linecolor=INK, title_font=dict(color=INK2, size=13))
    return fig


def add_phase_bands(fig: go.Figure, start: int = 2010, end: int = 2026) -> None:
    for name, a, b, color in PHASES:
        a, b = max(a, start), min(b, end)
        if a > b:
            continue
        fig.add_vrect(x0=a - 0.5, x1=b + 0.5, fillcolor=color, opacity=0.7, line_width=0, layer="below",
                      annotation_text=name, annotation_position="top left",
                      annotation_font=dict(size=13, color=INK2, family="DotGothic16, monospace"))


