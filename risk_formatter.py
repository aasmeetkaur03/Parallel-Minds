"""
risk_formatter.py
-----------------
PURPOSE : Takes Claude's raw risk text and converts it into
          a Python list of dictionaries that app.py can display.

USED BY : app.py (after get_risk_map() returns raw text)
DEPENDS ON : nothing (pure Python, no libraries needed)

HOW IT WORKS:
  1. Split Claude's output by "---" separator
  2. Parse each block line by line
  3. Build a dictionary for each risk clause
  4. Return a list of all risk dictionaries

EXAMPLE INPUT (raw text):
  RISK: HIGH
  CLAUSE: Landlord may enter at any time
  PLAIN ENGLISH: Your landlord can walk in whenever they want
  WHY RISKY: You have no privacy in your own home
  ---

EXAMPLE OUTPUT (Python list):
  [
    {
      "risk_level": "HIGH",
      "clause": "Landlord may enter at any time",
      "plain_english": "Your landlord can walk in whenever they want",
      "why_risky": "You have no privacy in your own home"
    }
  ]
"""


def parse_risk_output(raw_text):
    """
    Parse Claude's structured risk output into a list of dicts.

    PARAMETERS:
        raw_text (str) : full raw response from get_risk_map()

    RETURNS:
        list : list of risk dicts, each with keys:
               risk_level, clause, plain_english, why_risky

    PERSON 6 — HOW TO TEST:
        Paste a sample Claude risk response as a string.
        Call this function on it.
        Print the result and check all fields are filled.
    """
    risks  = []

    # Split by our separator "---" to get individual risk blocks
    blocks = raw_text.strip().split("---")

    for block in blocks:
        block = block.strip()
        if not block:
            continue   # skip empty sections

        # Start with empty values for this risk
        risk = {
            "risk_level"  : "LOW",
            "clause"      : "",
            "plain_english": "",
            "why_risky"   : ""
        }

        lines = block.split("\n")
        for line in lines:
            line = line.strip()

            # Match each label and extract the value after the colon
            if line.startswith("RISK:"):
                risk["risk_level"]   = line.replace("RISK:", "").strip()

            elif line.startswith("CLAUSE:"):
                risk["clause"]       = line.replace("CLAUSE:", "").strip()

            elif line.startswith("PLAIN ENGLISH:"):
                risk["plain_english"] = line.replace("PLAIN ENGLISH:", "").strip()

            elif line.startswith("WHY RISKY:"):
                risk["why_risky"]    = line.replace("WHY RISKY:", "").strip()

        # Only add if we got at least some content
        if risk["clause"] or risk["plain_english"]:
            risks.append(risk)

    return risks


def count_risks(risks):
    """
    Count how many risks fall into each level.

    PARAMETERS:
        risks (list) : output of parse_risk_output()

    RETURNS:
        dict : {"HIGH": int, "MEDIUM": int, "LOW": int}
    """
    counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}

    for r in risks:
        level = r["risk_level"].upper()
        if level in counts:
            counts[level] += 1

    return counts


def get_color(risk_level):
    """
    Return a hex color for each risk level (used in UI).

    HIGH   = red
    MEDIUM = orange
    LOW    = green
    """
    colors = {
        "HIGH"  : "#FF4B4B",
        "MEDIUM": "#FFA500",
        "LOW"   : "#00CC66"
    }
    return colors.get(risk_level.upper(), "#888888")


def get_emoji(risk_level):
    """Return a traffic-light emoji for each risk level."""
    emojis = {
        "HIGH"  : "🔴",
        "MEDIUM": "🟡",
        "LOW"   : "🟢"
    }
    return emojis.get(risk_level.upper(), "⚪")
