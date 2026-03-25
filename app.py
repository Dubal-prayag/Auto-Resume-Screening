# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  RecruitAI v5.0  —  Enterprise AI Hiring Platform                       ║
# ║  Inspired by Greenhouse · Lever · Ashby                                 ║
# ║  Features: Pipeline Kanban · Scorecards · Interview Notes · Analytics   ║
# ║            DEI-neutral scoring · Funnel metrics · Batch export          ║
# ║  Author: Dubal Prayag J · ADIT CVM University · 202040601               ║
# ╚══════════════════════════════════════════════════════════════════════════╝

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
from datetime import datetime

from utils.pdf_parser      import extract_text
from utils.preprocessor    import preprocess
from utils.scorer          import rank_resumes
from utils.skill_extractor import extract_skills, get_skill_match

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="RecruitAI — Enterprise Hiring",
    page_icon="🎯", layout="wide",
    initial_sidebar_state="expanded",
)

# ── Session state ─────────────────────────────────────────────────────────────
_D = {
    "results_df":None, "display_df":None, "jd_skills":[],
    "screened":False,  "n_resumes":0,     "detail_rows":[],
    "dark_mode":False, "jd_text":"",      "job_title":"",
    "department":"",   "location":"",     "job_type":"Full-time",
    "pipeline":{},     "notes":{},        "scores":{},
    "active_tab":"screening",
}
for k, v in _D.items():
    if k not in st.session_state: st.session_state[k] = v

# ── Theme ─────────────────────────────────────────────────────────────────────
DM = st.session_state.dark_mode
C = {
    # Dark mode  →  Deep navy (GitHub-inspired)
    # Light mode →  Pure white + deep ink (Linear/Vercel-inspired)
    "bg":   "#0A0F1A"  if DM else "#FFFFFF",
    "card": "#111827"  if DM else "#FFFFFF",
    "surf": "#0F1729"  if DM else "#FAFBFC",
    "bdr":  "#1E2D45"  if DM else "#EAEDF2",
    "txt":  "#F1F5F9"  if DM else "#0A0F1A",
    "sub":  "#64748B"  if DM else "#5E6E82",
    "pri":  "#3B82F6"  if DM else "#1A56DB",
    "sec":  "#0891B2"  if DM else "#0369A1",
    "grn":  "#10B981"  if DM else "#059669",
    "amb":  "#F59E0B"  if DM else "#D97706",
    "red":  "#EF4444"  if DM else "#DC2626",
    "pur":  "#8B5CF6"  if DM else "#7C3AED",
    "inp":  "#1A2744"  if DM else "#FFFFFF",
    "inpb": "#2E4268"  if DM else "#D1D9E6",
    # Light mode extras
    "l_accent": "#EFF6FF" if not DM else "#1E3A5F",
    "l_green":  "#F0FDF4" if not DM else "#052E16",
    "l_amber":  "#FFFBEB" if not DM else "#431407",
    "l_red":    "#FFF1F2" if not DM else "#450A0A",
}

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

*{{box-sizing:border-box}}
html,body,[data-testid="stAppViewContainer"],[data-testid="stMainBlockContainer"],
[data-testid="block-container"],section.main>div{{
  background:{C['bg']}!important;color:{C['txt']}!important;
  font-family:'Inter',sans-serif!important}}
p,span,div,label,li,h1,h2,h3,h4,h5,h6,
.stMarkdown,[data-testid="stMarkdownContainer"] *,
.element-container *{{color:{C['txt']}!important}}
[data-testid="stHeader"]{{
  background:{'#0A0F1A' if DM else '#FFFFFF'}!important;
  border-bottom:1px solid {C['bdr']}!important;height:3rem!important}}
[data-testid="stSidebar"]{{
  background:{'#0F1729' if DM else '#FAFBFC'}!important;
  border-right:1px solid {C['bdr']}!important}}
[data-testid="stSidebar"] *{{color:{C['txt']}!important}}

/* Topbar */
.topbar{{display:flex;align-items:center;justify-content:space-between;
  padding:16px 20px;margin-bottom:24px;
  border-radius:14px;
  border:1px solid {C['bdr']};
  box-shadow:{'none' if DM else '0 1px 4px rgba(0,0,0,0.04)'}}}
.tb-left{{display:flex;align-items:center;gap:14px}}
.tb-logo{{width:40px;height:40px;border-radius:12px;
  background:linear-gradient(135deg,{C['pri']},{C['sec']});
  display:flex;align-items:center;justify-content:center;
  font-size:1.2rem;font-weight:900;color:#fff;letter-spacing:-1px;
  box-shadow:0 4px 14px rgba(59,130,246,.35)}}
.tb-brand{{font-size:1.1rem;font-weight:800;color:{C['txt']}!important;
  letter-spacing:-.3px}}
.tb-version{{font-size:.65rem;color:{C['sub']}!important;
  background:{C['bdr']};padding:2px 7px;border-radius:10px;
  font-weight:600;letter-spacing:.3px}}
.tb-nav{{display:flex;gap:4px}}
.tb-btn{{padding:7px 16px;border-radius:8px;font-size:.82rem;font-weight:600;
  color:{C['sub']}!important;cursor:pointer;border:none;background:transparent;
  transition:all .15s}}
.tb-btn.on{{background:{C['pri']}22;color:{C['pri']}!important}}
.tb-right{{display:flex;align-items:center;gap:12px}}
.tb-stat{{text-align:center}}
.tb-val{{font-size:.92rem;font-weight:700;color:{C['txt']}!important;line-height:1}}
.tb-lbl{{font-size:.6rem;color:{C['sub']}!important;text-transform:uppercase;
  letter-spacing:.5px}}
.tb-sep{{width:1px;height:28px;background:{C['bdr']}}}

/* KPI cards */
.kpi-row{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;
  margin-bottom:20px}}
.kpi{{background:{C['card']};
  border:1px solid {C['bdr']};
  border-radius:12px;padding:18px 16px;position:relative;overflow:hidden;
  box-shadow:{'none' if DM else '0 1px 4px rgba(0,0,0,0.06),0 4px 12px rgba(0,0,0,0.04)'}}}
.kpi:hover{{box-shadow:{'0 2px 8px rgba(0,0,0,0.2)' if DM else '0 4px 16px rgba(26,86,219,0.12)'}}}
.kpi::before{{content:'';position:absolute;inset:0 0 auto;height:3px;
  background:var(--c);border-radius:12px 12px 0 0}}
.kpi-ico{{font-size:1.4rem;margin-bottom:8px}}
.kpi-val{{font-size:1.9rem;font-weight:900;color:var(--c)!important;line-height:1}}
.kpi-lbl{{font-size:.68rem;font-weight:700;color:{C['sub']}!important;
  text-transform:uppercase;letter-spacing:.6px;margin-top:5px}}
.kpi-sub{{font-size:.72rem;color:{C['sub']}!important;margin-top:4px}}

