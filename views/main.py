"""메인: 다시, 정상 기념 페이지 (디자인 시안 v8 이식)

- 숫자는 모두 data/clean/*.csv(정규시즌)와 data/external/samsung_korean_series.csv(포스트시즌 · 슬로건)에서 계산한다.
- 모양은 assets/main.css. 이 파일은 데이터 → HTML 조각만 만든다.
- st.html은 iframe 없이 페이지에 바로 붙고 JS는 돌지 않는다 → 애니메이션은 CSS(scroll-driven)만 쓴다.
  CSS · 이닝 바 · 모든 섹션이 한 st.html 안에 있어야 timeline-scope가 이어진다.

목차
  [숫자 계산] 데이터 읽기 → 헬퍼(pct · i · iottda · e) → 회별 데이터(1 · 2 · 4~8회, 3 · 9회는 계산 없음)
  [HTML]      상단 바(5차전 이닝 점수) → 히어로 → 1회..9회 → 조립(PAGE)
"""
from html import escape
from pathlib import Path

import pandas as pd
import streamlit as st

from core.data import EXTERNAL, departures, load_batters, load_ks, load_pitchers, load_samsung, load_team, origin_share

CSS = (Path(__file__).parent.parent / "assets" / "main.css").read_text(encoding="utf-8")
assert "<" not in CSS, "main.css에 꺾쇠가 있으면 st.html(DOMPurify)이 style 태그를 통째로 지움"

# ══════════════════════════════════════════════════════════
# 숫자 계산 — 여기서는 HTML을 만들지 않는다
# ══════════════════════════════════════════════════════════

# ── 데이터 읽기 ──
s = load_samsung()
team = load_team()
ks = load_ks()
titles = ks[ks.result.isin(["우승", "통합우승"])]
NOW = int(s.index.max())                                   # 2026
now = s.loc[NOW]
ks_now = ks.loc[NOW]
LOW = int(s.loc[2010:, "win_pct"].idxmin())                # 2017
low = s.loc[LOW]
all_time_low = LOW == int(s["win_pct"].idxmin())
prev_title = int(titles.index[titles.index < NOW].max())   # 2014
n_titles = int((titles.index <= NOW).sum())                # 9


# ── 헬퍼 ──
def pct(x: float) -> str:
    return f"{x:.3f}".lstrip("0")


def i(x) -> int:
    return int(round(float(x)))


def iottda(word: str) -> str:
    """받침 있으면 '이었', 없으면 '였' (구자욱 → 이었)"""
    c = ord(word[-1]) - 0xAC00
    return "이었" if 0 <= c < 11172 and c % 28 else "였"


def e(x) -> str:
    return escape(str(x))


# 1회: 왕조 — 2011년부터 이어진 정규시즌 1위 · KS 우승 연속
def streak(years, start):
    out, y = [], start
    while y in years:
        out.append(y)
        y += 1
    return out

dyn_rank1 = streak(set(s.index[s["rank"] == 1]), 2011)
dyn_ks = streak(set(titles.index), 2011)

# 2회: 떠난 주축
bat_out, pit_out = departures()
DEP_HR, DEP_W = int(bat_out.HR.sum()), int(pit_out.W.sum())
CLIP_PICKS = [("배영수", "p"), ("박석민", "b"), ("최형우", "b"), ("차우찬", "p")]  # 신문 스크랩으로 보여 줄 4명
clips = []
for name, kind in CLIP_PICKS:
    d = (pit_out if kind == "p" else bat_out).query("Player == @name").iloc[0]
    stat = f"{int(d.W)}승" if kind == "p" else f"{int(d.HR)}홈런"
    clips.append((f"{int(d.Season)} 시즌 후", f"{name}, {d.next_team}로", f"삼성 마지막 시즌 {stat}"))

# 4회: 2014~NOW 전광판
dark = s.loc[2016:2023]
dark_under = int((dark.win_pct < .5).sum())
ks_mark = {y: ("W" if r in ("우승", "통합우승") else "RU") for y, r in ks.result.items() if r in ("우승", "통합우승", "준우승")}

# 5회: 2021 반짝
FLASH = 2021
prev_500 = int(s.index[(s.index < FLASH) & (s.win_pct >= .5)].max())
tie = ks.loc[FLASH]

# 6회: 2024
SIG = 2024
sig, ks_sig = s.loc[SIG], ks.loc[SIG]

# 7회: 9이닝당 볼넷 (리그 = 그 시즌 전체 합계)
def lg_bb9(y):
    t = team[team.Season == y]
    return t.BB_allowed.sum() * 9 / t.IP.sum()

bb_low, bb_now = s.loc[LOW, "BB9"], s.loc[NOW, "BB9"]
lg_low, lg_now = lg_bb9(LOW), lg_bb9(NOW)
t_now = team[team.Season == NOW]
bb_rank = int((t_now.BB9 < bb_now).sum() + 1)

