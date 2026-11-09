"""'더 깊이 보기' 페이지 공통 UI: 상단 바 · 출처 · 기록지 표"""
import html
import re

import pandas as pd
import streamlit as st

from core.data import ROOT

SOURCE = ("데이터: KBO 기록실(koreabaseball.com) 정규시즌 선수 기록 — "
          "[KBO Player Stats 1982–2026](https://www.kaggle.com/datasets/netsong/kbo-player-stats-19822025) "
          "(netsong, CC BY-NC-SA 4.0)을 팀 단위로 합쳐 계산했습니다. 한국시리즈 결과는 언론 기사에서 따로 모았습니다. 2021 순위는 공식 기록(2위)으로 바로잡았습니다. "
          "삼성 라이온즈 구단과 무관한, 학습용으로 제작한 페이지입니다.")


def footer() -> None:
    """출처 (마크다운 링크 · 코드 표기를 HTML로 바꿔서)"""
    t = html.escape(SOURCE, quote=False)
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2" target="_blank">\1</a>', t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    st.html(f'<div class="dfoot">{t}</div>')


# ── '더 깊이 보기' 공통 테마 (기록지 종이 톤) ──
DEEP_CSS = (ROOT / "assets" / "deep.css").read_text(encoding="utf-8")
assert "<" not in DEEP_CSS, "deep.css에 꺾쇠가 있으면 st.html(DOMPurify)이 style 태그를 통째로 지움"
DEEP_PAGES = [("fall", "어떻게 무너졌나"), ("key", "탈출의 열쇠"),
              ("members", "2026 멤버는 어디서 왔나"), ("timemachine", "타임머신")]


def deep_page(current: str) -> None:
    """종이 톤 CSS + 상단 바(메인으로 · 4개 페이지 탭). 각 페이지 맨 위에서 한 번 부른다.
    링크는 st.page_link로 만든다. 배포 환경(Streamlit Cloud)은 앱을 iframe에 넣어서,
    HTML 링크로 옮기면 iframe 안에서만 페이지가 바뀌고 주소창은 그대로 남기 때문이다."""
    st.html(f"<style>{DEEP_CSS}</style>")
    with st.container(key="dbar"):
        with st.container(key="dhome", width="content"):
            st.page_link("views/main.py", label="← 다시, 정상")
        st.html('<div class="lb">더 깊이 보기</div>')
        with st.container(horizontal=True, horizontal_alignment="center", key="dtabs"):
            for u, t in DEEP_PAGES:
                with st.container(key=f"dtab_{'on' if u == current else u}", width="content"):
                    st.page_link(f"views/deep/{u}.py", label=t)


def _cell(v, fmt):
    if isinstance(v, (int, float)) and fmt:
        return fmt.format(v) if v == v else "-"
    if isinstance(v, float):
        if v != v:
            return "-"
        return str(int(v)) if v.is_integer() else f"{v:.2f}"
    return html.escape(str(v))


def scorebook(df: pd.DataFrame, title: str = "", note: str = "", fmt: dict | None = None,
              index: bool = False) -> None:
    """표를 기록지처럼 HTML로 그린다. fmt = {칸 이름: "{:.3f}"} (없으면 정수는 그대로, 소수는 둘째 자리)"""
    fmt = fmt or {}
    d = df.reset_index(names="") if index else df
    head = "".join(f"<th>{html.escape(str(c))}</th>" for c in d.columns)
    body = "".join("<tr>" + "".join(f"<td>{_cell(v, fmt.get(c))}</td>" for c, v in row.items()) + "</tr>"
                   for _, row in d.iterrows())
    cap = f'<div class="sbt">{html.escape(title)}<span>{html.escape(note)}</span></div>' if title else ""
    st.html(f'{cap}<div class="sbwrap"><table class="sb"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>')


