# app.py — Resume Screener Pro
# Semantic AI scoring with sentence-transformers, skill matching & explainable AI

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils.pdf_parser      import extract_text
from utils.scorer          import rank_resumes
from utils.skill_extractor import extract_skills, get_skill_match

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Resume Screener Pro",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS — modern premium theme ─────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
  
  /* ── Global SaaS Colors ── */
  :root {
      --bg-main: #f8fafc;        /* slate-50 */
      --bg-card: #ffffff;        /* white */
      --border-color: #e2e8f0;   /* slate-200 */
      --text-main: #0f172a;      /* slate-900 */
      --text-muted: #64748b;     /* slate-500 */
      --primary: #4f46e5;        /* indigo-600 */
      --primary-hover: #4338ca;  /* indigo-700 */
      --success: #059669;        /* emerald-600 */
      --warning: #d97706;        /* amber-600 */
      --danger: #dc2626;         /* red-600 */
      
      --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
      --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
  }

  html, body, [class*="css"] {
      font-family: 'Inter', sans-serif !important;
      color: var(--text-main);
  }
  [data-testid="stAppViewContainer"] {
      background-color: var(--bg-main);
  }
  [data-testid="stHeader"] {
      background: transparent;
  }
  
  /* ── Text Elements ── */
  p, div, span, label, .stMarkdown p {
      color: #334155 !important; /* slate-700 */
  }
  h1, h2, h3, h4, .card-title {
      color: var(--text-main) !important;
      font-weight: 700;
  }
  [data-testid="stMetricLabel"] > div {
      color: var(--text-muted) !important;
      font-weight: 600;
  }
  [data-testid="stMetricValue"] > div {
      color: var(--text-main) !important;
  }

  /* ── Top banner ── */
  .top-banner {
      background-color: var(--bg-card);
      padding: 40px 48px;
      border-radius: 16px;
      margin-bottom: 32px;
      border: 1px solid var(--border-color);
      box-shadow: var(--shadow-md);
      border-top: 4px solid var(--primary);
  }
  .top-banner h1 {
      font-size: 2.25rem;
      margin: 0 0 12px 0;
      letter-spacing: -0.025em;
  }
  .top-banner p {
      font-size: 1.1rem;
      color: var(--text-muted) !important;
      margin: 0;
  }

  /* ── Section cards ── */
  .card-title {
      font-size: 1.15rem;
      margin-bottom: 16px;
      display: flex;
      align-items: center;
      gap: 10px;
      color: var(--text-main);
  }
  .card-title svg {
      color: var(--primary) !important;
  }

  /* ── Stat badges ── */
  .stat-row {
      display: flex;
      gap: 24px;
      margin-bottom: 40px;
      flex-wrap: wrap;
  }
  .stat-box {
      flex: 1;
      min-width: 180px;
      background: var(--bg-card);
      border-radius: 12px;
      padding: 24px;
      border: 1px solid var(--border-color);
      box-shadow: var(--shadow-sm);
      position: relative;
      overflow: hidden;
  }
  .stat-val {
      font-size: 2.5rem;
      font-weight: 700;
      color: var(--text-main);
      line-height: 1;
      margin-bottom: 8px;
  }
  .stat-lbl {
      font-size: 0.85rem;
      color: var(--text-muted);
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.05em;
  }

  /* ── Rank & Score Colors ── */
  .rank-1 { color: var(--warning); font-weight: 700; }
  .rank-2 { color: #475569; font-weight: 600; } /* slate-600 */
  .rank-3 { color: #b45309; font-weight: 600; }
  
  .score-high { color: var(--success); font-weight: 600; }
  .score-mid  { color: var(--primary); font-weight: 600; }
  .score-low  { color: var(--danger); font-weight: 600; }

  /* ── Skill tags ── */
  .skill-tag {
      display: inline-flex;
      align-items: center;
      background: #e0e7ff; /* indigo-100 */
      color: #3730a3;      /* indigo-800 */
      border: 1px solid #c7d2fe; /* indigo-200 */
      border-radius: 9999px;
      padding: 4px 12px;
      font-size: 0.85rem;
      margin: 4px 6px 4px 0;
      font-weight: 500;
  }
  .skill-tag.missing {
      background: #fee2e2; /* red-100 */
      color: #991b1b;      /* red-800 */
      border-color: #fca5a5; /* red-300 */
  }

  /* ── Inputs (Text Area & Uploader) ── */
  div[data-baseweb="textarea"] > div,
  section[data-testid="stFileUploadDropzone"] {
      background-color: var(--bg-card) !important;
      border: 1px solid var(--border-color) !important;
      border-radius: 8px !important;
      transition: border-color 0.2s;
  }
  div[data-baseweb="textarea"] > div:focus-within {
      border-color: var(--primary) !important;
      box-shadow: 0 0 0 1px var(--primary) !important;
  }
  div[data-baseweb="textarea"] textarea {
      color: var(--text-main) !important;
  }

  /* ── Button ── */
  .stButton > button {
      background-color: var(--primary) !important;
      border: none;
      width: 100%;
      box-shadow: var(--shadow-sm);
      transition: background-color 0.2s;
      padding: 12px 24px;
      border-radius: 8px;
  }
  .stButton > button p {
      color: #ffffff !important;
      font-weight: 600;
      font-size: 1.05rem;
      margin: 0;
  }
  .stButton > button:hover { 
      background-color: var(--primary-hover) !important;
  }

  /* ── Expander & DataFrame Wrapper ── */
  [data-testid="stExpander"] {
      background: var(--bg-card);
      border-radius: 8px;
      border: 1px solid var(--border-color);
      margin-bottom: 12px;
      box-shadow: var(--shadow-sm);
  }
  
  [data-testid="stDataFrame"] {
      border-radius: 8px;
      border: 1px solid var(--border-color);
  }

  /* ── Divider ── */
  hr { 
      border-color: var(--border-color); 
      margin: 32px 0; 
  }

</style>
""", unsafe_allow_html=True)

# ── Header banner ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="top-banner">
  <h1>Intelligent Resume Screening</h1>
  <p>Upload a job description and multiple resumes to get instant, data-driven candidate rankings and skill match insights.</p>
</div>
""", unsafe_allow_html=True)

# ── Input layout: two columns ─────────────────────────────────────────────────
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown("""
    <div class="card-title">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
      Job Description
    </div>
    """, unsafe_allow_html=True)
    jd_text = st.text_area(
        label="Job Description",
        height=280,
        placeholder="Paste the job description here...\n\nInclude skills, responsibilities, and requirements for best results.",
        label_visibility="collapsed",
    )

with col2:
    st.markdown("""
    <div class="card-title">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path></svg>
      Upload Resumes
    </div>
    """, unsafe_allow_html=True)
    uploaded_files = st.file_uploader(
        label="Upload Resumes",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
        label_visibility="collapsed",
        help="Upload PDF, DOCX, or TXT resume files. You can select multiple files at once.",
    )
    if uploaded_files:
        st.success(f"{len(uploaded_files)} resume(s) uploaded successfully.")

st.markdown("<br>", unsafe_allow_html=True)

# ── Screen button ─────────────────────────────────────────────────────────────
btn_col, _ = st.columns([2, 5])
with btn_col:
    screen_btn = st.button("Analyze Candidates", use_container_width=True)

# ── Main logic ────────────────────────────────────────────────────────────────
if screen_btn:
    if not jd_text.strip():
        st.error("Please enter a job description before screening.")
    elif not uploaded_files:
        st.error("Please upload at least one resume file.")
    else:
        with st.spinner("AI is analyzing resumes — this may take a moment on first run while loading the language model..."):

            # ── Step 1: Process JD (raw for semantics, extract skills from raw) ─
            jd_skills  = extract_skills(jd_text)

            # ── Step 2: Process each resume ─────────────────────────────────
            resumes_raw = {}

            for file in uploaded_files:
                raw = extract_text(file)
                resumes_raw[file.name] = raw

            # ── Step 3: Rank by semantic similarity (batch, raw text) ─────────
            # We pass raw text directly — preprocessing degrades embedding quality
            ranked = rank_resumes(jd_text, resumes_raw)

            # ── Step 4: Build results table ─────────────────────────────────
            results = []
            for item in ranked:
                fname          = item["resume"]
                semantic_score = item["score"]   # ← renamed from tfidf_score
                resume_skills  = extract_skills(resumes_raw[fname])
                matched, missing, skill_pct = get_skill_match(jd_skills, resume_skills)

                # Composite: 35% Semantic + 65% Skill Match
                # Skill match weighted higher so low-skill candidates cannot inflate score
                composite = round(0.35 * semantic_score + 0.65 * skill_pct, 2)

                results.append({
                    "Resume":           fname,
                    "Match Score (%)":  semantic_score,
                    "Skill Match (%)":  skill_pct,
                    "Final Score (%)":  composite,
                    "Matched Skills":   ", ".join(matched)  if matched else "—",
                    "Missing Skills":   ", ".join(missing)  if missing else "None",
                    "_matched_list":    matched,
                    "_missing_list":    missing,
                    "_resume_skills":   resume_skills,
                })

        df = pd.DataFrame(results)
        
        # FIX: The sorting issue where rank didn't match the final score. 
        # We sort by Final Score descending *after* calculating it for all resumes, then assign ranks.
        df = df.sort_values(by="Final Score (%)", ascending=False).reset_index(drop=True)
        df.insert(0, "Rank", df.index + 1)

        st.markdown("---")

        # ── Summary stats ─────────────────────────────────────────────────────
        top_score  = df["Final Score (%)"].max()
        avg_score  = df["Final Score (%)"].mean()
        top_resume = df.loc[0, "Resume"] if not df.empty else "N/A"
        top_skills_matched = len(df.loc[0, "_matched_list"]) if not df.empty else 0

        # Top Candidate highlight
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #f0f9ff 0%, #e0e7ff 100%); border: 1.5px solid #a5b4fc; border-radius: 14px; padding: 24px 32px; margin-bottom: 24px; display:flex; align-items:center; gap:20px;">
          <div style="font-size:2.8rem;">🏆</div>
          <div>
            <div style="font-size:0.78rem; font-weight:700; color:#4f46e5; text-transform:uppercase; letter-spacing:0.08em;">Top Candidate</div>
            <div style="font-size:1.5rem; font-weight:700; color:#0f172a; margin: 2px 0;">{top_resume}</div>
            <div style="color:#6366f1; font-size:0.95rem;">Final Score: <b>{top_score:.1f}%</b> &nbsp;·&nbsp; Matched <b>{top_skills_matched}</b> required skills</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="stat-row">
          <div class="stat-box">
            <div class="stat-val">{len(uploaded_files)}</div>
            <div class="stat-lbl">Resumes Screened</div>
          </div>
          <div class="stat-box">
            <div class="stat-val">{len(jd_skills)}</div>
            <div class="stat-lbl">Skills in JD</div>
          </div>
          <div class="stat-box">
            <div class="stat-val score-high">{top_score:.1f}%</div>
            <div class="stat-lbl">Top Match Score</div>
          </div>
          <div class="stat-box">
            <div class="stat-val">{avg_score:.1f}%</div>
            <div class="stat-lbl">Average Score</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Results table ─────────────────────────────────────────────────────
        st.markdown("### Screening Results")

        display_df = df[[
            "Rank", "Resume",
            "Match Score (%)", "Skill Match (%)", "Final Score (%)",
            "Matched Skills", "Missing Skills"
        ]].copy()

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Rank":            st.column_config.NumberColumn("Rank",  width="small"),
                "Resume":          st.column_config.TextColumn("Resume File", width="medium"),
                "Match Score (%)": st.column_config.NumberColumn("Semantic Match %", format="%.1f", width="small"),
                "Skill Match (%)": st.column_config.NumberColumn("Skill Match %",  format="%.1f", width="small"),
                "Final Score (%)": st.column_config.ProgressColumn("Final Score %", format="%.1f", min_value=0, max_value=100, width="medium"),
                "Matched Skills":  st.column_config.TextColumn("Matched Skills",  width="large"),
                "Missing Skills":  st.column_config.TextColumn("Missing Skills",  width="large"),
            }
        )

        # ── Bar chart ─────────────────────────────────────────────────────────
        st.markdown("### Score Comparison")

        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            fig1 = px.bar(
                df,
                x="Resume",
                y="Final Score (%)",
                color="Final Score (%)",
                color_continuous_scale=["#ef4444", "#f59e0b", "#10b981"],
                range_color=[0, 100],
                text="Final Score (%)",
                title="Final Score per Candidate",
                labels={"Resume": "Candidate", "Final Score (%)": "Final Score (%)"},
            )
            fig1.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
            fig1.update_layout(
                plot_bgcolor="#ffffff",
                paper_bgcolor="#ffffff",
                font_color="#374151",
                showlegend=False,
                coloraxis_showscale=False,
                title_font_size=16,
                title_font_color="#111827",
                xaxis_tickangle=-30,
                margin=dict(t=50, b=60),
            )
            fig1.update_xaxes(showgrid=False, zeroline=False)
            fig1.update_yaxes(showgrid=True, gridcolor="#e5e7eb", zeroline=False)
            st.plotly_chart(fig1, use_container_width=True)

        with chart_col2:
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(
                name="Semantic Match",
                x=df["Resume"],
                y=df["Match Score (%)"],
                marker_color="#8b5cf6",
            ))
            fig2.add_trace(go.Bar(
                name="Skill Match",
                x=df["Resume"],
                y=df["Skill Match (%)"],
                marker_color="#3b82f6",
            ))
            fig2.update_layout(
                barmode="group",
                title={"text": "Semantic vs Skill Match Score", "y": 0.95},
                plot_bgcolor="#ffffff",
                paper_bgcolor="#ffffff",
                font_color="#374151",
                title_font_size=16,
                title_font_color="#111827",
                xaxis_tickangle=-30,
                margin=dict(t=80, b=60),
                legend=dict(orientation="h", yanchor="bottom", y=1.08, font_color="#374151"),
            )
            fig2.update_xaxes(showgrid=False, zeroline=False)
            fig2.update_yaxes(showgrid=True, gridcolor="#e5e7eb", zeroline=False)
            st.plotly_chart(fig2, use_container_width=True)

        # ── Candidate detail expanders ────────────────────────────────────────
        st.markdown("### Candidate Detail Analysis")

        for _, row in df.iterrows():
            rank    = int(row["Rank"])
            score   = row["Final Score (%)"]
            score_color = "score-high" if score >= 60 else ("score-mid" if score >= 40 else "score-low")

            with st.expander(f"Rank {rank} — {row['Resume']} (Score: {score:.1f}%)"):

                d1, d2, d3 = st.columns(3)
                d1.metric("Final Score",   f"{row['Final Score (%)']:.1f}%")
                d2.metric("Semantic Match",f"{row['Match Score (%)']:.1f}%")
                d3.metric("Skill Match",   f"{row['Skill Match (%)']:.1f}%")

                # Explainable AI Summary — thresholds adapt to actual score range
                st.markdown("<br>**AI Reasoning:**", unsafe_allow_html=True)
                top_score_in_batch = df["Final Score (%)"].max()
                high_threshold = max(65, top_score_in_batch * 0.80)  # top 80% of best score
                mid_threshold  = max(40, top_score_in_batch * 0.50)  # top 50% of best score

                if score >= high_threshold:
                    st.info(f"**Highly Recommended:** This candidate is an excellent fit. They possess {row['Skill Match (%)']:.0f}% of the required skills and their experience aligns very closely ({row['Match Score (%)']:.0f}% semantic match) with the core responsibilities.")
                elif score >= mid_threshold:
                    st.warning(f"**Potential Match:** This candidate shows promise with a {row['Skill Match (%)']:.0f}% skill match, but their overall experience profile ({row['Match Score (%)']:.0f}% semantic match) suggests they may need upskilling in certain areas.")
                else:
                    st.error(f"**Weak Match:** This candidate lacks critical requirements. They only match {row['Skill Match (%)']:.0f}% of the necessary skills and their resume does not strongly align with the job description.")
                st.markdown("<br>", unsafe_allow_html=True)

                st.markdown("**Matched Skills:**")
                matched_list = row["_matched_list"]
                if matched_list:
                    tags = " ".join([f'<span class="skill-tag">{s}</span>' for s in matched_list])
                    st.markdown(tags, unsafe_allow_html=True)
                else:
                    st.markdown("_No skills matched from JD_")

                st.markdown("<br>**Missing Skills:**", unsafe_allow_html=True)
                missing_list = row["_missing_list"]
                if missing_list:
                    tags = " ".join([f'<span class="skill-tag missing">{s}</span>' for s in missing_list])
                    st.markdown(tags, unsafe_allow_html=True)
                else:
                    st.markdown("All required skills are present.")

                st.markdown("<br>**All Skills Found in Resume:**", unsafe_allow_html=True)
                all_skills = row["_resume_skills"]
                if all_skills:
                    tags = " ".join([f'<span class="skill-tag">{s}</span>' for s in all_skills])
                    st.markdown(tags, unsafe_allow_html=True)
                else:
                    st.markdown("_No skills detected_")

        # ── Threshold filter ──────────────────────────────────────────────────
        st.markdown("---")
        st.markdown("### Filter by Minimum Score")

        threshold = st.slider(
            "Show only candidates with Final Score above:",
            min_value=0, max_value=100, value=40, step=5,
            format="%d%%"
        )
        filtered = df[df["Final Score (%)"] >= threshold]
        if len(filtered) > 0:
            st.info(f"**{len(filtered)}** candidate(s) meet the {threshold}% threshold.")
            st.dataframe(
                filtered[["Rank","Resume","Final Score (%)","Matched Skills"]],
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.warning(f"No candidates meet the {threshold}% threshold. Try lowering it.")

        # ── Download CSV ──────────────────────────────────────────────────────
        st.markdown("---")
        csv = display_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download Full Results as CSV",
            data=csv,
            file_name="resume_screening_results.csv",
            mime="text/csv",
            use_container_width=False,
        )

        # ── JD Skills reference ───────────────────────────────────────────────
        with st.expander("Skills Detected in Job Description"):
            if jd_skills:
                tags = " ".join([f'<span class="skill-tag">{s}</span>' for s in jd_skills])
                st.markdown(tags, unsafe_allow_html=True)
            else:
                st.warning("No skills detected in the JD. Try using the sample JDs provided.")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='text-align:center;color:#94a3b8;font-size:0.82rem;'>"
    "Resume Screener Pro &nbsp;·&nbsp; "
    "Powered by Sentence Transformers &amp; Streamlit &nbsp;·&nbsp; "
    "ADIT, CVM University &nbsp;·&nbsp; Mini Project 202040601"
    "</p>",
    unsafe_allow_html=True,
)