# 8회: 2026 멤버
bat, pit = load_batters().query("Season == @NOW"), load_pitchers().query("Season == @NOW")
share = origin_share(bat, pit)["삼성 육성"]
team_hr_max, team_ip_max = bat.HR.max(), pit.IP_num.max()
MVP = ks_now.mvp


def bcard(name):
    r = bat.query("Player == @name").iloc[0]
    return r, r.Position


def pcard(name):
    r = pit.query("Player == @name").iloc[0]
    return r, ("CL" if r.SV >= 10 else "SP")


members = []
r, pos = bcard("구자욱"); members.append((r, pos, f"타율 {pct(r.AVG)} · {i(r.HR)}홈런 · 출루율 {pct(r.OBP)}"))
r, pos = bcard("디아즈"); members.append((r, pos, f"{'팀 최다 ' if r.HR == team_hr_max else ''}{i(r.HR)}홈런 · 타율 {pct(r.AVG)}"))
r, pos = pcard("후라도"); members.append((r, pos, f"{'팀 최다 ' if r.IP_num == team_ip_max else ''}{r.IP}이닝 · ERA {r.ERA:.2f}"))
r, pos = pcard("김재윤"); members.append((r, pos, f"{i(r.SV)}세이브 · ERA {r.ERA:.2f}"))
r, pos = bcard("최형우"); members.append((r, pos, f"{i(r.Age)}세 · {i(r.HR)}홈런 · 타율 {pct(r.AVG)}"))
choi = members[4][0]

ks_w, ks_l = i(ks_now.series_w), i(ks_now.series_l)
ks_score = f"{ks_w}-{ks_l}"
cl_date = pd.Timestamp(ks_now.clinch_date)

# ══════════════════════════════════════════════════════════
# HTML — 위에서 계산한 숫자로 섹션 조각을 만들고 맨 끝에서 한 번에 붙인다
# ══════════════════════════════════════════════════════════
MT = ks_now.source
SRC_NOTE = "자세한 출처는 맨 아래에."
DISCLAIM = "삼성 라이온즈 구단과 무관한 학습용으로 제작한 페이지입니다."

# ── 상단 바 ──
# 한국시리즈 5차전 삼성 이닝별 득점 (기사 출처 · 합계가 최종 점수와 맞는지 확인)
g5 = pd.read_csv(EXTERNAL / "ks2026_g5_linescore.csv", dtype=str, keep_default_na=False)
g5_runs = list(g5.runs)
g5_total = sum(int(r) for r in g5_runs if r.isdigit())
assert len(g5_runs) == 9 and str(g5_total) == ks_now.clinch_score.split("-")[0], "5차전 이닝 점수 합계가 최종 점수와 다릅니다"
ibar_cells = "".join(f'<div class="c n{k}"><span class="rn">{r}</span></div>' for k, r in enumerate(g5_runs, 1))
ibar_now = "".join(f'<span class="w{k}">▼ {k}회말</span>' for k in range(1, 10))
ibar = f"""
<div class="ibar"><div class="wrap fx ac jb" style="padding-top:8px;padding-bottom:8px;gap:14px">
  <div class="lsb">
    <div></div><div></div>{''.join(f'<div class="h">{k}</div>' for k in range(1, 10))}<div class="h rs">R</div>
    <div class="now" aria-hidden="true">{ibar_now}</div><div class="team">LIONS</div>{ibar_cells}
    <div class="c rs"><span class="r rcell">{g5_total}</span></div>
  </div>
  <div class="bso" aria-hidden="true"><div>B<i class="b1"></i><i class="b2"></i><i class="b3"></i></div><div>S<i class="k1"></i><i class="k2"></i></div><div>O<i class="o1"></i><i class="o2"></i></div></div>
</div></div>"""

