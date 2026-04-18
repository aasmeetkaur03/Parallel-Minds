"""
interface.py
------------
PURPOSE : Futuristic glassmorphism frontend for "Know What You Sign"
          Separate UI file — backend files are NOT modified.

HOW TO RUN:
    python -m streamlit run interface.py

BACKEND FILES USED (zero changes to them):
    extractor.py      — reads PDF/DOCX files
    analyzer.py       — sends text to Groq AI
    risk_formatter.py — parses and organizes risk output
    report.py         — builds downloadable report
"""

import streamlit as st
from extractor      import extract_text
from analyzer       import get_plain_summary, get_risk_map
from risk_formatter import parse_risk_output, count_risks
from report         import generate_report

# ── PAGE CONFIG ────────────────────────────────────────────
st.set_page_config(
    page_title="Know What You Sign",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── GLOBAL CSS ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Inter:wght@300;400;500;600&display=swap');

/* Hide default Streamlit chrome */
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
header    { visibility: hidden; }
.block-container { padding: 0 !important; max-width: 100% !important; }

/* ── BASE ── */
* { box-sizing: border-box; }

body, .stApp {
    background: linear-gradient(135deg, #07071a 0%, #0d0d2b 35%, #1a0a2e 65%, #0a1628 100%);
    min-height: 100vh;
    font-family: 'Inter', sans-serif;
    color: #e0e0ff;
}

/* Ambient glow layers */
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background:
        radial-gradient(ellipse at 20% 50%, rgba(79,70,229,0.07) 0%, transparent 55%),
        radial-gradient(ellipse at 80% 20%, rgba(139,92,246,0.07) 0%, transparent 55%),
        radial-gradient(ellipse at 50% 85%, rgba(59,130,246,0.04) 0%, transparent 55%);
    pointer-events: none;
    z-index: 0;
}

/* ── HERO ── */
.hero-section {
    text-align: center;
    padding: 56px 24px 36px;
    position: relative;
    z-index: 1;
}

.hero-title {
    font-family: 'Orbitron', monospace;
    font-size: clamp(2.2rem, 5.5vw, 4.8rem);
    font-weight: 900;
    background: linear-gradient(135deg, #a78bfa, #60a5fa, #34d399, #a78bfa);
    background-size: 300% 300%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: bubblePop 1.3s cubic-bezier(0.34, 1.56, 0.64, 1) both,
               gradientShift 5s ease infinite 1.3s;
    filter: drop-shadow(0 0 28px rgba(139,92,246,0.45));
    letter-spacing: 3px;
    line-height: 1.15;
}

@keyframes bubblePop {
    0%   { transform: scale(0.25); opacity: 0; filter: drop-shadow(0 0 0px rgba(139,92,246,0)); }
    55%  { transform: scale(1.1);  filter: drop-shadow(0 0 50px rgba(139,92,246,0.9)); }
    75%  { transform: scale(0.96); }
    90%  { transform: scale(1.02); }
    100% { transform: scale(1);    opacity: 1; filter: drop-shadow(0 0 25px rgba(139,92,246,0.45)); }
}

@keyframes gradientShift {
    0%,100% { background-position: 0% 50%; }
    50%     { background-position: 100% 50%; }
}

.hero-subtitle {
    font-size: 0.95rem;
    color: rgba(180,180,255,0.55);
    margin-top: 14px;
    letter-spacing: 2px;
    text-transform: uppercase;
    animation: fadeUp 1s ease 0.6s both;
}

@keyframes fadeUp {
    from { opacity: 0; transform: translateY(18px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* ── GLASS CARD ── */
.glass-card {
    background: rgba(255,255,255,0.035);
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 20px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.45),
                inset 0 1px 0 rgba(255,255,255,0.08);
    padding: 24px 28px;
    margin-bottom: 18px;
    transition: border-color 0.3s, box-shadow 0.3s;
}

.glass-card:hover {
    border-color: rgba(139,92,246,0.22);
    box-shadow: 0 8px 32px rgba(0,0,0,0.45),
                0 0 22px rgba(139,92,246,0.08),
                inset 0 1px 0 rgba(255,255,255,0.08);
}

.section-title {
    font-family: 'Orbitron', monospace;
    font-size: 0.62rem;
    letter-spacing: 3px;
    color: rgba(139,92,246,0.75);
    text-transform: uppercase;
    margin-bottom: 6px;
}

.panel-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: #e0e0ff;
    margin-bottom: 14px;
}

/* ── METRICS ROW ── */
.metrics-row {
    display: flex;
    gap: 10px;
    margin-bottom: 18px;
    animation: fadeUp 0.6s ease both;
}

.metric-chip {
    flex: 1;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px;
    padding: 14px 10px;
    text-align: center;
}

.metric-num {
    font-family: 'Orbitron', monospace;
    font-size: 1.9rem;
    font-weight: 700;
    line-height: 1;
}

.metric-lbl {
    font-size: 0.62rem;
    color: rgba(180,180,255,0.45);
    margin-top: 5px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
}

.metric-high   .metric-num { color: #ef4444; text-shadow: 0 0 16px rgba(239,68,68,0.55); }
.metric-medium .metric-num { color: #f59e0b; text-shadow: 0 0 16px rgba(245,158,11,0.55); }
.metric-low    .metric-num { color: #10b981; text-shadow: 0 0 16px rgba(16,185,129,0.55); }
.metric-total  .metric-num { color: #a78bfa; text-shadow: 0 0 16px rgba(167,139,250,0.55); }
.metric-total { background: rgba(124,58,237,0.07); border-color: rgba(124,58,237,0.18); flex: 1.5; }

/* ── RISK LEGEND ── */
.risk-legend {
    display: flex;
    gap: 20px;
    flex-wrap: wrap;
    margin-bottom: 18px;
    animation: fadeUp 0.7s ease 0.2s both;
}

.legend-item {
    display: flex;
    align-items: center;
    gap: 7px;
    font-size: 0.75rem;
    color: rgba(190,190,255,0.6);
}

.legend-dot {
    width: 9px; height: 9px;
    border-radius: 50%;
    flex-shrink: 0;
}

.dot-high   { background: #ef4444; box-shadow: 0 0 7px rgba(239,68,68,0.9); }
.dot-medium { background: #f59e0b; box-shadow: 0 0 7px rgba(245,158,11,0.9); }
.dot-low    { background: #10b981; box-shadow: 0 0 7px rgba(16,185,129,0.9); }

/* ── CLAUSE CARDS ── */
.clause-card {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,255,255,0.055);
    border-radius: 14px;
    padding: 15px 18px;
    margin-bottom: 10px;
    position: relative;
    overflow: hidden;
    transition: transform 0.3s cubic-bezier(0.4,0,0.2,1),
                box-shadow 0.3s, border-color 0.3s;
    animation: fadeUp 0.5s ease both;
}

.clause-card::before {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 3px;
    border-radius: 3px 0 0 3px;
}

.clause-card.high   { border-color: rgba(239,68,68,0.18); }
.clause-card.medium { border-color: rgba(245,158,11,0.18); }
.clause-card.low    { border-color: rgba(16,185,129,0.18); }

.clause-card.high::before   { background: #ef4444; box-shadow: 0 0 10px rgba(239,68,68,0.9); }
.clause-card.medium::before { background: #f59e0b; box-shadow: 0 0 10px rgba(245,158,11,0.9); }
.clause-card.low::before    { background: #10b981; box-shadow: 0 0 10px rgba(16,185,129,0.9); }

.clause-card:hover { transform: translateY(-3px); }
.clause-card.high:hover   { box-shadow: 0 10px 28px rgba(239,68,68,0.14); border-color: rgba(239,68,68,0.38); }
.clause-card.medium:hover { box-shadow: 0 10px 28px rgba(245,158,11,0.14); border-color: rgba(245,158,11,0.38); }
.clause-card.low:hover    { box-shadow: 0 10px 28px rgba(16,185,129,0.14); border-color: rgba(16,185,129,0.38); }

.risk-badge {
    display: inline-block;
    font-size: 0.6rem;
    font-weight: 700;
    letter-spacing: 1.8px;
    padding: 2px 9px;
    border-radius: 20px;
    margin-bottom: 8px;
    text-transform: uppercase;
}

.badge-high   { background: rgba(239,68,68,0.13); color: #f87171; border: 1px solid rgba(239,68,68,0.28); }
.badge-medium { background: rgba(245,158,11,0.13); color: #fbbf24; border: 1px solid rgba(245,158,11,0.28); }
.badge-low    { background: rgba(16,185,129,0.13); color: #34d399; border: 1px solid rgba(16,185,129,0.28); }

.clause-text  { font-size: 0.85rem; color: rgba(210,210,255,0.8); line-height: 1.55; margin-bottom: 5px; }
.clause-plain { font-size: 0.8rem;  color: rgba(160,160,220,0.6); font-style: italic; }
.clause-why   {
    font-size: 0.78rem;
    color: rgba(180,180,240,0.65);
    margin-top: 8px;
    padding-top: 8px;
    border-top: 1px solid rgba(255,255,255,0.04);
}

/* ── EXPLAIN PANEL ── */
.explain-card {
    background: rgba(139,92,246,0.05);
    border: 1px solid rgba(139,92,246,0.14);
    border-radius: 14px;
    padding: 16px 18px;
    margin-bottom: 10px;
    animation: fadeUp 0.5s ease both;
}

.explain-emoji { font-size: 1.3rem; margin-bottom: 7px; }

.explain-text    { font-size: 0.86rem; color: rgba(210,210,255,0.85); line-height: 1.65; }
.explain-analogy { font-size: 0.8rem;  color: rgba(167,139,250,0.65); font-style: italic; margin-top: 7px; }

/* ── RISK BARS ── */
.risk-bar-container { margin-bottom: 15px; }

.risk-bar-label {
    display: flex;
    justify-content: space-between;
    font-size: 0.76rem;
    color: rgba(180,180,255,0.65);
    margin-bottom: 5px;
}

.risk-bar-track {
    height: 7px;
    background: rgba(255,255,255,0.04);
    border-radius: 4px;
    overflow: hidden;
}

.risk-bar-fill {
    height: 100%;
    border-radius: 4px;
    animation: fillBar 1.6s cubic-bezier(0.4,0,0.2,1) both;
}

@keyframes fillBar {
    from { width: 0%; }
}

.bar-financial { background: linear-gradient(90deg,#ef4444,#f97316); box-shadow: 0 0 8px rgba(239,68,68,0.35); }
.bar-privacy   { background: linear-gradient(90deg,#a855f7,#6366f1); box-shadow: 0 0 8px rgba(168,85,247,0.35); }
.bar-legal     { background: linear-gradient(90deg,#f59e0b,#eab308); box-shadow: 0 0 8px rgba(245,158,11,0.35); }

/* ── STREAMLIT WIDGET OVERRIDES ── */
.stButton > button {
    background: linear-gradient(135deg,#7c3aed,#4f46e5) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 13px 36px !important;
    font-family: 'Orbitron', monospace !important;
    font-size: 0.78rem !important;
    letter-spacing: 2.5px !important;
    font-weight: 700 !important;
    width: 100% !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 22px rgba(124,58,237,0.4) !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 32px rgba(124,58,237,0.6) !important;
    background: linear-gradient(135deg,#8b5cf6,#6366f1) !important;
}

div[data-testid="stFileUploader"] {
    border: 2px dashed rgba(139,92,246,0.28) !important;
    border-radius: 16px !important;
    background: rgba(139,92,246,0.03) !important;
    transition: all 0.3s !important;
}

div[data-testid="stFileUploader"]:hover {
    border-color: rgba(139,92,246,0.55) !important;
    box-shadow: 0 0 24px rgba(139,92,246,0.12) !important;
}

.stSelectbox > div > div {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.09) !important;
    border-radius: 10px !important;
    color: #e0e0ff !important;
}

.stDownloadButton > button {
    background: rgba(16,185,129,0.12) !important;
    border: 1px solid rgba(16,185,129,0.28) !important;
    color: #34d399 !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    width: 100% !important;
    transition: all 0.3s !important;
}

.stDownloadButton > button:hover {
    background: rgba(16,185,129,0.22) !important;
    box-shadow: 0 0 20px rgba(16,185,129,0.18) !important;
}

.stRadio > div { gap: 8px !important; }

.stRadio > div > label {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 8px !important;
    padding: 5px 14px !important;
    color: rgba(200,200,255,0.7) !important;
    font-size: 0.8rem !important;
    transition: all 0.2s !important;
}

.stRadio > div > label:hover {
    border-color: rgba(139,92,246,0.35) !important;
    color: #a78bfa !important;
}

/* Spinner */
.stSpinner > div { border-top-color: #7c3aed !important; }

/* Scrollbar */
::-webkit-scrollbar       { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(139,92,246,0.35); border-radius: 2px; }

/* Alerts */
.status-ok  { background:rgba(16,185,129,0.08); border:1px solid rgba(16,185,129,0.22); border-radius:10px; padding:10px 16px; font-size:0.82rem; color:#34d399; }
.status-err { background:rgba(239,68,68,0.08);  border:1px solid rgba(239,68,68,0.22);  border-radius:10px; padding:10px 16px; font-size:0.82rem; color:#f87171; }
</style>
""", unsafe_allow_html=True)


# ── HERO ───────────────────────────────────────────────────
st.markdown("""
<div class="hero-section">
    <div class="hero-title">Know What You Sign</div>
    <div class="hero-subtitle">⚖️ &nbsp; AI-Powered Legal Intelligence &nbsp;·&nbsp; Plain Language &nbsp;·&nbsp; Risk Protection</div>
</div>
""", unsafe_allow_html=True)


# ── UPLOAD + SETTINGS ──────────────────────────────────────
with st.container():
    st.markdown('<div style="padding:0 28px;">', unsafe_allow_html=True)
    up_col, set_col = st.columns([3, 1], gap="medium")

    with up_col:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Step 1 — Upload Document</div>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "Upload your contract (PDF or DOCX)",
            type=["pdf", "docx"],
            help="Your file is processed locally and never stored."
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with set_col:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Document Type</div>', unsafe_allow_html=True)
        doc_type = st.selectbox(
            "Type",
            ["Rental Agreement", "Employment Contract", "Loan Agreement",
             "Terms of Service", "General Contract"],
            label_visibility="collapsed"
        )
        st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)
        analyze_btn = st.button("⚡  ANALYZE", type="primary")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


# ── EXTRACT TEXT ───────────────────────────────────────────
contract_text = ""
filename      = "document"

if uploaded_file:
    with st.spinner("Reading document..."):
        contract_text = extract_text(uploaded_file)
        filename      = uploaded_file.name

    st.markdown('<div style="padding:0 28px;margin-bottom:8px;">', unsafe_allow_html=True)
    if contract_text:
        wc = len(contract_text.split())
        st.markdown(f'<div class="status-ok">✓ &nbsp; Document loaded — {wc:,} words extracted from <b>{filename}</b></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-err">❌ &nbsp; Could not read this file. Try a newer PDF or paste text manually.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ── RUN ANALYSIS ───────────────────────────────────────────
if analyze_btn and contract_text:
    with st.spinner("Generating plain-language summary..."):
        st.session_state["summary"] = get_plain_summary(contract_text, doc_type)
    with st.spinner("Scanning for risky clauses..."):
        raw = get_risk_map(contract_text, doc_type)
        st.session_state["risks"]   = parse_risk_output(raw)
    st.session_state["doc_type"]    = doc_type
    st.session_state["filename"]    = filename

elif analyze_btn and not contract_text:
    st.markdown('<div style="padding:0 28px"><div class="status-err">❌ &nbsp; Please upload a document first.</div></div>', unsafe_allow_html=True)


# ── RESULTS ────────────────────────────────────────────────
if "risks" in st.session_state and "summary" in st.session_state:

    risks   = st.session_state["risks"]
    summary = st.session_state["summary"]
    counts  = count_risks(risks)
    total   = max(len(risks), 1)

    high_pct = int((counts["HIGH"]   / total) * 100)
    med_pct  = int((counts["MEDIUM"] / total) * 100)
    low_pct  = int((counts["LOW"]    / total) * 100)
    exp_pct  = min(high_pct + med_pct, 100)

    # Overall risk
    if counts["HIGH"] >= 3:
        overall, gauge_pct, g_color, g_cls = "HIGH",     82, "#ef4444", "gauge-high"
    elif counts["HIGH"] >= 1 or counts["MEDIUM"] >= 3:
        overall, gauge_pct, g_color, g_cls = "MODERATE", 51, "#f59e0b", "gauge-medium"
    else:
        overall, gauge_pct, g_color, g_cls = "LOW",      20, "#10b981", "gauge-low"

    # SVG gauge arc
    dash_val = int(gauge_pct * 2.36)

    st.markdown('<div style="padding:0 28px;">', unsafe_allow_html=True)

    # Metric chips
    st.markdown(f"""
    <div class="metrics-row">
        <div class="metric-chip metric-high">
            <div class="metric-num">{counts["HIGH"]}</div>
            <div class="metric-lbl">High Risk</div>
        </div>
        <div class="metric-chip metric-medium">
            <div class="metric-num">{counts["MEDIUM"]}</div>
            <div class="metric-lbl">Moderate</div>
        </div>
        <div class="metric-chip metric-low">
            <div class="metric-num">{counts["LOW"]}</div>
            <div class="metric-lbl">Low Risk</div>
        </div>
        <div class="metric-chip metric-total">
            <div class="metric-num">{len(risks)}</div>
            <div class="metric-lbl">Total Flagged</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Legend
    st.markdown("""
    <div class="risk-legend">
        <div class="legend-item"><div class="legend-dot dot-high"></div>High Risk — serious impact on rights or money</div>
        <div class="legend-item"><div class="legend-dot dot-medium"></div>Moderate — unfair but manageable</div>
        <div class="legend-item"><div class="legend-dot dot-low"></div>Low Risk — slightly unusual, minor impact</div>
    </div>
    """, unsafe_allow_html=True)

    # Two-column layout
    left_col, right_col = st.columns([3, 2], gap="large")

    # ── LEFT: Flagged Clauses ──────────────────────────────
    with left_col:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Document Analysis</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">Flagged Clauses</div>', unsafe_allow_html=True)

        if not risks:
            st.markdown('<p style="color:#34d399;font-size:0.88rem;">✓ No significant risks detected in this document.</p>', unsafe_allow_html=True)
        else:
            for i, risk in enumerate(risks):
                lv  = risk["risk_level"].upper()
                cls = lv.lower()
                delay = f"{i * 0.07:.2f}s"
                st.markdown(f"""
                <div class="clause-card {cls}" style="animation-delay:{delay}">
                    <span class="risk-badge badge-{cls}">{lv} RISK</span>
                    <div class="clause-text">{risk['clause']}</div>
                    <div class="clause-plain">💬 {risk['plain_english']}</div>
                    <div class="clause-why">⚠️ {risk['why_risky']}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # ── RIGHT: Explain + Dashboard + Download ──────────────
    with right_col:

        # Explain Like I'm 18
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Plain Language Panel</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">Explain Like I\'m 18 💬</div>', unsafe_allow_html=True)

        mode = st.radio("Mode", ["Normal", "Super Simple"], horizontal=True, label_visibility="collapsed")
        st.markdown('<div style="height:6px"></div>', unsafe_allow_html=True)

        if mode == "Normal":
            st.markdown(f"""
            <div class="explain-card">
                <div class="explain-emoji">📄</div>
                <div class="explain-text">{summary}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Trim to first 2 sentences for super-simple mode
            sentences = [s.strip() for s in summary.split(".") if s.strip()]
            simple    = ". ".join(sentences[:2]) + "." if sentences else summary
            st.markdown(f"""
            <div class="explain-card">
                <div class="explain-emoji">🧒</div>
                <div class="explain-text">{simple}</div>
                <div class="explain-analogy">
                    Think of it like: you are agreeing to follow someone else's rules.
                    If you break them, they can take action against you.
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # Risk Report Dashboard
        st.markdown(f"""
        <div class="glass-card">
            <div class="section-title">Risk Dashboard</div>
            <div class="panel-title">Risk Report 📊</div>

            <!-- Circular Gauge -->
            <div style="text-align:center;padding:10px 0 6px;">
                <svg width="190" height="105" viewBox="0 0 190 105" style="overflow:visible;">
                    <!-- background arc -->
                    <path d="M 18 92 A 78 78 0 0 1 172 92"
                          fill="none" stroke="rgba(255,255,255,0.05)"
                          stroke-width="14" stroke-linecap="round"/>
                    <!-- filled arc -->
                    <path d="M 18 92 A 78 78 0 0 1 172 92"
                          fill="none" stroke="{g_color}"
                          stroke-width="14" stroke-linecap="round"
                          stroke-dasharray="{dash_val} 245"
                          style="filter:drop-shadow(0 0 7px {g_color});
                                 transition:stroke-dasharray 1.6s cubic-bezier(0.4,0,0.2,1);"/>
                    <!-- centre text -->
                    <text x="95" y="82" text-anchor="middle"
                          fill="{g_color}" font-family="Orbitron,monospace"
                          font-size="15" font-weight="700"
                          style="filter:drop-shadow(0 0 8px {g_color});">{overall}</text>
                </svg>
                <div style="font-size:0.62rem;color:rgba(180,180,255,0.4);
                            letter-spacing:2.5px;text-transform:uppercase;margin-top:-6px;">
                    Overall Risk Score
                </div>
            </div>

            <div style="height:14px"></div>

            <!-- Financial Risk -->
            <div class="risk-bar-container">
                <div class="risk-bar-label">
                    <span>Financial Risk</span>
                    <span style="color:#f87171;">{high_pct}%</span>
                </div>
                <div class="risk-bar-track">
                    <div class="risk-bar-fill bar-financial"
                         style="width:{high_pct}%;animation-delay:0.2s;"></div>
                </div>
            </div>

            <!-- Privacy Risk -->
            <div class="risk-bar-container">
                <div class="risk-bar-label">
                    <span>Privacy Risk</span>
                    <span style="color:#c084fc;">{med_pct}%</span>
                </div>
                <div class="risk-bar-track">
                    <div class="risk-bar-fill bar-privacy"
                         style="width:{med_pct}%;animation-delay:0.5s;"></div>
                </div>
            </div>

            <!-- Legal Exposure -->
            <div class="risk-bar-container">
                <div class="risk-bar-label">
                    <span>Legal Exposure</span>
                    <span style="color:#fbbf24;">{exp_pct}%</span>
                </div>
                <div class="risk-bar-track">
                    <div class="risk-bar-fill bar-legal"
                         style="width:{exp_pct}%;animation-delay:0.8s;"></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Download report
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Export</div>', unsafe_allow_html=True)
        report_text = generate_report(
            doc_type = st.session_state["doc_type"],
            summary  = summary,
            risks    = risks,
            filename = st.session_state["filename"]
        )
        st.download_button(
            label     = "📄  Download Full Report (.txt)",
            data      = report_text,
            file_name = "know_what_you_sign_report.txt",
            mime      = "text/plain"
        )
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Disclaimer
    st.markdown("""
    <div style="text-align:center;padding:28px 24px 40px;
                font-size:0.68rem;color:rgba(180,180,255,0.28);letter-spacing:0.8px;">
        ⚠️ &nbsp; AI-generated analysis — not legal advice.
        Always consult a qualified lawyer before signing any document.
    </div>
    """, unsafe_allow_html=True)
