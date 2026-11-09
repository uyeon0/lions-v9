"""다시, 정상 — 진입점 (페이지 목록만 정의)
실행: streamlit run app.py
메인 = 기념 페이지(views/main.py), 나머지는 '더 깊이 보기' 분석 페이지
"""
import streamlit as st

st.set_page_config(page_title="다시, 정상", page_icon="⚾", layout="wide", initial_sidebar_state="collapsed")

pg = st.navigation({
    "": [st.Page("views/main.py", title="다시, 정상", icon="🏆", default=True)],
    "더 깊이 보기": [
        st.Page("views/deep/fall.py", title="어떻게 무너졌나", icon="📉", url_path="fall"),
        st.Page("views/deep/key.py", title="탈출의 열쇠", icon="🔑", url_path="key"),
        st.Page("views/deep/members.py", title="2026 멤버는 어디서 왔나", icon="🧢", url_path="members"),
        st.Page("views/deep/timemachine.py", title="타임머신", icon="⏳", url_path="timemachine"),
    ],
})
pg.run()
