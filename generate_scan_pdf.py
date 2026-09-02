# generate_scan_pdf.py — Converts a CyberMAP scan report JSON
# into a readable, professional PDF with explanations.
#
# Usage:
#     python generate_scan_pdf.py CyberMAP_ScanReport_XXXXXXXX.json

import sys
import json
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)
from reportlab.lib import colors
from reportlab.lib.units import cm

# ── Plain-English explanation for each check ───────────────────
EXPLANATIONS = {
    "Firewall Status": (
        "Checks whether the Windows Firewall is enabled on all three "
        "network profiles (Domain, Private, Public). A disabled firewall "
        "on any profile allows unfiltered network traffic to reach the "
        "machine, increasing exposure to network-based attacks."
    ),
    "Antivirus / EDR Status": (
        "Checks whether an antivirus or endpoint detection product is "
        "registered and active with Windows Security Center. Without "
        "active endpoint protection, malware and known threats are not "
        "automatically detected or blocked."
    ),
    "Password Policy": (
        "Reads the system's minimum password length requirement. A "
        "minimum length of 0 or below 8 characters means weak, easily "
        "guessed or brute-forced passwords are permitted, significantly "
        "increasing the risk of unauthorised account access."
    ),
    "Disk Encryption": (
        "Checks whether BitLocker disk encryption is enabled and the "
        "percentage of the volume encrypted. An unencrypted disk means "
        "that if the physical device is lost or stolen, all data on it "
        "can be read without needing any credentials."
    ),
    "Patch / Update Status": (
        "Confirms that Windows updates are being installed on this "
        "machine by checking for recorded update history. Regular "
        "patching closes known vulnerabilities before they can be "
        "exploited."
    ),
    "Unnecessary Services": (
        "Scans currently running Windows services for a fixed watch-list "
        "of historically risky services (Telnet, Remote Registry, FTP "
        "Server). These services, if running unnecessarily, expand the "
        "attack surface available to an attacker."
    ),
}

STATUS_COLORS = {
    "PASS":    colors.HexColor("#1E7C34"),
    "PARTIAL": colors.HexColor("#8A6D00"),
    "FAIL":    colors.HexColor("#B00020"),
    "ERROR":   colors.HexColor("#666666"),
}


def generate_pdf(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        report = json.load(f)

    meta    = report["scan_metadata"]
    results = report["results"]
    summary = report["summary"]
    report_hash = report.get("report_hash", "N/A")

    pdf_name = json_path.replace(".json", ".pdf")
    doc = SimpleDocTemplate(
        pdf_name, pagesize=A4,
        topMargin=1.8 * cm, bottomMargin=1.8 * cm,
        leftMargin=1.8 * cm, rightMargin=1.8 * cm,
    )
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleStyle", parent=styles["Title"],
        fontSize=18, textColor=colors.HexColor("#1F3864"),
        spaceAfter=4,
    )
    sub_style = ParagraphStyle(
        "SubStyle", parent=styles["Normal"],
        fontSize=10, textColor=colors.grey, spaceAfter=16,
    )
    h2_style = ParagraphStyle(
        "H2Style", parent=styles["Heading2"],
        fontSize=13, textColor=colors.HexColor("#1F3864"),
        spaceBefore=14, spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "BodyStyle", parent=styles["Normal"],
        fontSize=10, leading=14, spaceAfter=6,
    )
    mono_style = ParagraphStyle(
        "MonoStyle", parent=styles["Normal"],
        fontName="Courier", fontSize=8, leading=11,
        backColor=colors.HexColor("#F5F5F5"),
        borderPadding=6, spaceAfter=10,
    )

    story = []

    # ── Header ───────────────────────────────────────────────
    story.append(Paragraph("CyberMAP 2.0 — Endpoint Security Scan Report", title_style))
    story.append(Paragraph(
        f"Host: {meta['hostname']}  |  OS: {meta['os']}  |  "
        f"Scan Time: {meta['scan_time']}",
        sub_style,
    ))

    # ── Summary table ────────────────────────────────────────
    story.append(Paragraph("Scan Summary", h2_style))
    summary_data = [
        ["Total Checks", "Passed", "Partial", "Failed", "Errors"],
        [
            str(summary["total"]), str(summary["passed"]),
            str(summary["partial"]), str(summary["failed"]),
            str(summary["errors"]),
        ],
    ]
    summary_table = Table(summary_data, colWidths=[3.2 * cm] * 5)
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F3864")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D9D9D9")),
        ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#F2F2F2")),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 10))

    # ── Per-check detail ─────────────────────────────────────
    story.append(Paragraph("Detailed Check Results", h2_style))

    for r in results:
        status = r["status"]
        status_color = STATUS_COLORS.get(status, colors.black)

        header_line = (
            f'<font color="{status_color.hexval()}"><b>{r["check"]} — {status}</b></font>'
            f'&nbsp;&nbsp;&nbsp;<font size=8 color="#666666">'
            f'{r["nist_ref"]} / {r["iso_ref"]}</font>'
        )
        story.append(Paragraph(header_line, body_style))

        explanation = EXPLANATIONS.get(
            r["check"], "No explanation available for this check."
        )
        story.append(Paragraph(f"<i>{explanation}</i>", body_style))

        raw_output = r["raw_output"].replace("\n", "<br/>")
        raw_output = raw_output[:600]  # keep PDF readable
        story.append(Paragraph(
            f"<b>Raw command output:</b><br/>{raw_output}", mono_style
        ))
        story.append(Spacer(1, 6))

    # ── Integrity footer ─────────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("Report Integrity", h2_style))
    story.append(Paragraph(
        "This report's contents are hashed using SHA-256 at the moment "
        "of generation. Any modification to the underlying JSON file "
        "after generation would produce a different hash, making "
        "tampering detectable.",
        body_style,
    ))
    story.append(Paragraph(
        f"<b>SHA-256 Report Hash:</b><br/>{report_hash}", mono_style
    ))
    story.append(Paragraph(
        f"Generated by CyberMAP 2.0 Endpoint Scanner on "
        f"{datetime.now().strftime('%d %B %Y, %H:%M')}",
        sub_style,
    ))

    doc.build(story)
    print(f"✅ PDF generated: {pdf_name}")
    return pdf_name


if __name__ == "__main__":
    if len(sys.argv) < 2:
        # If no filename given, find the most recent scan report automatically
        json_files = [
            f for f in os.listdir(".")
            if f.startswith("CyberMAP_ScanReport_") and f.endswith(".json")
        ]
        if not json_files:
            print("❌ No scan report JSON found. Run scanner.py first.")
            sys.exit(1)
        json_files.sort(reverse=True)
        json_path = json_files[0]
        print(f"No filename given — using most recent report: {json_path}")
    else:
        json_path = sys.argv[1]

    generate_pdf(json_path)