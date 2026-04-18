# ⚖️ Know What You Sign

> AI-powered legal document simplifier with risk surface mapping.
> Built for the **Human Augmentation & Assistive Systems** track —
> *Extend what people can perceive, decide, and do — especially those underserved by existing tools.*

---

## What It Does

Upload any legal agreement — rental, employment, loan, or terms of service — and instantly get:

- **Plain English summary** — no legal jargon, written like a friend explaining it
- **Risk Surface Map** — every unusual, one-sided, or rights-waiving clause ranked HIGH / MEDIUM / LOW
- **Document type validation** — detects if you uploaded the wrong document type and warns you
- **Explain Like I'm 18** — toggle between Normal and Super Simple explanations
- **Risk Dashboard** — animated gauge + financial / privacy / legal exposure bars
- **Downloadable report** — full analysis as a `.txt` file

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Pure HTML + CSS + JavaScript |
| Backend | Python + Flask |
| AI Engine | Groq API (Llama 3.3 70B) — free tier |
| PDF Reading | pdfplumber |
| DOCX Reading | python-docx |

---

## Project Structure

```
Parallel Minds/
│
├── backend.py          ← Flask server — ONLY file you run
├── index.html          ← Full UI (served automatically)
├── analyzer.py         ← Groq AI calls (summary + risk + classify)
├── extractor.py        ← PDF / DOCX text extraction
├── risk_formatter.py   ← Parses AI risk output into structured data
├── report.py           ← Builds downloadable .txt report
├── .env                ← Your API key (never share or commit this)
└── requirements.txt    ← All Python dependencies
```

---

## Setup & Installation

### Step 1 — Get a Free Groq API Key

1. Go to [console.groq.com](https://console.groq.com)
2. Sign up for a free account
3. Navigate to **API Keys** → **Create Key**
4. Copy the key

### Step 2 — Create `.env` File

Inside the `Parallel Minds/` folder, create a file named `.env` and add:

```
GROQ_API_KEY=your_groq_api_key_here
```

### Step 3 — Install Dependencies

Open Command Prompt and run:

```bash
python -m pip install streamlit pdfplumber python-docx groq python-dotenv flask flask-cors
```

Or using the requirements file:

```bash
python -m pip install -r requirements.txt
```

---

## How to Run

```bash
cd "D:\Parallel Minds"
python backend.py
```

Then open your browser at:

```
http://localhost:5000
```

That's it. One command starts the entire application.

---

## How to Use

1. **Select document type** from the dropdown (Rental, Employment, Loan, ToS, General)
2. **Upload your contract** — drag & drop or click to browse (PDF or DOCX)
3. **Click Analyze** — wait 10–20 seconds for AI processing
4. **Read your results:**
   - Plain English summary on the left
   - Risk cards ranked by severity (hover each card to expand)
   - Explain Like I'm 18 panel on the right
   - Risk gauge + bars showing financial / privacy / legal exposure
5. **Download** the full report as a `.txt` file

---

## Document Type Validation

If you upload a **Loan Agreement** but select **Employment Contract**, the app will:

- Detect the real document type using AI
- Show a warning banner explaining the mismatch
- Give you two options:
  - ✅ Switch to the correct type and re-analyze
  - Continue anyway with your original selection

---

## Supported File Types

| Format | Supported |
|---|---|
| `.pdf` | ✅ Yes |
| `.docx` | ✅ Yes |
| `.doc` | ❌ Not supported — save as .docx first |
| `.txt` | ❌ Not supported |

---

## API Usage & Limits (Groq Free Tier)

| Model | Daily Limit |
|---|---|
| Llama 3.3 70B Versatile | 14,400 requests/day |

Each document analysis uses **3 API calls** (classify + summarize + risk map).
That means approximately **4,800 analyses per day** on the free tier.

---

## Team

| Person | Role | Files Owned |
|---|---|---|
| Person 1 | Project Lead + Setup | `requirements.txt`, `.env`, folder structure |
| Person 2 | File Extraction | `extractor.py` |
| Person 3 | AI Summary Prompts | `analyzer.py` — summary function |
| Person 4 | AI Risk Analysis Prompts | `analyzer.py` — risk function |
| Person 5 | Frontend UI | `index.html` |
| Person 6 | Report + Testing | `report.py`, `risk_formatter.py` |

---

## Data Sources Used for Testing

| Source | What We Used It For |
|---|---|
| [Common Paper](https://commonpaper.com) | Standard employment and SaaS agreements |
| [SEC EDGAR](https://efts.sec.gov) | Real loan and employment contracts (public filings) |
| [LawDepot](https://lawdepot.com) | Free sample rental agreements |
| [ToS;DR](https://tosdr.org) | Terms of Service documents rated by lawyers |

---

## Disclaimer

> This tool provides AI-generated analysis for **informational purposes only**.
> It is **not legal advice**.
> Always consult a qualified lawyer before signing any legal document.



## Hackathon Track

**Human Augmentation & Assistive Systems**
*Extend what people can perceive, decide, and do — especially those underserved by existing tools.*

Legal contracts are written to protect the party with the lawyer.
This tool levels the playing field for everyday people — renters, employees, borrowers —
who sign documents without fully understanding what they are agreeing to.