PCT_FS = ' style="font-size:clamp(17px,2.2vw,24px)"'
# ── 히어로 ──
hero = f"""
<section class="hero" style="background:var(--blue);color:#fff;position:relative;overflow:clip">
  <div class="disp" style="position:absolute;left:-30px;bottom:-60px;font-size:clamp(200px,30vw,400px);color:#fff;opacity:.07;pointer-events:none">{NOW}</div>
  <div class="wrap" style="display:flex;flex-wrap:wrap;gap:56px;align-items:center;padding-top:96px;padding-bottom:100px;position:relative">
    <div style="flex:1 1 420px;min-width:0">
      <div class="inn hero-in" style="color:var(--yellow)">PLAY BALL</div>
      <h1 class="disp hero-in dl1" style="margin:22px 0 0;font-size:clamp(46px,7vw,88px)">{NOW - prev_title}년 만에<br><span style="color:var(--yellow)">정상에 섰다</span></h1>
      <p class="hero-in dl2" style="margin:24px 0 0;font-size:18px;color:#d3e0f2;max-width:500px">삼성 라이온즈가 {NOW}년 정규시즌 {i(now['rank'])}위, 한국시리즈에서 {e(ks_now.opponent)}를 {ks_w}승 {ks_l}패로 꺾고 우승했습니다. 왕조와 암흑기를 지나 정상에 다시 서기까지를 9이닝으로 돌아봅니다.</p>
    </div>
    <div style="flex:1 1 420px;min-width:0">
      <div style="position:relative">
        <div class="park hero-in dl2">
          <div class="ptitle"><span class="led" style="font-size:14px;letter-spacing:.16em">LIONS PARK</span><span class="led sub" style="font-size:12px;letter-spacing:.12em;color:#8fb4e8;text-shadow:none">REGULAR + KS</span></div>
          <div class="ls">
            <div class="hd" style="text-align:left;padding-left:10px">SEASON</div><div class="hd">W</div><div class="hd">L</div><div class="hd">PCT</div><div class="hd">RANK</div><div class="hd">KS</div>
            <div class="cell team">{LOW}</div><div class="cell dim">{i(low.W)}</div><div class="cell dim">{i(low.L)}</div><div class="cell dim"{PCT_FS}>{pct(low.win_pct)}</div><div class="cell bad">{i(low['rank'])}</div><div class="cell dim">–</div>
            <div class="cell team">{NOW}</div><div class="cell lit">{i(now.W)}</div><div class="cell lit">{i(now.L)}</div><div class="cell lit"{PCT_FS}>{pct(now.win_pct)}</div><div class="cell lit">{i(now['rank'])}</div><div class="cell lit">{ks_score}</div>
          </div>
        </div>
        <div class="sticker stickin"><div class="disp" style="font-size:13px;line-height:1">{NOW}</div><div class="disp" style="font-size:17px;line-height:1.05">KOREAN<br>SERIES</div><div class="disp" style="font-size:12px;line-height:1.1;margin-top:2px">CHAMPIONS</div></div>
      </div>
      <div class="note" style="color:#b9cbe6;margin-top:22px">정규시즌: KBO 기록실 · KS vs {e(ks_now.opponent)}: <a href="{e(MT)}">머니투데이 {cl_date:%Y-%m-%d}</a></div>
    </div>
  </div>
</section>"""

# ── 1회 ──
trophies = "".join(f'<div class="fx col ac reveal" style="gap:6px"><div class="trophy">🏆</div><div class="led" style="font-size:15px">{y}</div></div>' for y in dyn_ks)
s1 = f"""
<section class="short s1" style="background:#0f2b55;color:#fff">
  <div class="wrap fx ac jb" style="flex-wrap:wrap;gap:32px">
    <div class="reveal" style="flex:1 1 380px">
      <div class="inn" style="color:#9db8dc"><span class="tri">▼</span>1ST<span class="sr">1회</span></div>
      <h2 class="disp h2">{len(dyn_ks)}년 동안, 정상은 늘 삼성이었다</h2>
      <p style="margin:0;color:#b9cbe6">삼성 왕조: {dyn_rank1[0]}~{dyn_rank1[-1]} 정규시즌 {len(dyn_rank1)}년 연속 1위, 한국시리즈 {len(dyn_ks)}년 연속 우승({dyn_ks[0]}~{dyn_ks[-1]}).</p>
    </div>
    <div class="fx" style="gap:22px">{trophies}</div>
  </div>
</section>"""

ROT = [-3, 2, -1.5, 3]
# ── 2회 ──
clip_html = "".join(f"""
      <div class="clip reveal" style="--r:{ROT[k]}deg">
        <div style="font-size:11px;letter-spacing:.12em;border-bottom:1.5px solid #1d1b17;padding-bottom:4px">스포츠 · {e(w)}</div>
        <div class="serif" style="font-size:22px;line-height:1.2;margin-top:10px">{e(h)}</div>
        <div style="font-size:14px;margin-top:8px;color:#4a463e">{e(b)}</div>
      </div>""" for k, (w, h, b) in enumerate(clips))
BIG = 'class="disp count" style="font-size:clamp(90px,12vw,140px);color:#fff;line-height:.9;margin-top:6px;--to:{}"'
s2 = f"""
<section class="sec s2" style="background:#1a1d22;color:#e9ecef">
  <div class="wrap">
    <div class="reveal">
      <div class="inn" style="color:#9aa3ae"><span class="tri">▼</span>2ND<span class="sr">2회</span></div>
      <h2 class="disp h2" style="color:#fff">왕조의 주축이 하나씩 떠났다</h2>
      <p style="margin:0;color:#9aa3ae;max-width:680px">삼성에서 한 시즌을 뛰고 다음 시즌 다른 팀 유니폼을 입은 주축(2014–2022).</p>
    </div>
    <div style="display:flex;flex-wrap:wrap;gap:48px;align-items:flex-end;margin-top:44px">
      <div class="reveal" style="border-left:4px solid var(--yellow);padding-left:20px"><div class="label" style="color:var(--yellow)">떠난 홈런</div><div {BIG.format(DEP_HR)}></div></div>
      <div class="reveal" style="border-left:4px solid var(--yellow);padding-left:20px"><div class="label" style="color:var(--yellow)">떠난 승리</div><div {BIG.format(DEP_W)}></div></div>
    </div>
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:28px;margin-top:56px">{clip_html}
    </div>
  </div>
</section>"""

