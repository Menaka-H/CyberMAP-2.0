# CyberMAP 2.0

### Evidence-Driven & Continuously Monitored Maturity Assessment Platform

M.Tech Cybersecurity Capstone Project 2

---

## Overview

CyberMAP 2.0 extends the original CyberMAP platform from a purely self-reported cybersecurity maturity assessment into an evidence-verified, continuously monitored, and explainable system. Instead of trusting answers alone, the platform collects real endpoint evidence, monitors security posture over time, explains its own AI risk predictions, and connects assessment gaps to real known vulnerabilities.

---

## What's New in 2.0

| Feature | Description |
|---|---|
| Evidence Upload and Repository | Optional file evidence attached to technical questions, hash-chained for tamper detection |
| Endpoint Security Posture Scanner | Standalone script checking firewall, antivirus, password policy, encryption, patches, and services |
| Continuous Monitoring | Windows Task Scheduler runs the scanner automatically; drift between scans is detected and logged |
| Email Alerting | Real email sent via Gmail SMTP when a security control regresses |
| Human-in-the-Loop Remediation | Approved, reversible fixes can be executed with explicit two-step confirmation and automatic re-verification |
| Explainable AI (SHAP) | Every risk classification includes a plain-English explanation of which domains drove the result |
| Vulnerability-to-Maturity Mapping | Live lookup against the NIST National Vulnerability Database, with local caching |
| Predictive Maturity Analysis | Projects future maturity scores from an organisation's assessment history |
| Automated Policy Gap Analyzer | Upload a policy PDF and check it against NIST/ISO governance requirements |
| Security Control Prioritization Engine | Ranks gaps by severity, business impact, exploitability, and effort — not severity alone |
| Fleet Import | Aggregates scan reports from multiple endpoints into one fleet-wide view |

---

## Tech Stack

- Python 3.10
- Streamlit
- SQLite
- Scikit-learn + SHAP
- psutil / wmi / pywin32 (endpoint scanning)
- Windows Task Scheduler
- NIST NVD REST API
- Gmail SMTP (smtplib)
- pypdf, ReportLab

---

## Setup

```bash
git clone https://github.com/Menaka-H/CyberMAP-2.0.git
cd CyberMAP-2.0
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in the project root (not committed to this repository) with: