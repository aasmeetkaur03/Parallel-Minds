"""
analyzer.py
-----------
PURPOSE : Sends contract text to Groq (free) and gets back:
            1. A plain English summary
            2. A structured risk analysis

CHANGED FROM : Anthropic Claude API
CHANGED TO   : Groq API (free tier - Llama 3.1 70B model)

USED BY : app.py
DEPENDS ON : groq library, .env file with GROQ_API_KEY
"""

from groq import Groq          # replaces: import anthropic
import os
from dotenv import load_dotenv

load_dotenv()

# Create Groq client using free API key
client = Groq(api_key=os.getenv("GROQ_API_KEY"))   # replaces: anthropic.Anthropic(...)

# Model to use — free on Groq
GROQ_MODEL = "llama-3.3-70b-versatile"             # replaces: "claude-sonnet-4-6"

# Valid document type labels (must match frontend dropdown exactly)
VALID_DOC_TYPES = [
    "Rental Agreement",
    "Employment Contract",
    "Loan Agreement",
    "Terms of Service",
    "General Contract",
]


def classify_document(contract_text):
    """
    Quickly classify what type of legal document this is.

    PARAMETERS:
        contract_text (str) : first portion of the contract text

    RETURNS:
        str : one of the VALID_DOC_TYPES labels, or "General Contract" if unclear

    PURPOSE:
        Used by backend.py to detect if the user selected the wrong document type.
        Only sends the first 2000 characters to keep it fast and cheap.
    """
    prompt = f"""You are a legal document classifier.

Read this legal document excerpt and identify what TYPE of document it is.

Respond with ONLY one of these exact labels — nothing else:
- Rental Agreement
- Employment Contract
- Loan Agreement
- Terms of Service
- General Contract

DOCUMENT EXCERPT:
{contract_text[:2000]}

Your answer (one label only):"""

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=15      # short answer — we only need the label
    )

    raw    = response.choices[0].message.content.strip()
    # Match against valid types (case-insensitive partial match for safety)
    for vtype in VALID_DOC_TYPES:
        if vtype.lower() in raw.lower():
            return vtype
    return "General Contract"


def get_plain_summary(contract_text, doc_type="General Contract"):
    """
    Send contract to Groq (Llama model) and get a plain English summary.

    PARAMETERS:
        contract_text (str) : full raw text of the contract
        doc_type      (str) : type selected by user in sidebar

    RETURNS:
        str : plain English summary
    """

    prompt = f"""You are a legal expert helping everyday people understand contracts.
They are NOT lawyers. Write like you are explaining to a friend.

Document Type: {doc_type}

CONTRACT TEXT:
{contract_text}

Write a plain English summary of this contract.
Rules:
- Use words a 16-year-old can understand
- Write in short paragraphs (3-4 sentences each)
- Cover: what is this agreement, key obligations, key dates/durations, payments, and consequences
- Do NOT use legal jargon
- Keep it under 300 words
"""

    # Groq API call — same structure as OpenAI
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=1024
    )

    # Extract the text from response
    return response.choices[0].message.content


def get_risk_map(contract_text, doc_type="General Contract"):
    """
    Send contract to Groq and get a structured risk analysis.

    PARAMETERS:
        contract_text (str) : full raw text of the contract
        doc_type      (str) : type selected by user in sidebar

    RETURNS:
        str : structured risk analysis with RISK/CLAUSE/PLAIN ENGLISH/WHY RISKY labels
    """

    prompt = f"""You are a legal expert protecting everyday people from unfair contracts.

Document Type: {doc_type}

CONTRACT TEXT:
{contract_text}

Find ALL unusual, one-sided, or rights-waiving clauses.
For EACH risky clause, respond in EXACTLY this format:

RISK: [HIGH or MEDIUM or LOW]
CLAUSE: [Quote or paraphrase the exact clause]
PLAIN ENGLISH: [What this means in simple words]
WHY RISKY: [Why this is bad for the person signing]
---

Sort all results from HIGH to LOW risk.
Be thorough.
"""

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=2048
    )

    return response.choices[0].message.content


def get_clause_ranking(contract_text, doc_type="General Contract"):
    """
    Identify the TOP 5 most important clauses the signer must read first.

    PARAMETERS:
        contract_text (str) : full raw text of the contract
        doc_type      (str) : type of document selected by user

    RETURNS:
        list of dicts, each with keys:
            rank          (int) : 1 to 5
            title         (str) : short clause name e.g. "Termination Rights"
            location      (str) : first few words to help user find it in the doc
            why_important (str) : one sentence on why this clause matters most

    PURPOSE:
        Saves the user's attention — tells them exactly which 5 clauses
        to read first instead of reading the whole document.
    """

    prompt = f"""You are a legal expert helping someone who has limited time.

Document Type: {doc_type}

CONTRACT TEXT:
{contract_text}

Identify the TOP 5 most important clauses this person MUST read before signing.
Rank them 1 (most critical) to 5 (still very important).

For EACH clause respond in EXACTLY this format:

RANK: [1 to 5]
TITLE: [Short name like "Termination Rights" or "Payment Penalties"]
LOCATION: [Quote the first 6-10 words of the actual clause so user can find it]
WHY IMPORTANT: [One clear sentence explaining why this clause matters most]
---

Focus on clauses that affect: money, rights, exit options, liability, privacy, or auto-renewal.
Do NOT include generic or standard boilerplate clauses.
"""

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=700
    )

    raw   = response.choices[0].message.content
    items = []
    blocks = raw.strip().split("---")

    for block in blocks:
        block = block.strip()
        if not block:
            continue

        item = {"rank": 0, "title": "", "location": "", "why_important": ""}
        for line in block.split("\n"):
            line = line.strip()
            if line.startswith("RANK:"):
                try:
                    item["rank"] = int(line.replace("RANK:", "").strip())
                except ValueError:
                    item["rank"] = 0
            elif line.startswith("TITLE:"):
                item["title"]         = line.replace("TITLE:", "").strip()
            elif line.startswith("LOCATION:"):
                item["location"]      = line.replace("LOCATION:", "").strip()
            elif line.startswith("WHY IMPORTANT:"):
                item["why_important"] = line.replace("WHY IMPORTANT:", "").strip()

        if item["title"]:
            items.append(item)

    # Sort by rank and keep top 5 only
    items.sort(key=lambda x: x["rank"])
    return items[:5]
