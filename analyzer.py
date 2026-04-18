"""
analyzer.py
-----------
PURPOSE : Sends contract text to Claude API and gets back:
            1. A plain English summary        (Person 3 owns this)
            2. A structured risk analysis     (Person 4 owns this)

USED BY : app.py (called when user clicks Analyze button)
DEPENDS ON : anthropic library, .env file with API key

HOW IT WORKS:
  1. Load API key from .env file
  2. Create Claude client
  3. Build a detailed prompt with the contract text
  4. Send to Claude, get response back
  5. Return response as a string
"""

import anthropic          # official Claude API library
import os                 # to read environment variables
from dotenv import load_dotenv  # to load .env file

# Load the .env file so ANTHROPIC_API_KEY is available
load_dotenv()

# Create one shared Claude client (reused by both functions)
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


# ─────────────────────────────────────────────
# PERSON 3 OWNS THIS FUNCTION
# ─────────────────────────────────────────────

def get_plain_summary(contract_text, doc_type="General Contract"):
    """
    Send contract to Claude and get a plain English summary.

    PARAMETERS:
        contract_text (str) : full raw text of the contract
        doc_type      (str) : type selected by user in sidebar
                              e.g. "Rental Agreement", "Loan Agreement"

    RETURNS:
        str : plain English summary written by Claude

    PERSON 3 — HOW TO TEST:
        Copy any contract text into a variable.
        Call this function with it.
        Print the result.
        Adjust the prompt below if the output isn't simple enough.

    PROMPT TUNING TIPS (Person 3):
        - If summary is too long  → add "in under 200 words"
        - If too technical        → add "avoid all legal terms"
        - If missing key info     → add "always mention payment amounts"
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
- Do NOT use legal jargon like "hereinafter", "indemnify", "pursuant to"
- Keep it under 300 words
"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )

    # Claude returns a list of content blocks — we want the first text block
    return message.content[0].text


# ─────────────────────────────────────────────
# PERSON 4 OWNS THIS FUNCTION
# ─────────────────────────────────────────────

def get_risk_map(contract_text, doc_type="General Contract"):
    """
    Send contract to Claude and get a structured risk analysis.

    PARAMETERS:
        contract_text (str) : full raw text of the contract
        doc_type      (str) : type selected by user in sidebar

    RETURNS:
        str : structured risk analysis in a specific format
              (this format is parsed later by risk_formatter.py)

    CRITICAL — Person 4 must NOT change the output format tags:
        RISK:, CLAUSE:, PLAIN ENGLISH:, WHY RISKY:, ---
        These are parsed by risk_formatter.py exactly as written.

    PERSON 4 — HOW TO TEST:
        Copy any contract text into a variable.
        Call this function with it.
        Print the result.
        Make sure it has RISK:, CLAUSE:, PLAIN ENGLISH:, WHY RISKY: labels.

    PROMPT TUNING TIPS (Person 4):
        - If too few risks found    → add "be thorough, flag everything unusual"
        - If too many LOW risks     → add "skip truly standard clauses"
        - If format breaks          → remind Claude of the exact format at end
    """

    prompt = f"""You are a legal expert protecting everyday people from unfair contracts.
Your job is to find every clause that could harm the person signing this contract.

Document Type: {doc_type}

CONTRACT TEXT:
{contract_text}

Find ALL unusual, one-sided, or rights-waiving clauses.
For EACH risky clause, respond in EXACTLY this format (do not change the labels):

RISK: [HIGH or MEDIUM or LOW]
CLAUSE: [Quote or paraphrase the exact clause]
PLAIN ENGLISH: [What this means in simple words]
WHY RISKY: [Why this is bad for the person signing]
---

Risk levels mean:
HIGH   = Could cost money, remove major rights, or cause serious harm
MEDIUM = Inconvenient or unfair but not immediately dangerous
LOW    = Slightly unusual but minor impact

Sort all results from HIGH to LOW.
Be thorough. Include anything unusual even if it seems minor.
"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}]
    )

    return message.content[0].text
