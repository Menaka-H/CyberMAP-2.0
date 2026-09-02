# CyberMAP 2.0

### Evidence-Driven and Continuously Monitored Maturity Assessment Platform

M.Tech Cybersecurity Capstone Project 2

![Python](https://img.shields.io/badge/Python-3.10-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)
![Status](https://img.shields.io/badge/Status-Complete-brightgreen)

## Overview

CyberMAP 2.0 extends the original CyberMAP platform into an evidence-verified, continuously monitored, and explainable system.

## What's New in 2.0

| Feature | Description |
|---|---|
| Evidence Upload and Repository | Optional file evidence, hash-chained for tamper detection |
| Endpoint Security Posture Scanner | Checks firewall, antivirus, password policy, encryption, patches, services |
| Continuous Monitoring | Task Scheduler runs the scanner automatically; drift is detected and logged |
| Email Alerting | Real email sent via Gmail SMTP when a control regresses |
| Human-in-the-Loop Remediation | Reversible fixes executed with two-step confirmation and re-verification |
| Explainable AI (SHAP) | Every risk classification includes a plain-English explanation |
| Vulnerability-to-Maturity Mapping | Live NVD lookup with local caching |
| Predictive Maturity Analysis | Projects future maturity scores from assessment history |
| Automated Policy Gap Analyzer | Checks uploaded policy PDFs against NIST/ISO requirements |
| Security Control Prioritization Engine | Ranks gaps by severity, impact, exploitability, and effort |
| Fleet Import | Aggregates scan reports from multiple endpoints |

## Tech Stack

- Python 3.10
- Streamlit
- SQLite
- Scikit-learn + SHAP
- psutil / wmi / pywin32
- Windows Task Scheduler
- NIST NVD REST API
- Gmail SMTP (smtplib)
- pypdf, ReportLab

## Setup

git clone https://github.com/Menaka-H/CyberMAP-2.0.git
cd CyberMAP-2.0
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

Create a .env file in the project root (not committed to this repository) with:

GMAIL_ADDRESS=your_email@gmail.com
GMAIL_APP_PASSWORD=your_16_char_app_password
ALERT_RECIPIENT=your_email@gmail.com

Run the application:

streamlit run app.py

Note: several features require Administrator privileges on Windows.

## Project Structure

- app.py - Main Streamlit application
- scanner.py - Standalone endpoint security scanner
- scheduled_scan.py - Wrapper for Task Scheduler
- pg_*.py - Streamlit page modules
- utils/database.py - SQLite storage, evidence, hash chain
- utils/scoring.py - Weighted maturity scoring
- utils/ml_model.py - Gradient Boosting + SHAP
- utils/prioritization.py - Priority score engine
- utils/remediation.py - Human-in-the-loop remediation
- utils/vulnerability_mapping.py - Live NVD CVE lookup
- utils/predictive_analysis.py - Maturity trend forecasting
- utils/policy_analyzer.py - Policy PDF gap analysis
- utils/alerting.py - Email alerting
- data/ - SQLite database (not committed)
