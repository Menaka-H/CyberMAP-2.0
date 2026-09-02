# utils/report_gen.py — Fixed PDF generator (CyberMAP 2.0 enhanced)
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table,
    TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from io import BytesIO
from datetime import datetime

# Brand colours
NAVY   = colors.HexColor("#1E3A5F")
ORANGE = colors.HexColor("#E8601C")
SLATE  = colors.HexColor("#475569")
RED    = colors.HexColor("#ef4444")
AMBER  = colors.HexColor("#f59e0b")
GREEN  = colors.HexColor("#22c55e")
PURPLE = colors.HexColor("#8b5cf6")
LGRAY  = colors.HexColor("#F3F4F6")
WHITE  = colors.white

def get_risk_colour(risk):
    return {
        "Critical": RED,
        "High":     AMBER,
        "Medium":   colors.HexColor("#3b82f6"),
        "Low":      GREEN,
    }.get(risk, SLATE)

def get_severity_colour(sev):
    return {
        "Critical": RED,
        "High":     AMBER,
        "Medium":   colors.HexColor("#eab308"),
    }.get(sev, SLATE)

def generate_pdf_report(assessment_data, domain_scores,
                         evidence_summary=None, shap_explanation=None,
                         priority_gaps=None):
    """
    assessment_data   — unchanged from before (org_name, assessor, etc.)
    domain_scores     — unchanged from before
    evidence_summary  — optional dict: {"total_eligible": int,
                         "with_evidence": int, "coverage_pct": float}
    shap_explanation  — optional dict from utils.ml_model.explain_prediction()
    priority_gaps     — optional list of gaps already run through
                         utils.prioritization.prioritize_gaps() (has
                         'priority_score' on each gap)
    All three new parameters are optional — if not passed, the PDF
    generates exactly as before with no CyberMAP 2.0 sections added.
    """
    buffer = BytesIO()
    doc    = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=40, leftMargin=40,
        topMargin=50, bottomMargin=40,
    )

    styles  = getSampleStyleSheet()
    story   = []

    # ── custom styles ──────────────────────────────────────────────────
    title_style = ParagraphStyle(
        "Title", parent=styles["Normal"],
        fontSize=26, fontName="Helvetica-Bold",
        textColor=WHITE, alignment=TA_CENTER, spaceAfter=4,
    )
    sub_style = ParagraphStyle(
        "Sub", parent=styles["Normal"],
        fontSize=11, fontName="Helvetica",
        textColor=colors.HexColor("#93c5fd"),
        alignment=TA_CENTER, spaceAfter=4,
    )
    h1_style = ParagraphStyle(
        "H1", parent=styles["Normal"],
        fontSize=14, fontName="Helvetica-Bold",
        textColor=NAVY, spaceBefore=18, spaceAfter=6,
    )
    h2_style = ParagraphStyle(
        "H2", parent=styles["Normal"],
        fontSize=11, fontName="Helvetica-Bold",
        textColor=ORANGE, spaceBefore=12, spaceAfter=4,
    )
    body_style = ParagraphStyle(
        "Body", parent=styles["Normal"],
        fontSize=9, fontName="Helvetica",
        textColor=colors.HexColor("#1e293b"),
        alignment=TA_JUSTIFY, spaceAfter=4,
    )
    center_style = ParagraphStyle(
        "Center", parent=styles["Normal"],
        fontSize=9, fontName="Helvetica",
        alignment=TA_CENTER,
    )

    # ── safe data extraction ───────────────────────────────────────────
    org_name    = str(assessment_data.get("org_name",    "Organisation"))
    assessor    = str(assessment_data.get("assessor",    "Assessor"))
    risk_level  = str(assessment_data.get("risk_level",  "Unknown"))
    mat_score   = float(assessment_data.get("maturity_score", 0.0))
    gaps        = assessment_data.get("gaps", [])
    if not isinstance(gaps, list):
        gaps = []
    date_str    = datetime.now().strftime("%d %B %Y")

    # ── COVER PAGE ─────────────────────────────────────────────────────
    cover_data = [[
        Paragraph("🛡️  CyberMAP", title_style),
    ]]
    cover_table = Table(cover_data, colWidths=[5.1*inch])
    cover_table.setStyle(TableStyle([
        ("BACKGROUND",  (0,0), (-1,-1), NAVY),
        ("ROUNDEDCORNERS", [10]),
        ("TOPPADDING",  (0,0), (-1,-1), 30),
        ("BOTTOMPADDING",(0,0),(-1,-1), 10),
        ("LEFTPADDING", (0,0), (-1,-1), 20),
        ("RIGHTPADDING",(0,0), (-1,-1), 20),
    ]))
    story.append(cover_table)
    story.append(Spacer(1, 8))

    sub_data = [[Paragraph("Cybersecurity Maturity Assessment Report", sub_style)]]
    sub_table = Table(sub_data, colWidths=[5.1*inch])
    sub_table.setStyle(TableStyle([
        ("BACKGROUND",  (0,0), (-1,-1), NAVY),
        ("BOTTOMPADDING",(0,0),(-1,-1), 20),
        ("LEFTPADDING", (0,0), (-1,-1), 20),
        ("RIGHTPADDING",(0,0), (-1,-1), 20),
    ]))
    story.append(sub_table)
    story.append(Spacer(1, 20))

    # ── EXECUTIVE SUMMARY ──────────────────────────────────────────────
    story.append(Paragraph("Executive Summary", h1_style))
    story.append(HRFlowable(
        width="100%", thickness=2,
        color=ORANGE, spaceAfter=10,
    ))

    risk_col  = get_risk_colour(risk_level)
    mat_label = (
        "Initial"    if mat_score < 1.0 else
        "Developing" if mat_score < 2.0 else
        "Defined"    if mat_score < 3.0 else
        "Managed"    if mat_score < 4.0 else
        "Optimising"
    )

    summary_data = [
        ["Organisation",    org_name],
        ["Assessor",        assessor],
        ["Date",            date_str],
        ["Overall Score",   f"{mat_score:.2f} / 5.00"],
        ["Maturity Level",  mat_label],
        ["Risk Level",      risk_level],
        ["Total Gaps",      str(len(gaps))],
        ["Framework",       "NIST CSF 2.0 + ISO/IEC 27001:2022"],
    ]
    sum_table = Table(
        summary_data,
        colWidths=[2.0*inch, 3.1*inch],
    )
    sum_table.setStyle(TableStyle([
        ("FONTNAME",    (0,0), (0,-1), "Helvetica-Bold"),
        ("FONTNAME",    (1,0), (1,-1), "Helvetica"),
        ("FONTSIZE",    (0,0), (-1,-1), 9),
        ("TEXTCOLOR",   (0,0), (0,-1), NAVY),
        ("BACKGROUND",  (0,0), (-1,0), LGRAY),
        ("BACKGROUND",  (0,2), (-1,2), LGRAY),
        ("BACKGROUND",  (0,4), (-1,4), LGRAY),
        ("BACKGROUND",  (0,6), (-1,6), LGRAY),
        ("ROWBACKGROUNDS",(0,0),(-1,-1),[LGRAY, WHITE]),
        ("GRID",        (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ("TOPPADDING",  (0,0), (-1,-1), 6),
        ("BOTTOMPADDING",(0,0),(-1,-1), 6),
        ("LEFTPADDING", (0,0), (-1,-1), 10),
        ("RIGHTPADDING",(0,0), (-1,-1), 10),
        ("ROUNDEDCORNERS", [4]),
    ]))
    story.append(sum_table)
    story.append(Spacer(1, 20))

    # ── DOMAIN SCORES ─────────────────────────────────────────────────
    story.append(Paragraph("Domain Scores", h1_style))
    story.append(HRFlowable(
        width="100%", thickness=2,
        color=ORANGE, spaceAfter=10,
    ))

    domain_header = [
        Paragraph("<b>Domain</b>",         center_style),
        Paragraph("<b>Score</b>",          center_style),
        Paragraph("<b>Maturity Level</b>", center_style),
        Paragraph("<b>Coverage</b>",       center_style),
        Paragraph("<b>Questions</b>",      center_style),
    ]
    domain_rows = [domain_header]
    for domain, info in domain_scores.items():
        sc  = float(info.get("score", 0))
        lbl = (
            "Initial"    if sc < 1.0 else
            "Developing" if sc < 2.0 else
            "Defined"    if sc < 3.0 else
            "Managed"    if sc < 4.0 else
            "Optimising"
        )
        cov = f"{(sc/5.0)*100:.1f}%"
        q   = str(info.get("count", info.get("question_count", 0)))
        domain_rows.append([
            Paragraph(str(domain), body_style),
            Paragraph(f"{sc:.2f}/5.00", center_style),
            Paragraph(lbl,              center_style),
            Paragraph(cov,              center_style),
            Paragraph(q,                center_style),
        ])

    dom_table = Table(
        domain_rows,
        colWidths=[1.5*inch, 1.0*inch, 1.3*inch, 0.9*inch, 0.8*inch],
    )
    dom_table.setStyle(TableStyle([
        ("BACKGROUND",  (0,0), (-1,0), NAVY),
        ("TEXTCOLOR",   (0,0), (-1,0), WHITE),
        ("FONTNAME",    (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",    (0,0), (-1,-1), 9),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[WHITE, LGRAY]),
        ("GRID",        (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ("TOPPADDING",  (0,0), (-1,-1), 6),
        ("BOTTOMPADDING",(0,0),(-1,-1), 6),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
        ("RIGHTPADDING",(0,0), (-1,-1), 8),
        ("ALIGN",       (1,0), (-1,-1), "CENTER"),
    ]))
    story.append(dom_table)
    story.append(Spacer(1, 20))

    # ── EVIDENCE COVERAGE (CyberMAP 2.0) ────────────────────────────────
    if evidence_summary:
        story.append(Paragraph("Evidence Coverage", h1_style))
        story.append(HRFlowable(
            width="100%", thickness=2,
            color=ORANGE, spaceAfter=10,
        ))
        total_e   = evidence_summary.get("total_eligible", 0)
        with_e    = evidence_summary.get("with_evidence", 0)
        pct_e     = evidence_summary.get("coverage_pct", 0)

        story.append(Paragraph(
            f"Of the {total_e} technical, evidence-eligible controls in "
            f"this assessment, <b>{with_e}</b> had supporting evidence "
            f"(screenshots, configuration exports, or automated scanner "
            f"reports) attached at the time of scoring — an evidence "
            f"coverage of <b>{pct_e}%</b>. The remaining evidence-eligible "
            f"controls, and all governance/process controls, were "
            f"self-reported without attached proof.",
            body_style,
        ))
        story.append(Spacer(1, 16))

    # ── AI EXPLANATION (CyberMAP 2.0, SHAP) ─────────────────────────────
    if shap_explanation:
        story.append(Paragraph("AI Risk Classification — Explanation", h1_style))
        story.append(HRFlowable(
            width="100%", thickness=2,
            color=ORANGE, spaceAfter=10,
        ))
        story.append(Paragraph(
            shap_explanation.get("explanation_text", ""),
            body_style,
        ))
        story.append(Spacer(1, 8))

        contrib = shap_explanation.get("domain_contributions", {})
        if contrib:
            contrib_header = [
                Paragraph("<b>Domain</b>", center_style),
                Paragraph("<b>Contribution to Prediction</b>", center_style),
            ]
            contrib_rows = [contrib_header]
            for dom, val in contrib.items():
                sign = "+" if val >= 0 else ""
                contrib_rows.append([
                    Paragraph(dom, body_style),
                    Paragraph(f"{sign}{val:.3f}", center_style),
                ])
            contrib_table = Table(contrib_rows, colWidths=[2.5*inch, 2.5*inch])
            contrib_table.setStyle(TableStyle([
                ("BACKGROUND",  (0,0), (-1,0), PURPLE),
                ("TEXTCOLOR",   (0,0), (-1,0), WHITE),
                ("FONTNAME",    (0,0), (-1,0), "Helvetica-Bold"),
                ("FONTSIZE",    (0,0), (-1,-1), 9),
                ("ROWBACKGROUNDS",(0,1),(-1,-1),[WHITE, LGRAY]),
                ("GRID",        (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
                ("TOPPADDING",  (0,0), (-1,-1), 5),
                ("BOTTOMPADDING",(0,0),(-1,-1), 5),
            ]))
            story.append(contrib_table)
        story.append(Spacer(1, 16))

    # ── GAP ANALYSIS ──────────────────────────────────────────────────
    story.append(Paragraph("Gap Analysis", h1_style))
    story.append(HRFlowable(
        width="100%", thickness=2,
        color=ORANGE, spaceAfter=10,
    ))

    crit = sum(1 for g in gaps if g.get("severity") == "Critical")
    high = sum(1 for g in gaps if g.get("severity") == "High")
    med  = sum(1 for g in gaps if g.get("severity") == "Medium")

    story.append(Paragraph(
        f"Total gaps identified: <b>{len(gaps)}</b> — "
        f"Critical: <b>{crit}</b> | High: <b>{high}</b> | Medium: <b>{med}</b>",
        body_style,
    ))
    story.append(Spacer(1, 8))

    if gaps:
        gap_header = [
            Paragraph("<b>Severity</b>",       center_style),
            Paragraph("<b>Domain</b>",          center_style),
            Paragraph("<b>Control</b>",         center_style),
            Paragraph("<b>Score</b>",           center_style),
            Paragraph("<b>NIST Ref</b>",        center_style),
            Paragraph("<b>Recommendation</b>",  center_style),
        ]
        gap_rows = [gap_header]
        for g in gaps[:40]:   # cap at 40 rows for PDF length
            sev  = str(g.get("severity",       ""))
            dom  = str(g.get("domain",         ""))
            sub  = str(g.get("subdomain",      ""))[:30]
            sc   = str(g.get("score",          ""))
            nist = str(g.get("nist_ref",       ""))
            rec  = str(g.get("recommendation", ""))[:60]
            sev_col = get_severity_colour(sev)
            gap_rows.append([
                Paragraph(sev,  ParagraphStyle("s", parent=center_style,
                    textColor=sev_col, fontName="Helvetica-Bold")),
                Paragraph(dom,  body_style),
                Paragraph(sub,  body_style),
                Paragraph(sc,   center_style),
                Paragraph(nist, center_style),
                Paragraph(rec,  body_style),
            ])

        gap_table = Table(
            gap_rows,
            colWidths=[0.7*inch, 0.9*inch, 1.1*inch,
                       0.5*inch, 0.8*inch, 1.5*inch],
        )
        gap_table.setStyle(TableStyle([
            ("BACKGROUND",   (0,0), (-1,0), NAVY),
            ("TEXTCOLOR",    (0,0), (-1,0), WHITE),
            ("FONTNAME",     (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE",     (0,0), (-1,-1), 8),
            ("ROWBACKGROUNDS",(0,1),(-1,-1),[WHITE, LGRAY]),
            ("GRID",         (0,0), (-1,-1), 0.5,
             colors.HexColor("#e2e8f0")),
            ("TOPPADDING",   (0,0), (-1,-1), 5),
            ("BOTTOMPADDING",(0,0), (-1,-1), 5),
            ("LEFTPADDING",  (0,0), (-1,-1), 5),
            ("RIGHTPADDING", (0,0), (-1,-1), 5),
            ("VALIGN",       (0,0), (-1,-1), "TOP"),
        ]))
        story.append(gap_table)

        if len(gaps) > 40:
            story.append(Spacer(1, 6))
            story.append(Paragraph(
                f"Showing top 40 of {len(gaps)} gaps. "
                f"View all gaps in the CyberMAP platform.",
                ParagraphStyle("note", parent=body_style,
                    textColor=SLATE, fontSize=8),
            ))
    else:
        story.append(Paragraph(
            "No gaps identified. All controls meet the Defined threshold.",
            body_style,
        ))

    story.append(Spacer(1, 20))

    # ── PRIORITY-RANKED TOP FIXES (CyberMAP 2.0) ────────────────────────
    if priority_gaps:
        story.append(Paragraph("Priority-Ranked Remediation", h1_style))
        story.append(HRFlowable(
            width="100%", thickness=2,
            color=ORANGE, spaceAfter=10,
        ))
        story.append(Paragraph(
            "Gaps below are ranked using Priority Score = (Severity × "
            "Business Impact × Exploitability) ÷ Remediation Effort, "
            "which surfaces high-value, low-effort fixes ahead of gaps "
            "that are severe but costly or lower-impact to remediate.",
            body_style,
        ))
        story.append(Spacer(1, 8))

        top_priority = sorted(
            priority_gaps, key=lambda g: g.get("priority_score", 0), reverse=True
        )[:5]

        pr_header = [
            Paragraph("<b>Rank</b>", center_style),
            Paragraph("<b>Priority Score</b>", center_style),
            Paragraph("<b>Domain / Control</b>", center_style),
            Paragraph("<b>Recommendation</b>", center_style),
        ]
        pr_rows = [pr_header]
        for i, g in enumerate(top_priority, 1):
            pr_rows.append([
                Paragraph(str(i), center_style),
                Paragraph(str(g.get("priority_score", "")), center_style),
                Paragraph(f"{g.get('domain','')} — {g.get('subdomain','')}", body_style),
                Paragraph(str(g.get("recommendation", ""))[:70], body_style),
            ])
        pr_table = Table(pr_rows, colWidths=[0.5*inch, 1.0*inch, 1.5*inch, 2.0*inch])
        pr_table.setStyle(TableStyle([
            ("BACKGROUND",   (0,0), (-1,0), NAVY),
            ("TEXTCOLOR",    (0,0), (-1,0), WHITE),
            ("FONTNAME",     (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE",     (0,0), (-1,-1), 8),
            ("ROWBACKGROUNDS",(0,1),(-1,-1),[WHITE, LGRAY]),
            ("GRID",         (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
            ("TOPPADDING",   (0,0), (-1,-1), 5),
            ("BOTTOMPADDING",(0,0), (-1,-1), 5),
        ]))
        story.append(pr_table)
        story.append(Spacer(1, 20))

    # ── RECOMMENDATIONS ───────────────────────────────────────────────
    story.append(Paragraph("Top Recommendations", h1_style))
    story.append(HRFlowable(
        width="100%", thickness=2,
        color=ORANGE, spaceAfter=10,
    ))

    seen_recs = set()
    count     = 0
    for g in gaps:
        rec = str(g.get("recommendation", "")).strip()
        if rec and rec not in seen_recs and count < 10:
            seen_recs.add(rec)
            count += 1
            story.append(Paragraph(
                f"{count}. [{g.get('domain','')} — "
                f"{g.get('severity','')}] {rec}",
                body_style,
            ))

    story.append(Spacer(1, 20))

    # ── FOOTER NOTE ───────────────────────────────────────────────────
    story.append(HRFlowable(
        width="100%", thickness=1,
        color=SLATE, spaceAfter=6,
    ))
    story.append(Paragraph(
        f"Generated by CyberMAP 2.0 on {date_str}  |  "
        f"NIST CSF 2.0 + ISO/IEC 27001:2022  |  "
        f"M.Tech Cybersecurity Capstone — RACE, REVA University",
        ParagraphStyle("footer", parent=center_style,
            fontSize=7, textColor=SLATE),
    ))

    # ── BUILD ─────────────────────────────────────────────────────────
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()