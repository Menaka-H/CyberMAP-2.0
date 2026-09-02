# utils/scoring.py
# This file calculates maturity scores and identifies security gaps

from collections import defaultdict
from utils.questions_data import (
    DOMAINS,
    DOMAIN_DESCRIPTIONS,
    RECOMMENDATIONS,
    SUBDOMAIN_RECOMMENDATIONS,
)


def compute_domain_scores(answers, questions):
    """
    Calculate the maturity score for each domain.

    How it works:
    - Each answer is a number from 0 to 5
    - Each question has a weight (importance factor)
    - Score = (weighted sum of answers) / (max possible weighted sum) * 5

    answers   → dict like {"1": 3, "2": 4, "3": 1, ...}
                key = question ID, value = score given (0-5)
    questions → list of question dicts from the database

    Returns a dict like:
    {
        "Govern":   {"score": 2.5, "pct": 50.0, "count": 7},
        "Identify": {"score": 3.1, "pct": 62.0, "count": 7},
        ...
    }
    """
    # Set up empty totals for each domain
    totals = defaultdict(lambda: {
        "weighted_sum":   0.0,
        "weight_total":   0.0,
        "count":          0
    })

    # Loop through every question
    for q in questions:
        qid    = str(q["id"])         # question ID as string
        weight = q.get("weight", 1.0) # importance of this question
        domain = q["domain"]

        if qid in answers:
            score = int(answers[qid])              # answer given (0-5)
            totals[domain]["weighted_sum"]  += score * weight
            totals[domain]["weight_total"]  += 5.0 * weight  # 5 = max possible
            totals[domain]["count"]         += 1

    # Now calculate the final score for each domain
    domain_scores = {}

    for domain in DOMAINS:
        if domain in totals and totals[domain]["weight_total"] > 0:
            ws  = totals[domain]["weighted_sum"]
            wt  = totals[domain]["weight_total"]

            # Scale to 0-5 range
            raw_score = (ws / wt) * 5.0

            domain_scores[domain] = {
                "score":       round(raw_score, 2),
                "pct":         round((ws / wt) * 100, 1),
                "count":       totals[domain]["count"],
                "description": DOMAIN_DESCRIPTIONS.get(domain, ""),
            }
        else:
            # Domain had no answers
            domain_scores[domain] = {
                "score":       0.0,
                "pct":         0.0,
                "count":       0,
                "description": DOMAIN_DESCRIPTIONS.get(domain, ""),
            }

    return domain_scores


def compute_overall_score(domain_scores):
    """
    Average the domain scores into one overall maturity score.

    Example:
        Govern=2.0, Identify=3.0, Protect=2.5,
        Detect=1.5, Respond=2.0, Recover=3.0
        Overall = (2.0+3.0+2.5+1.5+2.0+3.0) / 6 = 2.33
    """
    scores = [
        d["score"]
        for d in domain_scores.values()
        if d["score"] > 0
    ]

    if not scores:
        return 0.0

    return round(sum(scores) / len(scores), 2)


def get_maturity_label(score):
    """
    Convert a numeric score into a human-readable maturity level.

    Returns a tuple: (label, emoji, hex_color)

    Example:
        get_maturity_label(2.3)
        → ("Developing", "🟠", "#ea580c")
    """
    if score < 1.5:
        return ("Initial",    "🔴", "#dc2626")
    elif score < 2.5:
        return ("Developing", "🟠", "#ea580c")
    elif score < 3.5:
        return ("Defined",    "🟡", "#ca8a04")
    elif score < 4.5:
        return ("Managed",    "🟢", "#16a34a")
    else:
        return ("Optimising", "🔵", "#2563eb")


def identify_gaps(answers, questions, threshold=3):
    """
    Find all questions where the score is BELOW the threshold.
    These are the security weaknesses — the "gaps".

    threshold = 3 means: anything below "Defined" is a gap.

    Returns a list of gap dicts, sorted worst-first.

    Example gap dict:
    {
        "domain":         "Protect",
        "subdomain":      "Identity Management",
        "question":       "Is MFA enforced...",
        "score":          1,
        "severity":       "Critical",
        "nist_ref":       "PR.AA-03",
        "iso_ref":        "ISO 8.5",
        "recommendation": "Enable MFA on all privileged accounts...",
    }
    """
    gaps = []

    for q in questions:
        qid   = str(q["id"])
        score = int(answers.get(qid, 0))

        # Only flag as a gap if below threshold
        if score < threshold:

            # Classify severity based on score
            if score <= 1:
                severity = "Critical"
            elif score == 2:
                severity = "High"
            else:
                severity = "Medium"

            gaps.append({
                "id":             q["id"],
                "domain":         q["domain"],
                "subdomain":      q["subdomain"],
                "question":       q["question"],
                "nist_ref":       q["nist_ref"],
                "iso_ref":        q["iso_ref"],
                "score":          score,
                "severity":       severity,
                "recommendation": _get_recommendation(q),
            })

    # Sort: Critical first, then High, then Medium
    severity_order = {"Critical": 0, "High": 1, "Medium": 2}
    gaps.sort(key=lambda g: (severity_order[g["severity"]], g["score"]))

    return gaps


def _get_recommendation(q):
    """
    Find the best recommendation for a gap.

    The base recommendation is still looked up at the (domain,
    subdomain) level, since the underlying fix genuinely is the same
    for every control in that subdomain (e.g. "have a documented
    policy"). To avoid identical text repeating verbatim across
    multiple gaps in the same subdomain, the specific control being
    asked about is appended as a second sentence, so each gap reads
    distinctly even when the core guidance is shared.
    """
    domain    = q["domain"]
    subdomain = q.get("subdomain", "")
    question  = q.get("question", "").strip()

    def specific_clause(question_text):
        if not question_text:
            return ""
        text = question_text.rstrip("?").strip()
        if text:
            text = text[0].lower() + text[1:]
        return f" Specifically, address: {text}."

    # 1. Specific subdomain match — this now covers all real subdomains
    base = SUBDOMAIN_RECOMMENDATIONS.get((domain, subdomain))
    if base:
        return base + specific_clause(question)

    # 2. Old domain-level fallback with keyword matching
    domain_recs = RECOMMENDATIONS.get(domain, [])
    if domain_recs:
        subdomain_lower = subdomain.lower()
        for rec in domain_recs:
            for word in subdomain_lower.split():
                if len(word) > 3 and word in rec.lower():
                    return rec + specific_clause(question)
        return domain_recs[0] + specific_clause(question)

    # 3. Final fallback
    return "Review and strengthen this control." + specific_clause(question)


def build_feature_vector(domain_scores):
    """
    Build a list of 6 numbers for the ML model to use.
    Order must always match the DOMAINS list.

    Example output: [2.0, 3.1, 1.8, 2.5, 3.0, 2.2]
                     Gov  Ide  Pro  Det  Res  Rec
    """
    return [
        domain_scores.get(d, {}).get("score", 0.0)
        for d in DOMAINS
    ]