# ── 3회 ──
s3 = f"""
<section class="sec s3" style="background:#0b0c0f;color:#e9ecef;padding:130px 0">
  <div class="wrap fx col ac" style="text-align:center">
    <div class="inn reveal" style="color:#9aa3ae"><span class="tri">▼</span>3RD<span class="sr">3회</span></div>
    <div class="disp reveal" style="font-size:clamp(72px,15vw,200px);line-height:.95;margin-top:20px;color:#fff">{i(low.W)}승 {i(low.L)}패</div>
    <p class="reveal" style="margin:18px 0 0;color:#9aa3ae;font-size:18px">{LOW}년, {i(low.n_teams)}팀 중 {i(low['rank'])}위.</p>
    <div class="stampin" style="margin-top:36px;border:5px solid #ff6b5b;color:#ff6b5b;padding:10px 20px;border-radius:10px;transform:rotate(-6deg)">
      <div class="disp" style="font-size:38px;line-height:1">승률 {pct(low.win_pct)}</div>
      <div style="font-size:13px;letter-spacing:.1em;font-weight:700">{f"{int(s.index.min())}년 창단 이후 최저" if all_time_low else "2010년 이후 최저"}</div>
    </div>
  </div>
</section>"""

# ── 4회 ──
# 전광판 (2014 ~ NOW)
cols = {"head": [], "pct": [], "wl": [], "rank": [], "ks": []}
for y in range(2014, NOW + 1):
    r = s.loc[y]
    on, esc = r.win_pct >= .5, y >= SIG
    cls = "led" if on else "led off"
    k = ks_mark.get(y, "")
    bar_h = (r.win_pct - 0.3) / 0.35 * 80
    bar_bg = ("#ffd84a" if esc else "#8fb4e8") if on else "#3a404a"
    cols["head"].append(f'<div class="{cls}" style="font-size:17px;text-align:center;color:{"#ff6b5b" if y == LOW else "#ffd84a"}">\'{str(y)[2:]}</div>')
    cols["pct"].append(f'<div style="height:120px;display:flex;flex-direction:column;justify-content:flex-end;align-items:center;gap:4px;border-bottom:2px solid #2a2f38">'
                       f'<div class="{cls}" style="font-size:12px">{pct(r.win_pct)}</div>'
                       f'<div class="grow" style="width:70%;height:{bar_h:.1f}px;background:{bar_bg};border-radius:2px 2px 0 0"></div></div>')
    cols["wl"].append(f'<div class="{cls}" style="font-size:14px;text-align:center">{i(r.W)}-{i(r.L)}</div>')
    cols["rank"].append(f'<div class="{cls}" style="font-size:14px;text-align:center">{i(r["rank"])}</div>')
    cols["ks"].append(f'<div class="led" style="font-size:14px;text-align:center;min-height:20px;color:{"#ffd84a" if k == "W" else "#8fb4e8"}">{k}</div>')
# 모바일에선 가로 전광판(820px)이 넘치므로 시즌을 줄로 세운 세로 전광판을 대신 보여 줌
vrows = ""
for y in range(2014, NOW + 1):
    r = s.loc[y]
    on, esc = r.win_pct >= .5, y >= SIG
    cls = "led" if on else "led off"
    k = ks_mark.get(y, "")
    bar_w = (r.win_pct - 0.3) / 0.35 * 100
    bar_bg = ("#ffd84a" if esc else "#8fb4e8") if on else "#3a404a"
    yc = "#ff6b5b" if y == LOW else "#ffd84a"
    vrows += (f'<div class="{cls}" style="color:{yc}">\'{str(y)[2:]}</div>'
              f'<div class="vbar"><div class="trk"><div class="grow-x" style="width:{bar_w:.1f}%;background:{bar_bg}"></div></div><span class="{cls}">{pct(r.win_pct)}</span></div>'
              f'<div class="{cls}">{i(r.W)}-{i(r.L)}</div><div class="{cls}">{i(r["rank"])}</div>'
              f'<div class="led" style="color:{"#ffd84a" if k == "W" else "#8fb4e8"}">{k}</div>')
