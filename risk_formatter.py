"""
risk_formatter.py
-----------------
PURPOSE : Parses Claude's raw risk text and converts it into
          a Python list of dictionaries that app.py can display.

USED BY : app.py (after get_risk_map() returns raw text)
DEPENDS ON : nothing (pure Python, no libraries needed)
"""


def parse_risk_output(raw_text):
    """
    Parse Claude's structured risk output into a list of dicts.

    PARAMETERS:
        raw_text (str) : full raw response from get_risk_map()

    RETURNS:
        list : list of risk dicts with keys:
               risk_level, clause, plain_english, why_risky
    """
    risks  = []
    blocks = raw_text.strip().split("---")

    for block in blocks:
        block = block.strip()
        if not block:
            continue

        risk = {
            "risk_level"   : "LOW",
            "clause"       : "",
            "plain_english": "",
            "why_risky"    : ""
        }

        lines = block.split("\n")
        for line in lines:
            line = line.strip()

            if line.startswith("RISK:"):
                risk["risk_level"]    = line.replace("RISK:", "").strip()
            elif line.startswith("CLAUSE:"):
                risk["clause"]        = line.replace("CLAUSE:", "").strip()
            elif line.startswith("PLAIN ENGLISH:"):
                risk["plain_english"] = line.replace("PLAIN ENGLISH:", "").strip()
            elif line.startswith("WHY RISKY:"):
                risk["why_risky"]     = line.replace("WHY RISKY:", "").strip()

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
    """Return hex color for each risk level."""
    colors = {
        "HIGH"  : "#FF4B4B",
        "MEDIUM": "#FFA500",
        "LOW"   : "#00CC66"
    }
    return colors.get(risk_level.upper(), "#888888")


def get_emoji(risk_level):
    """Return traffic-light emoji for each risk level."""
    emojis = {
        "HIGH"  : "🔴",
        "MEDIUM": "🟡",
        "LOW"   : "🟢"
    }
    return emojis.get(risk_level.upper(), "⚪")
