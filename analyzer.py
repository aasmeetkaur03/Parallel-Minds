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
