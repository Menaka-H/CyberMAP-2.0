# utils/prioritization.py — CyberMAP 2.0 Security Control Prioritization Engine
#
# Ranks identified gaps using a weighted formula that goes beyond
# severity alone: Priority Score = (Severity x Impact x Exploitability) / Effort
# This surfaces gaps that are both dangerous AND cheap/easy to fix,
# ahead of gaps that are severe but expensive or low-impact to remediate.

SEVERITY_WEIGHT = {
    "Critical": 3,
    "High": 2,
    "Medium": 1,
}

# Business impact by NIST domain — reflects how central each domain
# is to preventing and limiting damage from a real attack.
DOMAIN_IMPACT = {
    "Protect": 3,
    "Detect": 3,
    "Respond": 2,
    "Recover": 2,
    "Identify": 2,
    "Govern": 1,
}

# Exploitability — how directly a gap in this subdomain could be
# leveraged by an attacker. Internet/identity-facing controls score
# higher than internal process controls.
HIGH_EXPLOITABILITY_SUBDOMAINS = {
    "Identity Management", "Network Security", "Platform Security",
    "Endpoint Security", "Continuous Monitoring",
}
MEDIUM_EXPLOITABILITY_SUBDOMAINS = {
    "Data Security", "Event Analysis", "Vulnerability Management",
    "Mitigation", "Incident Management",
}

# Remediation effort — rough estimate of how much work a subdomain's
# fixes typically take. Lower effort = faster to close the gap.
LOW_EFFORT_SUBDOMAINS = {
    "Identity Management", "Policy", "Awareness and Training",
}
HIGH_EFFORT_SUBDOMAINS = {
    "Incident Recovery", "Resilience", "Platform Security",
    "Business Environment",
}


def get_exploitability(subdomain):
    if subdomain in HIGH_EXPLOITABILITY_SUBDOMAINS:
        return 3
    if subdomain in MEDIUM_EXPLOITABILITY_SUBDOMAINS:
        return 2
    return 1


def get_effort(subdomain):
    if subdomain in LOW_EFFORT_SUBDOMAINS:
        return 1  # low effort = divides less, ranks higher
    if subdomain in HIGH_EFFORT_SUBDOMAINS:
        return 3
    return 2


def calculate_priority_score(gap):
    """
    Calculate a priority score for a single gap dict (as produced by
    utils.scoring.identify_gaps). Higher score = fix this sooner.
    """
    severity = SEVERITY_WEIGHT.get(gap.get("severity", "Medium"), 1)
    impact = DOMAIN_IMPACT.get(gap.get("domain", ""), 1)
    exploitability = get_exploitability(gap.get("subdomain", ""))
    effort = get_effort(gap.get("subdomain", ""))

    score = (severity * impact * exploitability) / effort
    return round(score, 2)


def prioritize_gaps(gaps):
    """
    Takes the existing gap list (from identify_gaps) and returns a
    NEW list, sorted by priority score descending, with the score
    and its components attached to each gap for transparency.
    """
    enriched = []
    for gap in gaps:
        severity = SEVERITY_WEIGHT.get(gap.get("severity", "Medium"), 1)
        impact = DOMAIN_IMPACT.get(gap.get("domain", ""), 1)
        exploitability = get_exploitability(gap.get("subdomain", ""))
        effort = get_effort(gap.get("subdomain", ""))
        score = round((severity * impact * exploitability) / effort, 2)

        gap_copy = dict(gap)
        gap_copy["priority_score"] = score
        gap_copy["priority_components"] = {
            "severity_weight": severity,
            "business_impact": impact,
            "exploitability": exploitability,
            "effort": effort,
        }
        enriched.append(gap_copy)

    enriched.sort(key=lambda g: g["priority_score"], reverse=True)
    return enriched
# Add this to utils/prioritization.py - CVE-boosted priority scoring

def apply_cve_boost(ranked_gaps, max_checks=5):
    """
    Given gaps already scored by prioritize_gaps(), checks the top N
    gaps that have a CVE search mapping for real/cached CVEs and
    boosts their priority score by 1.5x if any are found. Only the
    top N gaps are checked (default 5) to keep this fast and avoid
    excessive live NVD API calls - this is an on-demand enhancement,
    not something run automatically on every page load.

    Mutates and returns the same list, re-sorted by the updated score.
    """
    from utils.vulnerability_mapping import search_cves_for_gap, NIST_REF_TO_KEYWORD

    checked = 0
    for gap in ranked_gaps:
        if checked >= max_checks:
            break
        nist_ref = gap.get("nist_ref", "")
        if nist_ref not in NIST_REF_TO_KEYWORD:
            continue
        checked += 1

        cve_result = search_cves_for_gap(nist_ref)
        cve_count = len(cve_result.get("cves", []))
        gap["cve_count"] = cve_count
        gap["cve_source"] = cve_result.get("source")

        if "priority_components" not in gap:
            gap["priority_components"] = {}

        if cve_count > 0:
            original_score = gap["priority_score"]
            gap["priority_score"] = round(original_score * 1.5, 2)
            gap["priority_components"]["cve_boost"] = 1.5
        else:
            gap["priority_components"]["cve_boost"] = 1.0

    ranked_gaps.sort(key=lambda g: g["priority_score"], reverse=True)
    return ranked_gaps
