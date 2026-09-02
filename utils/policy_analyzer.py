# utils/policy_analyzer.py — CyberMAP 2.0 Automated Policy Gap Analyzer
#
# Extracts text from an uploaded policy document (PDF) and checks it
# against a curated set of governance requirement keywords, mapped to
# NIST CSF 2.0 subcategories and ISO 27001 clauses. This extends
# automated evidence checking into the Govern domain, which cannot be
# verified through endpoint scanning since it covers policy and
# process controls rather than technical configuration.

import re
from pypdf import PdfReader

# ── Requirement -> keyword phrases that would indicate coverage ────
# Each requirement is checked against the extracted policy text.
# If ANY of the listed phrases appear (case-insensitive), the
# requirement is marked Covered, along with the matching snippet.
POLICY_REQUIREMENTS = [
    {
        "nist_ref": "GV.PO-01",
        "iso_ref": "ISO 5.1",
        "requirement": "Cybersecurity policy documented and approved",
        "keywords": ["cybersecurity policy", "information security policy", "security policy"],
    },
    {
        "nist_ref": "GV.PO-01",
        "iso_ref": "ISO 5.1",
        "requirement": "Policy review cycle defined",
        "keywords": ["reviewed annually", "annual review", "policy review", "reviewed periodically"],
    },
    {
        "nist_ref": "GV.RR-02",
        "iso_ref": "ISO 5.2",
        "requirement": "Designated security officer or CISO",
        "keywords": ["chief information security officer", "ciso", "security officer", "designated officer"],
    },
    {
        "nist_ref": "GV.RM-01",
        "iso_ref": "ISO 6.1",
        "requirement": "Risk tolerance / risk appetite statement",
        "keywords": ["risk tolerance", "risk appetite", "acceptable level of risk"],
    },
    {
        "nist_ref": "GV.OC-03",
        "iso_ref": "ISO 5.31",
        "requirement": "Legal and regulatory compliance obligations",
        "keywords": ["regulatory requirements", "legal obligations", "compliance obligations", "applicable law"],
    },
    {
        "nist_ref": "GV.SC-01",
        "iso_ref": "ISO 5.19",
        "requirement": "Third-party / vendor risk assessment",
        "keywords": ["third-party risk", "vendor risk", "supplier assessment", "vendor assessment"],
    },
    {
        "nist_ref": "GV.SC-04",
        "iso_ref": "ISO 5.19",
        "requirement": "Vendor offboarding procedure",
        "keywords": ["vendor offboarding", "contract termination", "secure offboarding", "termination of access"],
    },
    {
        "nist_ref": "GV.AT-01",
        "iso_ref": "ISO 6.3",
        "requirement": "Mandatory security awareness training",
        "keywords": ["security awareness training", "mandatory training", "annual training"],
    },
    {
        "nist_ref": "GV.OV-03",
        "iso_ref": "ISO 9.3",
        "requirement": "Management review of ISMS",
        "keywords": ["management review", "isms review", "leadership review"],
    },
    {
        "nist_ref": "PR.AA-03",
        "iso_ref": "ISO 8.5",
        "requirement": "Multi-factor authentication requirement",
        "keywords": ["multi-factor authentication", "mfa", "two-factor authentication", "2fa"],
    },
    {
        "nist_ref": "PR.DS-01",
        "iso_ref": "ISO 8.24",
        "requirement": "Data encryption requirement",
        "keywords": ["encryption", "encrypted at rest", "aes-256", "tls"],
    },
    {
        "nist_ref": "RS.MA-01",
        "iso_ref": "ISO 5.26",
        "requirement": "Incident response plan referenced",
        "keywords": ["incident response plan", "incident response procedure", "security incident"],
    },
    {
        "nist_ref": "RS.CO-02",
        "iso_ref": "ISO 5.29",
        "requirement": "Breach notification procedure",
        "keywords": ["breach notification", "data breach", "notify affected", "notification timeline"],
    },
    {
        "nist_ref": "RC.RP-01",
        "iso_ref": "ISO 5.30",
        "requirement": "Business continuity / disaster recovery plan",
        "keywords": ["business continuity", "disaster recovery", "bcp", "drp"],
    },
    {
        "nist_ref": "RC.RP-02",
        "iso_ref": "ISO 5.30",
        "requirement": "Recovery time / recovery point objectives",
        "keywords": ["recovery time objective", "recovery point objective", "rto", "rpo"],
    },
]


def extract_text_from_pdf(file_bytes):
    """
    Extract all readable text from an uploaded PDF's bytes.
    Returns the full text as one lowercase string for matching,
    plus the original-case text for showing matched snippets.
    """
    import io
    reader = PdfReader(io.BytesIO(file_bytes))
    full_text = ""
    for page in reader.pages:
        text = page.extract_text() or ""
        full_text += text + "\n"
    return full_text


def find_snippet(text, keyword, context_chars=80):
    """
    Find the first occurrence of a keyword in the text and return
    a short surrounding snippet, for showing the user WHERE the
    match came from.
    """
    lower_text = text.lower()
    idx = lower_text.find(keyword.lower())
    if idx == -1:
        return None
    start = max(0, idx - context_chars)
    end = min(len(text), idx + len(keyword) + context_chars)
    snippet = text[start:end].strip()
    snippet = re.sub(r"\s+", " ", snippet)
    return "..." + snippet + "..."


def analyze_policy_document(file_bytes, filename):
    """
    Main entry point. Extracts text from the uploaded policy PDF and
    checks it against every requirement in POLICY_REQUIREMENTS.

    Returns:
    {
        "filename": "...",
        "total_requirements": 15,
        "covered_count": 9,
        "coverage_pct": 60.0,
        "results": [
            {
                "nist_ref": "...",
                "iso_ref": "...",
                "requirement": "...",
                "status": "Covered" | "Not Covered",
                "matched_keyword": "..." or None,
                "snippet": "..." or None,
            },
            ...
        ]
    }
    """
    try:
        text = extract_text_from_pdf(file_bytes)
    except Exception as e:
        return {
            "filename": filename,
            "error": f"Could not read PDF: {e}",
            "total_requirements": 0,
            "covered_count": 0,
            "coverage_pct": 0,
            "results": [],
        }

    if not text.strip():
        return {
            "filename": filename,
            "error": "No extractable text found in this PDF (it may be a scanned image without OCR).",
            "total_requirements": 0,
            "covered_count": 0,
            "coverage_pct": 0,
            "results": [],
        }

    results = []
    for req in POLICY_REQUIREMENTS:
        matched_keyword = None
        snippet = None
        for kw in req["keywords"]:
            if kw.lower() in text.lower():
                matched_keyword = kw
                snippet = find_snippet(text, kw)
                break

        results.append({
            "nist_ref": req["nist_ref"],
            "iso_ref": req["iso_ref"],
            "requirement": req["requirement"],
            "status": "Covered" if matched_keyword else "Not Covered",
            "matched_keyword": matched_keyword,
            "snippet": snippet,
        })

    covered_count = sum(1 for r in results if r["status"] == "Covered")
    total = len(results)
    coverage_pct = round((covered_count / total) * 100, 1) if total > 0 else 0

    return {
        "filename": filename,
        "total_requirements": total,
        "covered_count": covered_count,
        "coverage_pct": coverage_pct,
        "results": results,
    }
