"""
backend.py
----------
PURPOSE : Flask server that serves index.html and handles AI analysis.
          Replaces Streamlit entirely. Backend files stay unchanged.

HOW TO RUN:
    python -m pip install flask flask-cors
    python backend.py
    Then open: http://localhost:5000

BACKEND FILES USED (zero changes):
    analyzer.py       — Groq AI calls
    risk_formatter.py — parses risk output
    report.py         — builds downloadable report
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pdfplumber
import docx
import io
import os
from dotenv import load_dotenv

from analyzer       import get_plain_summary, get_risk_map, classify_document
from risk_formatter import parse_risk_output, count_risks
from report         import generate_report

load_dotenv()

app = Flask(__name__, static_folder=".")
CORS(app)


def extract_from_flask_file(file):
    """
    Extract plain text from a Flask uploaded file.
    Supports PDF and DOCX. Returns None if unsupported.
    """
    name  = file.filename.lower()
    raw   = file.read()

    if name.endswith(".pdf"):
        text = ""
        with pdfplumber.open(io.BytesIO(raw)) as pdf:
            for page in pdf.pages:
                pt = page.extract_text()
                if pt:
                    text += pt + "\n"
        return text.strip() or None

    elif name.endswith(".docx"):
        doc  = docx.Document(io.BytesIO(raw))
        paras = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n".join(paras) or None

    return None


@app.route("/")
def index():
    return send_from_directory(".", "index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    file     = request.files.get("file")
    doc_type = request.form.get("doc_type", "General Contract")
    force    = request.form.get("force", "false").lower() == "true"

    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    contract_text = extract_from_flask_file(file)
    if not contract_text:
        return jsonify({"error": "Could not extract text. Try a different file."}), 400

    # ── Document type validation (skipped if user clicked "Analyze Anyway") ──
    if not force and doc_type != "General Contract":
        detected = classify_document(contract_text)
        if detected != doc_type:
            return jsonify({
                "type_mismatch" : True,
                "detected_type" : detected,
                "selected_type" : doc_type,
                "filename"      : file.filename,
            })

    summary   = get_plain_summary(contract_text, doc_type)
    raw_risks = get_risk_map(contract_text, doc_type)
    risks     = parse_risk_output(raw_risks)
    counts    = count_risks(risks)
    report    = generate_report(doc_type, summary, risks, file.filename)

    return jsonify({
        "summary"   : summary,
        "risks"     : risks,
        "counts"    : counts,
        "word_count": len(contract_text.split()),
        "report"    : report,
        "filename"  : file.filename
    })


if __name__ == "__main__":
    print("\n⚖️  Know What You Sign")
    print("─" * 40)
    print("📍 Open browser at: http://localhost:5000\n")
    app.run(debug=True, port=5000)