VHEAD = "".join(f'<div class="led" style="opacity:.6;font-size:11px">{h}</div>' for h in ["", "PCT", "W-L", "RK", "KS"])
LBL = '<div class="led" style="font-size:12px;opacity:.6{}">{}</div>'
n_years = NOW - 2014 + 1
board = (LBL.format("", "SEASON") + "".join(cols["head"]) + LBL.format(";align-self:end", "PCT") + "".join(cols["pct"])
         + LBL.format("", "W-L") + "".join(cols["wl"]) + LBL.format("", "RANK") + "".join(cols["rank"])
         + LBL.format("", "KS") + "".join(cols["ks"]))
s4 = f"""
<section class="sec s4" style="background:var(--night);color:#e9ecef">
  <div class="wrap">
    <div class="reveal">
      <div class="inn" style="color:#9aa3ae"><span class="tri">▼</span>4TH<span class="sr">4회</span></div>
      <h2 class="disp h2" style="color:#fff">{len(dark)}시즌 중 {dark_under}시즌, 5할을 못 넘었다</h2>
      <p style="margin:0;color:#9aa3ae;max-width:680px">{dark.index.min()}~{dark.index.max()}년. 전광판의 불이 꺼지는 칸이 5할 미만 시즌입니다.</p>
    </div>
    <div class="board dots reveal" style="margin-top:40px;padding:22px;overflow-x:auto">
      <div class="hboard" style="display:grid;grid-template-columns:64px repeat({n_years},minmax(52px,1fr));gap:6px;min-width:820px">{board}</div>
      <div class="vboard">{VHEAD}{vrows}</div>
      <div class="led" style="font-size:11px;opacity:.55;margin-top:12px;text-shadow:none;color:#c9d1db">W = 한국시리즈 우승 · RU = 준우승 · {FLASH}년은 {e(tie.opponent)}와 {i(s.loc[FLASH].W)}승 {i(s.loc[FLASH].L)}패 {i(s.loc[FLASH, 'T'])}무 동률, 1위 결정전 패배로 {i(s.loc[FLASH]['rank'])}위</div>
    </div>
  </div>
</section>"""

# ── 5회 ──
mini = ""
for y in range(FLASH - 1, FLASH + 3):
    hot = y == FLASH
    dim = "" if hot else ";color:#5b6370;text-shadow:none"
    mini += (f'<div class="board{" pulse" if hot else ""}"><div class="led" style="font-size:12px{dim}">\'{str(y)[2:]}</div>'
             f'<div class="led" style="font-size:22px{dim}">{pct(s.loc[y].win_pct)}</div></div>')
s5 = f"""
<section class="short s5" style="background:#161a20;color:#e9ecef">
  <div class="wrap fx ac jb" style="flex-wrap:wrap;gap:32px">
    <div class="reveal" style="flex:1 1 420px">
      <div class="inn" style="color:#9aa3ae"><span class="tri">▼</span>5TH<span class="sr">5회</span></div>
      <h2 class="disp h2" style="color:#fff">{FLASH}년, {FLASH - prev_500}년 만의 5할. 그리고 다시</h2>
      <p style="margin:0;color:#9aa3ae">{e(tie.opponent)}와 동률까지 갔지만 1위 결정전에서 {e(tie.clinch_score)}로 져 {i(s.loc[FLASH]['rank'])}위. 그리고 {FLASH + 1}년 {i(s.loc[FLASH + 1]['rank'])}위 · {FLASH + 2}년 {i(s.loc[FLASH + 2]['rank'])}위로 다시 내려갔습니다.</p>
    </div>
    <div class="mini">{mini}</div>
  </div>
</section>"""

# ── 6회 ──
s6 = f"""
<section class="short s6" style="background:var(--blue2);color:#fff">
  <div class="wrap fx ac jb" style="flex-wrap:wrap;gap:32px">
    <div class="reveal" style="flex:1 1 420px">
      <div class="inn" style="color:var(--yellow)"><span class="tri">▼</span>6TH<span class="sr">6회</span></div>
      <h2 class="disp h2">{SIG}년, 불이 다시 들어왔다</h2>
      <p style="margin:0;color:#c9d7ee">정규시즌 {i(sig['rank'])}위({i(sig.W)}승 {i(sig.L)}패), 한국시리즈 {e(ks_sig.result)}({e(ks_sig.opponent)}에 {i(ks_sig.series_w)}승 {i(ks_sig.series_l)}패). 우승은 아니었지만 탈출의 첫 신호였습니다.</p>
    </div>
    <div class="board reveal" style="padding:16px 22px;text-align:center"><div class="led" style="font-size:13px">{SIG}</div><div class="led" style="font-size:40px">RANK {i(sig['rank'])}</div><div class="led" style="font-size:13px;color:#8fb4e8;text-shadow:none">KS RUNNER-UP</div></div>
  </div>
</section>"""