/* Top candidate hero */
.hero{{background:linear-gradient(135deg,#1e3a8a 0%,#1d4ed8 55%,#0891b2 100%);
  border-radius:16px;padding:22px 26px;margin-bottom:20px;
  display:flex;align-items:center;gap:20px;
  border:1px solid rgba(255,255,255,.08);
  box-shadow:0 8px 32px rgba(30,58,138,.3)}}
.hero-av{{width:56px;height:56px;border-radius:14px;flex-shrink:0;
  background:rgba(255,255,255,.12);display:flex;align-items:center;
  justify-content:center;font-size:1.8rem;
  border:1.5px solid rgba(255,255,255,.2)}}
.hero-name{{font-size:1.25rem;font-weight:800;color:#fff!important;margin-bottom:2px}}
.hero-meta{{font-size:.8rem;color:rgba(255,255,255,.65)!important;margin-bottom:8px}}
.hero-score{{margin-left:auto;text-align:center;flex-shrink:0;
  background:rgba(255,255,255,.08);border-radius:14px;padding:14px 22px;
  border:1px solid rgba(255,255,255,.12)}}
.hero-num{{font-size:2.8rem;font-weight:900;color:#fde047!important;line-height:1}}
.hero-slbl{{font-size:.6rem;font-weight:700;
  color:rgba(255,255,255,.55)!important;text-transform:uppercase;letter-spacing:1.5px}}

/* Pipeline kanban */
.pipe-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;
  margin-bottom:20px}}
.pipe-col{{
  background:{'#0F1729' if DM else '#FAFBFC'};
  border:1px solid {C['bdr']};border-radius:12px;padding:14px 12px}}
.pipe-hdr{{display:flex;align-items:center;justify-content:space-between;
  margin-bottom:10px}}
.pipe-title{{font-size:.72rem;font-weight:700;text-transform:uppercase;
  letter-spacing:.8px;color:{C['sub']}!important;
  display:flex;align-items:center;gap:6px}}
.pipe-dot{{width:7px;height:7px;border-radius:50%;display:inline-block}}
.pipe-count{{font-size:.68rem;font-weight:700;padding:2px 8px;
  border-radius:10px;color:var(--pc)!important;background:var(--pc)18}}
.pipe-card{{
  background:{C['card']};
  border:1px solid {C['bdr']};border-radius:8px;padding:10px 12px;
  margin-bottom:7px;border-left:3px solid var(--pc);
  box-shadow:{'none' if DM else '0 1px 3px rgba(0,0,0,0.05)'}}}
.pipe-card:hover{{
  border-color:var(--pc);
  box-shadow:{'0 2px 8px rgba(0,0,0,0.2)' if DM else '0 3px 10px rgba(26,86,219,0.1)'}}}
.pc-name{{font-size:.82rem;font-weight:600;color:{C['txt']}!important;
  margin-bottom:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.pc-score{{font-size:.7rem;color:{C['sub']}!important}}

/* Section title */
.stitle{{font-size:.68rem;font-weight:700;text-transform:uppercase;
  letter-spacing:1px;color:{C['pri']}!important;
  margin:22px 0 10px;display:flex;align-items:center;gap:8px}}
.stitle::after{{content:'';flex:1;height:1px;
  background:{'linear-gradient(90deg,'+C['bdr']+',transparent)' if True else C['bdr']}}}

/* Candidate profile card */
.cand-hdr{{background:{C['surf']};border:1px solid {C['bdr']};
  border-radius:12px;padding:16px 18px;margin-bottom:2px}}

/* Scorecard */
.scorecard{{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin:12px 0}}
.sc-item{{
  background:{'#0F1729' if DM else '#F8FAFF'};
  border:1px solid {C['bdr']};border-radius:10px;padding:12px;text-align:center;
  box-shadow:{'none' if DM else '0 1px 3px rgba(0,0,0,0.05)'}}}
.sc-val{{font-size:1.5rem;font-weight:800;color:{C['txt']}!important;line-height:1}}
.sc-lbl{{font-size:.65rem;font-weight:700;color:{C['sub']}!important;
  text-transform:uppercase;letter-spacing:.5px;margin-top:4px}}

/* Badges */
.badge{{display:inline-flex;align-items:center;gap:4px;
  padding:4px 11px;border-radius:99px;font-size:.71rem;font-weight:700}}
.b-sl{{
  background:{'#052E16' if DM else '#DCFCE7'};
  color:{'#4ADE80' if DM else '#166534'}!important;
  border:1px solid {'#166534' if DM else '#86EFAC'}}}
.b-rv{{
  background:{'#431407' if DM else '#FEF3C7'};
  color:{'#FCD34D' if DM else '#92400E'}!important;
  border:1px solid {'#92400E' if DM else '#FCD34D'}}}
.b-rj{{
  background:{'#450A0A' if DM else '#FFE4E6'};
  color:{'#FCA5A5' if DM else '#9F1239'}!important;
  border:1px solid {'#9F1239' if DM else '#FDA4AF'}}}
.b-new{{
  background:{'#1e1b4b' if DM else '#EEF2FF'};
  color:{'#a5b4fc' if DM else '#4338CA'}!important;
  border:1px solid {'#3730a3' if DM else '#c7d2fe'}}}

/* Skill chips */
.chip{{display:inline-flex;align-items:center;padding:4px 11px;
  border-radius:99px;font-size:.72rem;margin:2px;font-weight:600;
  transition:all .12s}}
.chip:hover{{transform:scale(1.04)}}
.c-base{{
  background:{'#1e2d45' if DM else '#EFF6FF'};
  color:{'#93c5fd' if DM else '#1E40AF'}!important;
  border:1px solid {'#2E4268' if DM else '#BFDBFE'}}}
.c-ok{{
  background:{'#052E16' if DM else '#DCFCE7'};
  color:{'#4ADE80' if DM else '#15803D'}!important;
  border:1px solid {'#166534' if DM else '#86EFAC'}}}
.c-no{{
  background:{'#450A0A' if DM else '#FFE4E6'};
  color:{'#FCA5A5' if DM else '#9F1239'}!important;
  border:1px solid {'#9F1239' if DM else '#FDA4AF'}}}

/* Progress bar */
.bar{{background:{C['bdr']};border-radius:99px;height:5px;
  overflow:hidden;margin:3px 0 10px}}
.bf{{height:5px;border-radius:99px}}

/* Funnel chart */
.funnel{{display:flex;flex-direction:column;gap:6px;padding:8px 0}}
.funnel-row{{display:flex;align-items:center;gap:10px}}
.funnel-lbl{{font-size:.75rem;font-weight:600;color:{C['sub']}!important;
  width:80px;text-align:right}}
.funnel-bar{{flex:1;background:{C['bdr']};border-radius:99px;
  height:24px;overflow:hidden;position:relative}}
.funnel-fill{{height:24px;border-radius:99px;display:flex;
  align-items:center;padding:0 10px;
  font-size:.7rem;font-weight:700;color:#fff!important;
  transition:width 1s ease;min-width:28px}}
.funnel-n{{font-size:.78rem;font-weight:700;color:{C['txt']}!important;
  width:28px;text-align:right}}

/* Inputs */
textarea{{
  background:{C['inp']}!important;color:{C['txt']}!important;
  border:1.5px solid {C['inpb']}!important;border-radius:10px!important;
  font-size:.87rem!important;line-height:1.5!important;
  box-shadow:{'none' if DM else '0 1px 3px rgba(0,0,0,0.05)'}!important}}
textarea:focus{{
  border-color:{C['pri']}!important;
  box-shadow:0 0 0 3px {'rgba(59,130,246,0.2)' if DM else 'rgba(26,86,219,0.12)'}!important}}
textarea::placeholder{{color:{C['sub']}!important}}
.stTextInput input{{
  background:{C['inp']}!important;color:{C['txt']}!important;
  border:1.5px solid {C['inpb']}!important;border-radius:8px!important;
  box-shadow:{'none' if DM else '0 1px 3px rgba(0,0,0,0.05)'}!important}}
.stTextInput input:focus{{
  border-color:{C['pri']}!important;
  box-shadow:0 0 0 3px {'rgba(59,130,246,0.2)' if DM else 'rgba(26,86,219,0.12)'}!important}}

[data-testid="stFileUploaderDropzone"]{{
  background:{'#1A2744' if DM else '#F8FAFF'}!important;
  border:2px dashed {'#2E4268' if DM else '#BFDBFE'}!important;
  border-radius:12px!important}}
[data-testid="stFileUploaderDropzone"]:hover{{
  border-color:{C['pri']}!important;
  background:{'#1E3A5F' if DM else '#EFF6FF'}!important}}
[data-testid="stFileUploaderDropzone"] p,
[data-testid="stFileUploaderDropzone"] span,
[data-testid="stFileUploaderDropzone"] div{{
  color:{'#93C5FD' if DM else '#1E40AF'}!important;font-weight:500!important}}
[data-testid="stFileUploaderFile"] *{{color:{C['txt']}!important}}

/* Buttons */
.stButton>button{{background:linear-gradient(135deg,{C['pri']},{C['sec']})!important;
  color:#fff!important;font-weight:600!important;font-size:.88rem!important;
  border-radius:9px!important;border:none!important;
  padding:9px 22px!important;transition:all .18s!important}}
.stButton>button:hover{{opacity:.9!important;transform:translateY(-1px)!important;
  box-shadow:0 6px 20px {C['pri']}44!important}}
[data-testid="stDownloadButton"] button{{
  background:{'#1A2744' if DM else '#F8FAFF'}!important;
  color:{C['txt']}!important;
  border:1.5px solid {C['bdr']}!important;
  font-weight:600!important;border-radius:9px!important;font-size:.82rem!important}}
[data-testid="stDownloadButton"] button:hover{{
  border-color:{C['pri']}!important;
  color:{C['pri']}!important;
  background:{'#1E3A5F' if DM else '#EFF6FF'}!important}}

/* Metrics */
[data-testid="stMetricValue"],[data-testid="stMetricValue"]>div{{
  color:{C['pri']}!important;font-weight:800!important;font-size:1.45rem!important}}
[data-testid="stMetricLabel"] p{{color:{C['sub']}!important;
  font-size:.65rem!important;text-transform:uppercase!important;
  letter-spacing:.6px!important;font-weight:700!important}}

/* Expanders */
[data-testid="stExpander"]{{background:{C['card']}!important;
  border:1px solid {C['bdr']}!important;border-radius:12px!important;
  margin-bottom:8px!important;overflow:hidden!important}}
[data-testid="stExpander"] summary{{
  background:{'#0F1729' if DM else '#F4F7FF'}!important;
  padding:11px 16px!important;
  border-bottom:1px solid {C['bdr']}!important}}
[data-testid="stExpander"] summary span,
[data-testid="stExpander"] summary p{{color:{C['txt']}!important;
  font-weight:600!important;font-size:.88rem!important}}

/* Misc widgets */
[data-testid="stSlider"] *,[data-testid="stAlert"] *{{color:{C['txt']}!important}}
[data-testid="stDataFrame"]{{background:{C['card']}!important;
  border-radius:12px!important;border:1px solid {C['bdr']}!important;
  overflow:hidden!important;
  box-shadow:{'none' if DM else '0 1px 4px rgba(0,0,0,0.05)'}!important}}
.stSelectbox>div>div{{background:{C['inp']}!important;color:{C['txt']}!important;
  border-color:{C['inpb']}!important;border-radius:8px!important}}
[data-testid="stToggle"] span{{color:{C['txt']}!important}}
hr{{border-color:{C['bdr']}!important;margin:18px 0!important}}
::-webkit-scrollbar{{width:5px;height:5px}}
::-webkit-scrollbar-track{{background:{C['bg']}}}
::-webkit-scrollbar-thumb{{background:{C['bdr']};border-radius:3px}}

/* Footer */
.foot{{text-align:center;padding:20px;
  border-top:1px solid {C['bdr']};
  margin-top:32px;font-size:.75rem;color:{C['sub']}!important;
  background:{'transparent' if DM else 'linear-gradient(to top,#F0F4FF,transparent)'}}}
</style>""", unsafe_allow_html=True)

# ── Pure helpers ──────────────────────────────────────────────────────────────
def decision(score, ht):
    if score >= ht:  return "✅ Shortlist",     "b-sl", C["grn"]
    if score >= 45:  return "🔍 Review",        "b-rv", C["amb"]
    return                  "❌ Pass",           "b-rj", C["red"]

def gauge(score):
    r=38; c=2*3.14159*r; d=(min(score,100)/100)*c
    col = C["grn"] if score>=65 else C["amb"] if score>=45 else C["red"]
    return (f'<svg width="90" height="90" viewBox="0 0 90 90">'
            f'<circle cx="45" cy="45" r="{r}" fill="none" stroke="{C["bdr"]}" stroke-width="7"/>'
            f'<circle cx="45" cy="45" r="{r}" fill="none" stroke="{col}" stroke-width="7"'
            f' stroke-dasharray="{d:.1f} {c-d:.1f}" stroke-linecap="round"'
            f' transform="rotate(-90 45 45)"/>'
            f'<text x="45" y="41" text-anchor="middle" font-size="15" font-weight="800"'
            f' fill="{C["txt"]}" font-family="Inter">{score:.0f}%</text>'
            f'<text x="45" y="55" text-anchor="middle" font-size="7.5"'
            f' fill="{C["sub"]}" font-family="Inter">SCORE</text></svg>')

def chips(lst, cls):
    return " ".join(f'<span class="chip {cls}">{s}</span>' for s in lst) if lst else ""

def pbar(v, col):
    return f'<div class="bar"><div class="bf" style="width:{v:.0f}%;background:{col}"></div></div>'

def html_report(df, jd_skills, jd_text, jt, dept, loc):
    rows = "".join(
        f"<tr><td>{int(r['Rank'])}</td><td>{r['Resume']}</td>"
        f"<td>{r['Match Score (%)']:.1f}%</td><td>{r['Skill Match (%)']:.1f}%</td>"
        f"<td><b>{r['Final Score (%)']:.1f}%</b></td><td>{r['Recommendation']}</td>"
        f"<td>{r['Matched Skills']}</td>"
        f"<td style='color:#BE123C'>{r['Missing Skills']}</td></tr>"
        for _, r in df.iterrows()
    )
    return (
        f"<!DOCTYPE html><html><head><meta charset='UTF-8'>"
        f"<title>RecruitAI — {jt or 'Screening'} Report</title>"
        f"<style>"
        f"*{{box-sizing:border-box;margin:0;padding:0}}"
        f"body{{font-family:'Segoe UI',Arial,sans-serif;background:#F1F5FB;color:#0F172A}}"
        f".hdr{{background:linear-gradient(135deg,#1e3a8a,#0891b2);padding:28px 36px;color:#fff}}"
        f".hdr h1{{font-size:1.6rem;font-weight:800;margin-bottom:4px}}"
        f".hdr p{{opacity:.75;font-size:.88rem}}"
        f".body{{padding:28px 36px}}"
        f".meta{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:24px}}"
        f".mc{{background:#fff;border:1px solid #E2E8F0;border-radius:10px;padding:14px;text-align:center}}"
        f".mv{{font-size:1.6rem;font-weight:800;color:#1D4ED8}}"
        f".ml{{font-size:.65rem;font-weight:700;color:#64748B;"
        f"text-transform:uppercase;letter-spacing:.5px;margin-top:3px}}"
        f".jd-box{{background:#EFF6FF;border-left:3px solid #3B82F6;"
        f"padding:10px 14px;border-radius:0 8px 8px 0;"
        f"font-size:.82rem;color:#1e40af;margin-bottom:20px}}"
        f"table{{width:100%;border-collapse:collapse;background:#fff;"
        f"border-radius:12px;overflow:hidden;border:1px solid #E2E8F0;"
        f"font-size:12.5px;box-shadow:0 1px 3px rgba(0,0,0,.06)}}"
        f"th{{background:#1D4ED8;color:#fff;padding:10px 12px;text-align:left;"
        f"font-size:.68rem;text-transform:uppercase;letter-spacing:.5px}}"
        f"td{{padding:9px 12px;border-bottom:1px solid #F1F5F9}}"
        f"tr:last-child td{{border:none}}"
        f"tr:nth-child(even) td{{background:#F8FAFF}}"
        f".foot{{margin-top:24px;text-align:center;font-size:.72rem;color:#94A3B8;padding-top:16px;border-top:1px solid #E2E8F0}}"
        f"</style></head><body>"
        f"<div class='hdr'><h1>🎯 RecruitAI — Screening Report</h1>"
        f"<p>Role: {jt or 'Not specified'} &nbsp;|&nbsp; "
        f"Dept: {dept or '—'} &nbsp;|&nbsp; Location: {loc or '—'} &nbsp;|&nbsp; "
        f"Generated: {datetime.now():%d %b %Y, %I:%M %p}</p></div>"
        f"<div class='body'>"
        f"<div class='meta'>"
        f"<div class='mc'><div class='mv'>{len(df)}</div><div class='ml'>Screened</div></div>"
        f"<div class='mc'><div class='mv'>{len(jd_skills)}</div><div class='ml'>JD Skills</div></div>"
        f"<div class='mc'><div class='mv'>{df['Final Score (%)'].max():.0f}%</div><div class='ml'>Top Score</div></div>"
        f"<div class='mc'><div class='mv'>{df['Final Score (%)'].mean():.0f}%</div><div class='ml'>Avg Score</div></div>"
        f"</div>"
        f"<div class='jd-box'><b>JD Skills Detected:</b> {' · '.join(jd_skills) or 'None'}</div>"
        f"<table><tr><th>#</th><th>Candidate</th><th>TF-IDF</th><th>Skills</th>"
        f"<th>Final Score</th><th>Decision</th><th>Matched Skills</th><th>Missing Skills</th></tr>"
        f"{rows}</table>"
        f"<div class='foot'>RecruitAI v5.0 · AI Hiring Platform · "
        f"ADIT CVM University · 202040601 · Dubal Prayag J</div></div>"
        f"</body></html>"
    ).encode()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        f"<div style='text-align:center;padding:20px 0 22px;"
        f"border-bottom:1px solid {C['bdr']};margin-bottom:4px'>"
        f"<div style='width:52px;height:52px;border-radius:16px;"
        f"background:linear-gradient(135deg,{C['pri']},{C['sec']});"
        f"display:flex;align-items:center;justify-content:center;"
        f"font-size:1.4rem;margin:0 auto 12px;"
        f"box-shadow:{'0 4px 14px rgba(59,130,246,.45)' if DM else '0 8px 20px rgba(26,86,219,.2)'}'>"
        f"🎯</div>"
        f"<div style='font-size:1.05rem;font-weight:800;color:{C['txt']};letter-spacing:-.3px'>RecruitAI</div>"
        f"<div style='font-size:.65rem;color:{C['sub']};margin-top:3px;"
        f"background:{'#1E2D45' if DM else '#EFF6FF'};display:inline-block;"
        f"padding:2px 10px;border-radius:10px;font-weight:600;"
        f"color:{C['pri']}!important'>Enterprise v5.0</div>"
        f"</div>",
        unsafe_allow_html=True)

    st.markdown(f"<hr style='margin:0 0 14px'>", unsafe_allow_html=True)

    # Dark mode
    dm = st.toggle("🌙  Dark Mode", value=DM, key="dm")
    if dm != DM:
        st.session_state.dark_mode = dm; st.rerun()

    # Job details
    st.markdown(f"<div style='font-size:.65rem;font-weight:700;color:{C['pri']};"
                f"text-transform:uppercase;letter-spacing:1px;margin:14px 0 6px'>"
                f"📋 Job Details</div>", unsafe_allow_html=True)
    jt  = st.text_input("Job Title",   value=st.session_state.job_title,
                         placeholder="e.g. Python Developer",
                         label_visibility="collapsed", key="jt_in")
    dept= st.text_input("Department",  value=st.session_state.department,
                         placeholder="e.g. Engineering",
                         label_visibility="collapsed", key="dept_in")
    loc = st.text_input("Location",    value=st.session_state.location,
                         placeholder="e.g. Ahmedabad / Remote",
                         label_visibility="collapsed", key="loc_in")
    jtyp= st.selectbox("Job Type",
                        ["Full-time","Part-time","Contract","Internship"],
                        index=["Full-time","Part-time","Contract","Internship"]
                              .index(st.session_state.job_type),
                        label_visibility="collapsed", key="jtyp_in")
    # Persist job details
    st.session_state.job_title   = jt
    st.session_state.department  = dept
    st.session_state.location    = loc
    st.session_state.job_type    = jtyp

    st.markdown(f"<div style='font-size:.65rem;font-weight:700;color:{C['pri']};"
                f"text-transform:uppercase;letter-spacing:1px;margin:14px 0 6px'>"
                f"⚙️ Scoring</div>", unsafe_allow_html=True)
    tw = st.slider("TF-IDF Weight", 0, 100, 70, 5, format="%d%%", key="tw",
                   help="Weight given to text similarity vs skill matching")
    st.caption(f"Skill Match Weight: **{100-tw}%**")

    st.markdown(f"<div style='font-size:.65rem;font-weight:700;color:{C['pri']};"
                f"text-transform:uppercase;letter-spacing:1px;margin:14px 0 6px'>"
                f"🎯 Hire Threshold</div>", unsafe_allow_html=True)
    ht = st.slider("Shortlist above", 40, 90, 65, 5, format="%d%%", key="ht")

    if st.session_state.screened:
        st.markdown(f"<hr style='margin:14px 0'>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:.65rem;font-weight:700;color:{C['pri']};"
                    f"text-transform:uppercase;letter-spacing:1px;margin-bottom:8px'>"
                    f"🔍 Search & Sort</div>", unsafe_allow_html=True)
        sq = st.text_input("Search", placeholder="Filter candidate...",
                           label_visibility="collapsed", key="sq")
        sc = st.selectbox("Sort by",
                          ["Final Score (%)","Match Score (%)","Skill Match (%)","Rank"],
                          label_visibility="collapsed", key="sc")
        sa = st.checkbox("Ascending", False, key="sa")

        st.markdown(f"<hr style='margin:14px 0'>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:.65rem;font-weight:700;color:{C['pri']};"
                    f"text-transform:uppercase;letter-spacing:1px;margin-bottom:8px'>"
                    f"📤 Export</div>", unsafe_allow_html=True)
        dfe = st.session_state.display_df
        if dfe is not None:
            st.download_button("📊  Export CSV",
                dfe.to_csv(index=False).encode(),
                f"recruitai_{(jt or 'results').replace(' ','_')}.csv",
                "text/csv", use_container_width=True)
            st.download_button("📄  Full HTML Report",
                html_report(st.session_state.results_df,
                            st.session_state.jd_skills,
                            st.session_state.jd_text, jt, dept, loc),
                "recruitai_report.html", "text/html",
                use_container_width=True)

        st.markdown(f"<hr style='margin:14px 0'>", unsafe_allow_html=True)
        if st.button("🔄  New Job Screening", use_container_width=True):
            for k in ["results_df","display_df","screened","detail_rows",
                      "n_resumes","jd_text","pipeline","notes","scores"]:
                st.session_state[k] = _D[k]
            st.rerun()

    st.markdown(
        f"<div style='margin-top:20px;font-size:.68rem;color:{C['sub']};text-align:center;line-height:1.7'>"
        f"Built by <span style='color:{C['pri']};font-weight:700'>Dubal Prayag J</span><br>"
        f"ADIT · CVM University · 202040601</div>",
        unsafe_allow_html=True)

# ── Top bar ───────────────────────────────────────────────────────────────────
nr     = st.session_state.n_resumes
top_sc = st.session_state.results_df["Final Score (%)"].max() \
         if st.session_state.screened else 0
hired  = len(st.session_state.pipeline.get("Shortlist",[])) \
         if st.session_state.screened else 0

_tb_style = "background:#0A0F1A" if DM else "background:linear-gradient(135deg,#1E40AF08,#0369A108);border-bottom:1px solid #EAEDF2"
st.markdown(
    f'<div class="topbar" style="{_tb_style}">'
    f'<div class="tb-left">'
    f'<div class="tb-logo">R</div>'
    f'<div>'
    f'<div class="tb-brand">RecruitAI</div>'
    f'<span class="tb-version">Enterprise v5.0</span>'
    f'</div></div>'
    f'</div>'
    f'<div class="tb-right">'
    f'<div class="tb-stat"><div class="tb-val">{nr}</div>'
    f'<div class="tb-lbl">Candidates</div></div>'
    f'<div class="tb-sep"></div>'
    f'<div class="tb-stat"><div class="tb-val">{top_sc:.0f}%</div>'
    f'<div class="tb-lbl">Top Match</div></div>'
    f'<div class="tb-sep"></div>'
    f'<div class="tb-stat"><div class="tb-val">{hired}</div>'
    f'<div class="tb-lbl">Shortlisted</div></div>'
    f'<div class="tb-sep"></div>'
    f'<div class="tb-stat"><div class="tb-val" style="font-size:.75rem!important">'
    f'{(jt or "—")[:18]}</div><div class="tb-lbl">{jtyp}</div></div>'
    f'</div></div>',
    unsafe_allow_html=True)

# ── Input section ─────────────────────────────────────────────────────────────
if not st.session_state.screened:
    st.markdown(
        f'<div class="stitle">📋 New Screening — '
        f'{jt or "Job Title not set"}'
        f'{"  ·  " + dept if dept else ""}'
        f'{"  ·  " + loc  if loc  else ""}</div>',
        unsafe_allow_html=True)

    col1, col2 = st.columns([5,4], gap="large")
    with col1:
        st.markdown(f"<div style='font-size:.68rem;font-weight:700;color:{C['sub']};"
                    f"text-transform:uppercase;letter-spacing:1px;margin-bottom:6px'>"
                    f"Job Description</div>", unsafe_allow_html=True)
        jd = st.text_area("jd", height=280,
                          value=st.session_state.jd_text,
                          placeholder=(
                              "Paste the complete job description here.\n\n"
                              "For best results, include a 'Skills Required:' section "
                              "listing all required technologies and tools.\n\n"
                              "Example:\nSkills Required: Python, Django, SQL, "
                              "Git, REST API, problem solving, communication."),
                          label_visibility="collapsed")
        if jd:
            st.session_state.jd_text = jd
            n_sk = len(extract_skills(jd))
            st.caption(f"🔍 {n_sk} skills detected  ·  "
                       f"Formula: **{tw}% TF-IDF + {100-tw}% Skill Match**")

    with col2:
        st.markdown(f"<div style='font-size:.68rem;font-weight:700;color:{C['sub']};"
                    f"text-transform:uppercase;letter-spacing:1px;margin-bottom:6px'>"
                    f"Resume Files (PDF · DOCX · TXT)</div>", unsafe_allow_html=True)
        files = st.file_uploader("r", type=["pdf","docx","txt"],
                                 accept_multiple_files=True,
                                 label_visibility="collapsed",
                                 help="Upload up to 20 candidate resumes at once. "
                                      "Tip: Use text-based PDFs for best accuracy.")
        if files:
            st.success(f"✅  {len(files)} file(s) ready to screen")
            for f in files[:5]:
                ico = "📄" if f.name.lower().endswith("pdf") else \
                      "📝" if f.name.lower().endswith("docx") else "📃"
                st.markdown(
                    f"<div style='font-size:.78rem;color:{C['sub']};padding:1px 0'>"
                    f"{ico} {f.name}</div>",
                    unsafe_allow_html=True)
            if len(files) > 5:
                st.caption(f"+ {len(files)-5} more")

    st.markdown("<br>", unsafe_allow_html=True)
    b1, b2 = st.columns([3,7])
    with b1:
        run_btn = st.button("🚀  Run AI Screening", use_container_width=True)
    with b2:
        st.markdown(
            f"<div style='color:{C['sub']};font-size:.8rem;padding:10px 0'>"
            f"AI will parse all resumes, compute TF-IDF similarity, match skills, "
            f"and rank candidates automatically. "
            f"<b style='color:{C['txt']}'>DEI-neutral</b> — scores text only, no name/gender bias."
            f"</div>",
            unsafe_allow_html=True)

else:
    # After screening: compact re-screen expander
    with st.expander("➕  Screen Additional Candidates"):
        c1, c2 = st.columns(2, gap="large")
        with c1:
            jd = st.text_area("jd2", height=160,
                              value=st.session_state.jd_text,
                              label_visibility="collapsed")
            if jd: st.session_state.jd_text = jd
        with c2:
            files = st.file_uploader("r2", type=["pdf","docx","txt"],
                                     accept_multiple_files=True,
                                     label_visibility="collapsed")
        run_btn = st.button("🔄  Re-run Screening", use_container_width=True)

# ── Screening engine  O(n·m) ──────────────────────────────────────────────────
if run_btn:
    jd_run = st.session_state.jd_text
    files_run = files if 'files' in dir() and files else []
    if not jd_run.strip():
        st.error("⚠️  Please enter a job description first.")
    elif not files_run:
        st.error("⚠️  Please upload at least one resume.")
    else:
        tw_f, sw_f = tw/100, (100-tw)/100
        pb = st.progress(0, "Initialising AI engine...")

        pb.progress(8, "Parsing job description...")
        cjd = preprocess(jd_run)
        jd_skills = extract_skills(jd_run)

        raw, clean = {}, {}
        for i, f in enumerate(files_run):
            pb.progress(8 + int(54*(i/len(files_run))),
                        f"Reading {f.name} ({i+1}/{len(files_run)})...")
            raw[f.name]   = extract_text(f)
            clean[f.name] = preprocess(raw[f.name])

        pb.progress(66, "Computing TF-IDF similarity vectors...")
        ranked = rank_resumes(cjd, clean)

        pb.progress(82, "Extracting skills & computing scores...")
        results, rows = [], []
        pipe = {"Shortlist":[], "Review":[], "Pass":[]}

        for i, item in enumerate(ranked):
            fn = item["resume"]
            ts = item["score"]
            rs = extract_skills(raw[fn])
            mat, mis, sp = get_skill_match(jd_skills, rs)
            comp = round(tw_f*ts + sw_f*sp, 2)
            dl, dc, _ = decision(comp, ht)

            results.append({
                "Rank":i+1, "Resume":fn,
                "Match Score (%)":ts, "Skill Match (%)":sp,
                "Final Score (%)":comp, "Recommendation":dl,
                "Matched Skills":", ".join(mat) or "—",
                "Missing Skills":", ".join(mis) or "None",
            })
            rows.append({
                "rank":i+1, "fn":fn, "ts":ts, "sp":sp,
                "comp":comp, "dl":dl, "dc":dc,
                "mat":mat, "mis":mis, "rs":rs,
            })
            stage = "Shortlist" if comp>=ht else "Review" if comp>=45 else "Pass"
            pipe[stage].append({"name":fn, "score":comp, "dc":dc})

        pb.progress(100, "✅  Screening complete!"); time.sleep(0.3); pb.empty()

        df  = pd.DataFrame(results)
        ddf = df[["Rank","Resume","Match Score (%)","Skill Match (%)",
                  "Final Score (%)","Recommendation","Matched Skills","Missing Skills"]]
        st.session_state.update({
            "results_df":df, "display_df":ddf, "jd_skills":jd_skills,
            "n_resumes":len(files_run), "detail_rows":rows,
            "screened":True, "pipeline":pipe,
        })
        st.rerun()

# ── Results ───────────────────────────────────────────────────────────────────
if st.session_state.screened:
    df   = st.session_state.results_df
    jds  = st.session_state.jd_skills
    nr   = st.session_state.n_resumes
    rows = st.session_state.detail_rows
    pipe = st.session_state.pipeline

    # Search + sort  O(n log n)
    sq = st.session_state.get("sq","")
    if sq:
        rows = [r for r in rows if sq.lower() in r["fn"].lower()]
        df   = df[df["Resume"].str.lower().str.contains(sq.lower(), na=False)]
    df = df.sort_values(
        st.session_state.get("sc","Final Score (%)"),
        ascending=st.session_state.get("sa",False))

    hired  = len(pipe.get("Shortlist",[]))
    review = len(pipe.get("Review",[]))
    passe  = len(pipe.get("Pass",[]))
    top    = max(st.session_state.detail_rows, key=lambda r: r["comp"])
    avg_s  = st.session_state.results_df["Final Score (%)"].mean()
    top_s  = st.session_state.results_df["Final Score (%)"].max()

    tab1, tab2, tab3 = st.tabs(["📋  Screening", "📊  Analytics", "👥  Pipeline"])

    with tab1:
        # ── KPI Row ───────────────────────────────────────────────────────────────
        st.markdown(
            f'<div class="kpi-row">'
            f'<div class="kpi" style="--c:{C["pri"]}">'
            f'<div class="kpi-ico">📄</div><div class="kpi-val">{nr}</div>'
            f'<div class="kpi-lbl">Screened</div>'
            f'<div class="kpi-sub">Batch processed automatically</div></div>'
            f'<div class="kpi" style="--c:{C["grn"]}">'
            f'<div class="kpi-ico">✅</div><div class="kpi-val">{hired}</div>'
            f'<div class="kpi-lbl">Shortlisted</div>'
            f'<div class="kpi-sub" style="color:{C["grn"]}!important">'
            f'{round(hired/nr*100) if nr else 0}% pass rate</div></div>'
            f'<div class="kpi" style="--c:{C["amb"]}">'
            f'<div class="kpi-ico">🏆</div><div class="kpi-val">{top_s:.0f}%</div>'
            f'<div class="kpi-lbl">Top Score</div>'
            f'<div class="kpi-sub">Avg: {avg_s:.0f}%</div></div>'
            f'<div class="kpi" style="--c:{C["sec"]}">'
            f'<div class="kpi-ico">🔧</div><div class="kpi-val">{len(jds)}</div>'
            f'<div class="kpi-lbl">JD Skills</div>'
            f'<div class="kpi-sub">Extracted from description</div></div>'
            f'</div>',
            unsafe_allow_html=True)

        # ── Hero: Top Candidate ───────────────────────────────────────────────────
        tdl, tdc, _ = decision(top["comp"], ht)
        top_chips   = chips(top["mat"][:7], "c-ok")
        st.markdown(
            f'<div class="hero">'
            f'<div class="hero-av">🏆</div>'
            f'<div style="flex:1;min-width:0">'
            f'<div class="hero-name">{top["fn"]}</div>'
            f'<div class="hero-meta">'
            f'Rank #1 · TF-IDF: {top["ts"]:.1f}% · Skill Match: {top["sp"]:.1f}% · '
            f'{len(top["mat"])} / {len(jds)} skills matched</div>'
            f'<div style="margin-bottom:10px">'
            f'<span class="badge {tdc}">{tdl}</span>'
            f'<span style="font-size:.75rem;color:rgba(255,255,255,.5);margin-left:10px">'
            f'Highest scoring candidate for this role</span></div>'
            f'<div>{top_chips}</div></div>'
            f'<div class="hero-score">'
            f'<div class="hero-num">{top["comp"]:.1f}%</div>'
            f'<div class="hero-slbl">Final Score</div></div></div>',
            unsafe_allow_html=True)


    with tab3:
        # ── Pipeline Kanban ───────────────────────────────────────────────────────
        st.markdown('<div class="stitle">👥 Hiring Pipeline</div>', unsafe_allow_html=True)
        stages = [("Shortlist",C["grn"]), ("Review",C["amb"]), ("Pass",C["red"])]
        pcols  = st.columns(3)
        for col, (stage, sc_) in zip(pcols, stages):
            with col:
                cands = pipe.get(stage, [])
                cards = "".join(
                    f'<div class="pipe-card" style="--pc:{sc_}">'
                    f'<div class="pc-name">{c["name"]}</div>'
                    f'<div class="pc-score">{c["score"]:.1f}% match</div></div>'
                    for c in cands
                ) or (f'<div style="text-align:center;padding:14px;'
                      f'font-size:.78rem;color:{C["sub"]}">No candidates</div>')
                ico = "✅" if stage=="Shortlist" else "🔍" if stage=="Review" else "❌"
                st.markdown(
                    f'<div class="pipe-col">'
                    f'<div class="pipe-hdr">'
                    f'<span class="pipe-title">'
                    f'<span class="pipe-dot" style="background:{sc_}"></span>'
                    f'{ico} {stage}</span>'
                    f'<span class="pipe-count" style="--pc:{sc_}">{len(cands)}</span>'
                    f'</div>{cards}</div>',
                    unsafe_allow_html=True)

        # ── Results table ─────────────────────────────────────────────────────────
        st.markdown('<div class="stitle">📊 Ranked Candidates</div>', unsafe_allow_html=True)
        show = df[["Rank","Resume","Match Score (%)","Skill Match (%)",
                   "Final Score (%)","Recommendation","Matched Skills","Missing Skills"]]
        st.dataframe(show, use_container_width=True, hide_index=True, column_config={
            "Rank":            st.column_config.NumberColumn("Rank",   width="small"),
            "Resume":          st.column_config.TextColumn("Candidate",width="medium"),
            "Match Score (%)": st.column_config.NumberColumn("TF-IDF", format="%.1f", width="small"),
            "Skill Match (%)": st.column_config.NumberColumn("Skills", format="%.1f", width="small"),
            "Final Score (%)": st.column_config.ProgressColumn("Score",format="%.1f",
                               min_value=0, max_value=100, width="medium"),
            "Recommendation":  st.column_config.TextColumn("Decision", width="medium"),
            "Matched Skills":  st.column_config.TextColumn("Matched",  width="large"),
            "Missing Skills":  st.column_config.TextColumn("Missing",  width="large"),
        })


    with tab2:
        # ── Analytics row ─────────────────────────────────────────────────────────
        st.markdown('<div class="stitle">📈 Analytics</div>', unsafe_allow_html=True)
        pdf = st.session_state.results_df
        CL  = dict(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                   font=dict(color=C["sub"], size=11, family="Inter"),
                   title_font=dict(color=C["sub"], size=10, family="Inter"),
                   margin=dict(t=34, b=50, l=6, r=6))
        AX  = dict(showgrid=False, tickfont=dict(color=C["sub"], size=10))
        AY  = dict(gridcolor=C["bdr"], tickfont=dict(color=C["sub"], size=10))

        a1, a2, a3 = st.columns(3)
        with a1:
            f1 = px.bar(pdf, x="Resume", y="Final Score (%)", text="Final Score (%)",
                        color="Final Score (%)", title="Final Score by Candidate",
                        color_continuous_scale=["#EF4444","#F97316","#F59E0B","#10B981"],
                        range_color=[0,100])
            f1.update_traces(texttemplate="%{text:.1f}%", textposition="outside",
                             marker_line_width=0)
            f1.update_layout(**CL, showlegend=False, coloraxis_showscale=False,
                             xaxis={**AX,"tickangle":-25}, yaxis={**AY,"range":[0,112]})
            st.plotly_chart(f1, use_container_width=True)

        with a2:
            f2 = go.Figure([
                go.Bar(name="TF-IDF Similarity", x=pdf["Resume"],
                       y=pdf["Match Score (%)"],  marker_color=C["pri"],
                       text=pdf["Match Score (%)"],
                       texttemplate="%{text:.0f}%", textposition="outside",
                       marker_line_width=0),
                go.Bar(name="Skill Match", x=pdf["Resume"],
                       y=pdf["Skill Match (%)"], marker_color=C["sec"],
                       text=pdf["Skill Match (%)"],
                       texttemplate="%{text:.0f}%", textposition="outside",
                       marker_line_width=0),
            ])
            f2.update_layout(**CL, barmode="group", title="Component Scores",
                             xaxis={**AX,"tickangle":-25}, yaxis={**AY,"range":[0,112]},
                             legend=dict(orientation="h",y=1.1,
                                         font=dict(color=C["sub"],size=9)))
            st.plotly_chart(f2, use_container_width=True)

        with a3:
            # Hiring funnel (horizontal bars — like Greenhouse analytics)
            st.markdown(
                f'<div style="font-size:.68rem;font-weight:700;color:{C["sub"]};'
                f'text-transform:uppercase;letter-spacing:.8px;margin-bottom:10px">'
                f'Hiring Funnel</div>',
                unsafe_allow_html=True)
            funnel_data = [
                ("Applied",    nr,      C["pri"],  "All resumes submitted"),
                ("Reviewed",   nr,      C["pur"],  "Processed by AI"),
                ("Shortlisted",hired,   C["grn"],  "Meet hire threshold"),
                ("Review",     review,  C["amb"],  "Need manual review"),
                ("Passed",     passe,   C["red"],  "Below threshold"),
            ]
            for lbl, val, col, hint in funnel_data:
                w = round((val/nr)*100) if nr else 0
                st.markdown(
                    f'<div class="funnel-row">'
                    f'<div class="funnel-lbl">{lbl}</div>'
                    f'<div class="funnel-bar">'
                    f'<div class="funnel-fill" style="width:{w}%;background:{col}">'
                    f'{val}</div></div>'
                    f'<div class="funnel-n">{val}</div>'
                    f'</div>',
                    unsafe_allow_html=True)


    with tab1:
        # ── Candidate profiles ────────────────────────────────────────────────────
        st.markdown('<div class="stitle">👤 Candidate Profiles</div>',
                    unsafe_allow_html=True)

        icons = {1:"🥇", 2:"🥈", 3:"🥉"}
        for row in rows:
            dl, dc, dcol = decision(row["comp"], ht)
            ri = icons.get(row["rank"], f"#{row['rank']}")
            with st.expander(
                f"{ri}  {row['fn']}  —  {row['comp']:.1f}%  —  {dl}"
            ):
                # Profile header
                ph1, ph2 = st.columns([1,3], gap="large")
                with ph1:
                    st.markdown(
                        f"<div style='text-align:center;padding:6px 0'>"
                        f"{gauge(row['comp'])}"
                        f"<div style='margin-top:6px'>"
                        f"<span class='badge {dc}'>{dl}</span></div></div>",
                        unsafe_allow_html=True)
                with ph2:
                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("TF-IDF",        f"{row['ts']:.1f}%")
                    m2.metric("Skill Match",   f"{row['sp']:.1f}%")
                    m3.metric("Final Score",   f"{row['comp']:.1f}%")
                    m4.metric("Skills Found",  f"{len(row['rs'])}")

                    # Score bars
                    for lbl, val, col in [
                        ("Content Match (TF-IDF)",  row["ts"],   C["pri"]),
                        ("Skill Coverage",           row["sp"],   C["sec"]),
                        ("Final Composite Score",    row["comp"], dcol),
                    ]:
                        st.markdown(
                            f'<div style="display:flex;justify-content:space-between;'
                            f'font-size:.72rem;color:{C["sub"]};margin-top:6px">'
                            f'<span>{lbl}</span>'
                            f'<span style="font-weight:700;color:{C["txt"]}">{val:.1f}%</span>'
                            f'</div>' + pbar(val, col),
                            unsafe_allow_html=True)

                st.markdown("<hr>", unsafe_allow_html=True)

                # Skills grid
                sk1, sk2 = st.columns(2)
                with sk1:
                    n_mat = len(row["mat"])
                    st.markdown(
                        f"<div style='font-size:.65rem;font-weight:700;color:{C['pri']};"
                        f"text-transform:uppercase;letter-spacing:1px;margin-bottom:6px'>"
                        f"✅ Matched Skills ({n_mat})</div>",
                        unsafe_allow_html=True)
                    st.markdown(
                        chips(row["mat"],"c-ok") or
                        f"<span style='color:{C['sub']};font-size:.8rem'>None detected</span>",
                        unsafe_allow_html=True)
                with sk2:
                    n_mis = len(row["mis"])
                    st.markdown(
                        f"<div style='font-size:.65rem;font-weight:700;color:{C['pri']};"
                        f"text-transform:uppercase;letter-spacing:1px;margin-bottom:6px'>"
                        f"❌ Missing Skills ({n_mis})</div>",
                        unsafe_allow_html=True)
                    st.markdown(
                        chips(row["mis"],"c-no") or
                        f"<span style='color:{C['grn']};font-size:.8rem;font-weight:600'>"
                        f"✅ All required skills present!</span>",
                        unsafe_allow_html=True)

                st.markdown(
                    f"<div style='font-size:.65rem;font-weight:700;color:{C['pri']};"
                    f"text-transform:uppercase;letter-spacing:1px;margin:12px 0 6px'>"
                    f"📋 All Skills in Resume ({len(row['rs'])})</div>",
                    unsafe_allow_html=True)
                st.markdown(
                    chips(row["rs"],"c-base") or
                    f"<span style='color:{C['red']};font-size:.78rem'>"
                    f"⚠️ No skills detected — likely image-based PDF. Ask candidate "
                    f"for a text-based PDF for accurate screening.</span>",
                    unsafe_allow_html=True)

                # Recruiter Notes (persisted in session state)
                st.markdown(
                    f"<div style='font-size:.65rem;font-weight:700;color:{C['pri']};"
                    f"text-transform:uppercase;letter-spacing:1px;margin:14px 0 6px'>"
                    f"📝 Recruiter Notes</div>",
                    unsafe_allow_html=True)
                note = st.text_area(
                    f"note_{row['fn']}", height=68,
                    placeholder="Add notes, observations, or interview reminders...",
                    label_visibility="collapsed",
                    value=st.session_state.notes.get(row["fn"],""),
                    key=f"note_{row['fn']}")
                if note != st.session_state.notes.get(row["fn"],""):
                    st.session_state.notes[row["fn"]] = note

        # ── Score filter ──────────────────────────────────────────────────────────
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown('<div class="stitle">🎚️ Score Filter</div>', unsafe_allow_html=True)
        fc1, fc2 = st.columns([5,1])
        with fc1:
            thr = st.slider("Threshold", 0, 100, 30, 5, format="%d%%", key="thr")
        with fc2:
            q = len(st.session_state.results_df[
                st.session_state.results_df["Final Score (%)"] >= thr])
            st.markdown(
                f"<div style='padding-top:28px;font-size:.82rem;color:{C['sub']}'>"
                f"<b style='color:{C['txt']}'>{q}</b> / {nr}</div>",
                unsafe_allow_html=True)

        filt = st.session_state.results_df[
            st.session_state.results_df["Final Score (%)"] >= thr]
        if len(filt):
            st.dataframe(
                filt[["Rank","Resume","Final Score (%)","Recommendation",
                      "Matched Skills","Missing Skills"]],
                use_container_width=True, hide_index=True)
        else:
            st.warning("No candidates meet this threshold. Lower the slider to see more.")

        # JD skills reference
        with st.expander(f"📌 JD Skills Detected ({len(jds)})"):
            st.markdown(
                chips(jds,"c-base") or "No skills detected",
                unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(
    f'<div class="foot">'
    f'🎯 <b style="color:{C["txt"]}">RecruitAI v5.0</b>'
    f' — Enterprise AI Hiring Platform &nbsp;·&nbsp;'
    f' Python · Streamlit · scikit-learn · NLTK · plotly'
    f' &nbsp;·&nbsp; <b style="color:{C["txt"]}">ADIT, CVM University</b>'
    f' &nbsp;·&nbsp; 202040601 &nbsp;·&nbsp;'
    f' <span style="color:{C["pri"]};font-weight:700">Dubal Prayag J</span>'
    f'</div>',
    unsafe_allow_html=True)