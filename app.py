"""
app.py
------
PURPOSE : Main entry point of the Legal Plain Talk application.
          This is the ONLY file you need to run.

HOW TO RUN:
    streamlit run app.py

WHAT IT DOES:
    1. Shows the upload interface
    2. Extracts text from uploaded file (via extractor.py)
    3. Sends text to Claude for analysis (via analyzer.py)
    4. Formats and displays the risk map (via risk_formatter.py)
    5. Offers a downloadable report (via report.py)

DEPENDS ON:
    extractor.py, analyzer.py, risk_formatter.py, report.py
    All must be in the same folder as this file.

PERSON 5 — YOUR JOB:
    - Write and style all st.* calls
    - Arrange the layout (columns, expanders, metrics)
    - Make sure the Analyze button triggers analysis
    - Store results in st.session_state so they survive page refreshes
"""

import streamlit as st

# Import our own modules (all in same folder)
from extractor      import extract_text
from analyzer       import get_plain_summary, get_risk_map
from risk_formatter import parse_risk_output, count_risks, get_color, get_emoji
from report         import generate_report


# ─────────────────────────────────────────────────────────
# PAGE CONFIGURATION — must be the FIRST streamlit call
# ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Legal Plain Talk",
    page_icon="⚖️",
    layout="wide"          # use full screen width
)


# HEADER SECTION
st.title("⚖️ Legal Plain Talk")
st.subheader("Understand what you're signing. Before you sign.")
st.caption("Upload any rental, employment, loan, or terms-of-service agreement.")
st.markdown("---")

# SIDEBAR — Document Type Selector
# The selected type is passed to Claude to tune its prompts.
st.sidebar.title("⚙️ Settings")
doc_type = st.sidebar.selectbox(
    "What type of document is this?",
    options=[
        "Rental Agreement",
        "Employment Contract",
        "Loan Agreement",
        "Terms of Service",
        "General Contract"
    ],
    help="Choosing the right type helps Claude give more accurate analysis."
)

st.sidebar.markdown("---")
st.sidebar.info(
    "Supported file types:\n"
    "- PDF (.pdf)\n"
    "- Word Document (.docx)\n"
    "- Or paste text below"
)
st.sidebar.markdown("---")
st.sidebar.warning(
    "This tool provides AI analysis only.\n"
    "Always consult a real lawyer before signing."
)

# STEP 1 — FILE UPLOAD
st.markdown("### Step 1 — Upload Your Document")

uploaded_file = st.file_uploader(
    label="Upload a PDF or DOCX contract",
    type=["pdf", "docx"],
    help="Your document is only used for analysis and is not stored anywhere."
)

# Fallback option: user can paste raw text instead of uploading
st.markdown("**No file? Paste your contract text here instead:**")
pasted_text = st.text_area(
    label="Paste contract text",
    height=180,
    placeholder="Paste the full text of the contract here..."
)

# TEXT EXTRACTION LOGIC
# Runs immediately after file upload (before button click)

contract_text = ""    # will hold the final extracted text
filename      = "document"

if uploaded_file is not None:
    with st.spinner("Reading your document..."):
        contract_text = extract_text(uploaded_file)
        filename      = uploaded_file.name

    if contract_text:
        word_count = len(contract_text.split())
        st.success(f"Document loaded successfully. ({word_count} words found)")
    else:
        st.error(
            "Could not read this file. "
            "Try saving it as a newer PDF or paste the text manually below."
        )

elif pasted_text.strip():
    # Use the manually pasted text
    contract_text = pasted_text.strip()
    word_count    = len(contract_text.split())
    st.success(f"Text received. ({word_count} words)")


# STEP 2 — ANALYZE BUTTON
# Only active when we have contract text to analyze.

st.markdown("---")
st.markdown("### Step 2 — Analyze")

# Show a hint if no document is loaded yet
if not contract_text:
    st.info("Upload a document or paste text above to enable analysis.")

# The button is disabled until contract_text is available
analyze_clicked = st.button(
    label="Analyze Document",
    disabled=(not contract_text),
    type="primary"
)

if analyze_clicked:
    #  Run Summary 
    with st.spinner("Reading and summarizing the contract..."):
        summary = get_plain_summary(contract_text, doc_type)

    # Run Risk Analysis 
    with st.spinner("Scanning for risky clauses..."):
        raw_risk_text = get_risk_map(contract_text, doc_type)
        risks         = parse_risk_output(raw_risk_text)

    # Save to session state 
    # session_state persists across Streamlit reruns (e.g. button clicks)
    st.session_state["summary"]   = summary
    st.session_state["risks"]     = risks
    st.session_state["doc_type"]  = doc_type
    st.session_state["filename"]  = filename

    st.success("Analysis complete! Scroll down to see results.")

# STEP 3 — SHOW RESULTS
# Only shown after analysis has run (stored in session_state)

if "summary" in st.session_state and "risks" in st.session_state:

    summary  = st.session_state["summary"]
    risks    = st.session_state["risks"]
    counts   = count_risks(risks)

    st.markdown("---")
    st.markdown("## Results")

    # ── Risk Count Badges ──────────────────────────────
    # Show 3 metric cards at the top for quick overview
    col_high, col_medium, col_low = st.columns(3)

    col_high.metric(
        label="🔴 HIGH Risk Clauses",
        value=counts["HIGH"],
        help="Clauses that could seriously harm your rights or finances"
    )
    col_medium.metric(
        label="🟡 MEDIUM Risk Clauses",
        value=counts["MEDIUM"],
        help="Clauses that are inconvenient or unfair"
    )
    col_low.metric(
        label="🟢 LOW Risk Clauses",
        value=counts["LOW"],
        help="Slightly unusual but minor impact"
    )

    st.markdown("---")

    # ── Two Column Layout: Summary | Risk Map ──────────
    left_col, right_col = st.columns([1, 1], gap="large")

    # LEFT — Plain English Summary
    with left_col:
        st.markdown("### Plain English Summary")
        st.info(summary)

    # RIGHT — Risk Surface Map
    with right_col:
        st.markdown("### Risk Surface Map")

        if not risks:
            st.success("No significant risks detected in this document.")
        else:
            # Show each risk as a collapsible card (expander)
            for risk in risks:
                level   = risk["risk_level"].upper()
                emoji   = get_emoji(level)
                # Truncate long clause text for the expander title
                title   = risk["clause"][:80] + ("..." if len(risk["clause"]) > 80 else "")

                with st.expander(f"{emoji} [{level}] — {title}"):
                    st.markdown(f"**Original Clause:**")
                    st.markdown(f"> {risk['clause']}")

                    st.markdown(f"**In Plain English:**")
                    st.markdown(f"{risk['plain_english']}")

                    st.markdown(f"**Why This Is Risky:**")
                    st.markdown(f"{risk['why_risky']}")

    # Download Report 
    st.markdown("---")
    st.markdown("### Download Your Report")

    report_text = generate_report(
        doc_type = st.session_state["doc_type"],
        summary  = summary,
        risks    = risks,
        filename = st.session_state["filename"]
    )

    st.download_button(
        label     = " Download Full Report (.txt)",
        data      = report_text,
        file_name = "legal_analysis_report.txt",
        mime      = "text/plain"
    )

    # Analyze Another Document 
    if st.button(" Analyze Another Document"):
        # Clear session state so the page resets cleanly
        for key in ["summary", "risks", "doc_type", "filename"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

    # Legal Disclaimer 
    st.markdown("---")
    st.caption(
        "Disclaimer: This is an AI-generated analysis for informational purposes only. "
        "It is not legal advice. Always consult a qualified lawyer before signing any legal document."
    )