d_low, d_now = bb_low - lg_low, lg_now - bb_now
# ── 7회 ──
s7 = f"""
<section class="sec s7" style="background:#fff">
  <div class="seam" style="right:-300px;top:-120px"></div>
  <div class="seam" style="left:-360px;bottom:-260px"></div>
  <div class="wrap" style="position:relative">
    <div class="reveal">
      <div class="inn" style="color:var(--blue)"><span class="tri">▼</span>7TH<span class="sr">7회</span></div>
      <h2 class="disp h2">탈출의 열쇠: 마운드가 볼넷을 줄였다</h2>
      <p style="margin:0;color:var(--ink2);max-width:680px">{LOW}년과 {NOW}년을 리그 평균과 비교했을 때 가장 크게 좋아진 지표, 9이닝당 볼넷 허용.</p>
    </div>
    <div style="display:flex;flex-wrap:wrap;gap:48px;align-items:flex-end;margin-top:48px">
      <div class="reveal" style="flex:1 1 280px;min-width:0">
        <div class="label" style="color:var(--ink2)">{LOW} · 바닥</div>
        <div class="disp strike" style="font-size:clamp(90px,12vw,140px);line-height:.95;color:#9aa3ae">{bb_low:.2f}</div>
        <div style="font-size:16px;margin-top:6px">리그 평균({lg_low:.2f})보다 <b>{d_low:.2f}개 더</b></div>
      </div>
      <div class="reveal" style="flex:1 1 280px;min-width:0">
        <div class="label" style="color:var(--blue)">{NOW} · 우승</div>
        <div class="disp" style="font-size:clamp(90px,12vw,140px);line-height:.95;color:var(--blue)">{bb_now:.2f}</div>
        <div style="font-size:16px;margin-top:6px">리그 평균({lg_now:.2f})보다 <b>{d_now:.2f}개 덜</b> · {len(t_now)}팀 중 {bb_rank}번째로 적음</div>
      </div>
    </div>
    <div style="display:flex;flex-wrap:wrap;gap:20px;margin-top:48px">
      <div class="reveal" style="flex:1 1 280px;border-top:3px solid var(--ink);padding-top:14px"><div style="font-size:15px;color:var(--ink2)">실점 억제 ERA+ (리그 = 100)</div><div class="disp" style="font-size:44px">{i(low.ERA_plus)} <span style="color:#9aa3ae">→</span> <span class="count" style="color:var(--blue);--to:{i(now.ERA_plus)}"></span></div></div>
      <div class="reveal" style="flex:1 1 280px;border-top:3px solid var(--ink);padding-top:14px"><div style="font-size:15px;color:var(--ink2)">득점력 R+ (리그 = 100)</div><div class="disp" style="font-size:44px">{i(low.R_plus)} <span style="color:#9aa3ae">→</span> <span class="count" style="color:var(--blue);--to:{i(now.R_plus)}"></span></div></div>
    </div>
    <div style="font-size:13px;color:var(--ink2);margin-top:18px">함께 좋아진 것이지, 이것만으로 우승했다고 단정할 수는 없습니다.</div>
  </div>
</section>"""

MROT = [-3, 2, -2, 3, -1]
# ── 8회 ──
cards = ""
for k, (r, pos, stat) in enumerate(members):
    mvp = f'<div class="mvp">KS MVP · {e(ks_now.mvp_avg)}</div>' if r.Player == MVP else ""
    cards += f"""
      <div class="tcard flip" style="--r:{MROT[k]}deg">
        <div class="stripes" style="height:150px;position:relative">
          <div class="disp" style="position:absolute;top:8px;left:12px;font-size:42px;color:var(--yellow);-webkit-text-stroke:1.5px var(--ink)">{k + 1:02d}</div>
          <div style="position:absolute;top:14px;right:12px;font-family:'DotGothic16',monospace;font-size:12px;background:var(--ink);color:var(--yellow);padding:2px 8px;border-radius:4px">{e(pos)}</div>{mvp}
        </div>
        <div style="background:#fff;color:var(--ink);padding:14px 16px 16px;flex:1;display:flex;flex-direction:column;align-items:flex-start">
          <div class="disp" style="font-size:26px">{e(r.Player)}</div>
          <div style="font-size:14px;line-height:1.5;margin-top:4px;flex:1">{e(stat)}</div>
          <div style="margin-top:10px;display:inline-flex;font-size:12px;font-weight:700;padding:3px 10px;border-radius:999px;background:var(--blue);color:#fff">{e(r.origin)}</div>
        </div>
      </div>"""
mvp_row = members[0][0] if members[0][0].Player == MVP else None
mvp_tail = f"한국시리즈 MVP도 삼성이 키운 {e(MVP)}{iottda(MVP)}습니다." if mvp_row is not None and mvp_row.origin == "삼성 육성" else f"한국시리즈 MVP는 {e(MVP)}{iottda(MVP)}습니다."
s8 = f"""
<section class="sec s8" style="background:var(--yellow)">
  <div class="wrap">
    <div class="reveal">
      <div class="inn" style="color:var(--ink)"><span class="tri">▼</span>8TH<span class="sr">8회</span></div>
      <h2 class="disp h2">출전의 {share:.0%}는 삼성이 키운 선수였다</h2>
      <p style="margin:0;color:#3d3a2c;max-width:680px">{NOW}년 타석·이닝의 절반이 삼성에서 시작한 선수 몫. {mvp_tail}</p>
    </div>
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:22px;margin-top:56px">{cards}
    </div>
    <div class="note" style="color:#3d3a2c;margin-top:28px;text-align:center">카드 기록은 {NOW} 정규시즌(KBO 기록실). KS MVP: 한국시리즈 {e(ks_now.mvp_ab)}타수 {e(ks_now.mvp_h)}안타 {e(ks_now.mvp_hr)}홈런 {e(ks_now.mvp_rbi)}타점 (머니투데이 {cl_date:%Y-%m-%d}).</div>
  </div>
</section>"""

# ── 9회 ──
# 더 깊이 보기 링크는 HTML 밖에서 st.page_link로 붙인다 (맨 아래 '조립' 참고)
DEEPER = [("fall", "어떻게 무너졌나", "떠난 주축 선수와 득점력 · 실점 억제의 변화"),
          ("key", "탈출의 열쇠", "두 시즌을 골라 리그 평균 대비 지표 비교"),
          ("members", f"{NOW} 멤버는 어디서 왔나", "출전을 선수가 삼성에 온 경로별로 나눔"),
          ("timemachine", "타임머신", "시즌을 골라 그해 주요 타자 · 투수 카드")]
s9 = f"""
<section class="sec s9" style="background:var(--blue);padding:110px 0 0">
  <div class="wrap">
    <div class="reveal" style="color:#fff">
      <div class="inn" style="color:var(--yellow)"><span class="tri">▼</span>9TH<span class="sr">9회</span></div>
      <h2 class="disp h2">한국시리즈 <span class="count" style="color:var(--yellow);--to:{ks_w}"></span>승 {ks_l}패, 끝내 정상</h2>
    </div>
    <div style="display:flex;flex-wrap:wrap;gap:40px;align-items:center;justify-content:center;margin-top:44px">
      <div class="clip drop" style="flex:1 1 440px;max-width:600px;min-width:0;--r:-1.5deg;padding:26px 28px 28px">
        <div class="fx jb ac" style="border-bottom:3px double #1d1b17;padding-bottom:8px;font-size:12px;letter-spacing:.1em;gap:8px"><span>{cl_date.year}. {cl_date.month}. {cl_date.day}.</span><span class="serif" style="font-size:20px;letter-spacing:.2em">라이온즈 호외</span><span>학습용 제작</span></div>
        <div class="serif" style="font-size:clamp(34px,5vw,52px);line-height:1.12;margin-top:18px">삼성, {NOW - prev_title}년 만의 정상</div>
        <div class="serif" style="font-size:19px;margin-top:10px;color:#3d3a2c">{e(ks_now.opponent)} 꺾고 {ks_w}승 {ks_l}패… 통산 {n_titles}번째 한국시리즈 우승</div>
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:16px;margin-top:18px;font-size:14px;line-height:1.7;border-top:1.5px solid #1d1b17;padding-top:14px">
          <div>{LOW}년 {i(low.W)}승 {i(low.L)}패, {i(low.n_teams)}팀 중 {i(low['rank'])}위에 머물렀던 라이온즈가 {NOW}년 {i(now.W)}승 {i(now.L)}패로 정규시즌 {i(now['rank'])}위를 차지했다. 한국시리즈에서는 정규시즌 1위 {e(ks_now.opponent)}를 {ks_w}승 {ks_l}패로 꺾었고, {cl_date.month}월 {cl_date.day}일 {e(ks_now.clinch_venue)} {e(ks_now.clinch_game)}을 {e(ks_now.clinch_score)}로 잡아 우승을 확정했다.</div>
          <div>MVP는 시리즈 타율 {e(ks_now.mvp_avg)}({e(ks_now.mvp_ab)}타수 {e(ks_now.mvp_h)}안타)의 {e(MVP)}. 출전의 절반은 삼성이 직접 키운 선수들이 맡았고, {i(choi.Age)}세의 최형우는 다시 돌아와 정규시즌 {i(choi.HR)}홈런을 보탰다. {prev_title}년 이후 {NOW - prev_title}년 만의 우승이다.</div>
        </div>
      </div>
      <div class="reveal" style="flex:0 1 420px;min-width:0;--r:3deg">
        <div class="ticket">
          <div style="padding:20px 22px">
            <div style="font-family:'DotGothic16',monospace;font-size:12px;letter-spacing:.12em;color:var(--blue)">{NOW} SEASON · ADMIT ONE</div>
            <div class="disp" style="font-size:32px;margin-top:6px">{i(now.W)}승 {i(now.L)}패</div>
            <div style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;margin-top:12px">
              <div><div class="disp" style="font-size:22px;color:var(--blue)">{i(now['rank'])}위</div><div style="font-size:12px;color:var(--ink2)">정규시즌</div></div>
              <div><div class="disp" style="font-size:22px;color:var(--blue)">{ks_score}</div><div style="font-size:12px;color:var(--ink2)">KS vs {e(ks_now.opponent)}</div></div>
              <div><div class="disp" style="font-size:22px;color:var(--blue)">{e(ks_now.clinch_score)}</div><div style="font-size:12px;color:var(--ink2)">{e(ks_now.clinch_game)}</div></div>
            </div>
          </div>
          <div style="border-left:2px dashed #c9ced6;padding:18px 14px;display:flex;flex-direction:column;justify-content:space-between;align-items:center;background:var(--yellow);border-radius:0 14px 14px 0">
            <div class="disp" style="font-size:24px;text-align:center;line-height:1.1">V{n_titles}</div>
            <div class="barcode" style="width:100%;height:40px"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
  <div class="endscreen" style="margin-top:110px">
  <div class="finmark" style="background:var(--yellow);color:var(--ink);padding:90px 0 40px;text-align:center;overflow:clip">
    <div class="wrap">
      <div class="disp reveal" style="font-size:clamp(80px,16vw,200px);line-height:.9;letter-spacing:.02em">{e(ks_now.slogan)}</div>
      <div class="reveal" style="margin-top:14px;font-size:18px;font-weight:700">함께 나아가자. 다음 시즌에도.</div>
      <div class="note" style="margin-top:8px;color:#3d3a2c">{e(ks_now.slogan)}({e(ks_now.slogan_meaning)})는 삼성 라이온즈의 {NOW} 포스트시즌 슬로건입니다 · <a href="{e(ks_now.slogan_source)}">머니투데이 2026-10-26</a></div>
    </div>
  </div>
  </div>
</section>"""

# ── 조립 ──
top = f'<div class="topnote" style="background:#05070a;color:#8a929c;border-bottom:1px solid #1c2129"><div class="wrap note" style="padding-top:8px;padding-bottom:8px">{DISCLAIM} {SRC_NOTE}</div></div>'

PAGE = f"<style>{CSS}</style><div class=\"page\" style=\"background:var(--night)\">{top}{ibar}{hero}{s1}{s2}{s3}{s4}{s5}{s6}{s7}{s8}{s9}</div>"

FOOT = f"""<div class="foot">
  <div style="background:#05070a;color:#8a929c">
    <div class="wrap note" style="padding-top:22px;padding-bottom:26px">{DISCLAIM} 정규시즌: KBO 기록실 선수 기록 (<a href="https://www.kaggle.com/datasets/netsong/kbo-player-stats-19822025">KBO Player Stats 1982–2026</a>, netsong, CC BY-NC-SA 4.0)을 팀 단위로 합쳐 계산. 포스트시즌: <a href="{e(MT)}">머니투데이</a>, <a href="https://www.newsis.com/view/NISI20261109_0002286205">뉴시스</a>, <a href="https://kbmaeil.com/article/201411120114505">경북매일</a>, <a href="https://www.jjan.kr/articleAmp/20241029580003">전북일보</a>, <a href="{e(tie.source)}">스포츠경향</a>({FLASH} 1위 결정전). 상단 전광판은 {NOW} 한국시리즈 {e(ks_now.clinch_game)} 삼성 이닝별 득점: <a href="https://www.mediapen.com/news/view/1136064">미디어펜</a>, <a href="https://news.jkn.co.kr/post/1078306">재경일보</a>, <a href="https://www.kbmaeil.com/article/20261108500566">경북매일</a>(득점이 적히지 않은 이닝은 합계로 추론한 0).
    </div>
  </div>
</div>"""

st.html(PAGE)

# ── 더 깊이 보기 카드 + 출처 ──
# 배포 환경(Streamlit Cloud)은 앱을 iframe에 넣어서 HTML 링크로는 주소창이 바뀌지 않음 → st.page_link로 카드를 만든다.
# 카드는 VAMOS(노랑) 바로 아래에 이어 붙이고, 출처는 그 아래 별도 st.html로 그린다.
with st.container(key="deepcards"):
    st.html('<div class="dk-h">더 깊이 보기</div>')
    with st.container(key="dgrid"):
        for u, t, d in DEEPER:
            with st.container(key=f"dcard_{u}"):
                st.page_link(f"views/deep/{u}.py", label=f"{t} →")
                st.html(f'<div class="dk-d">{d}</div>')

st.html(FOOT)
