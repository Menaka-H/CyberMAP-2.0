# 🛡️ CyberMAP
### Cybersecurity Maturity Assessment Automation Platform

---

## 📌 Overview

CyberMAP is an AI-powered web application that automates cybersecurity
maturity assessments for large enterprises. The platform maps 194 security
controls to NIST Cybersecurity Framework 2.0 and ISO/IEC 27001:2022
simultaneously, providing automated gap analysis, risk classification
and actionable security recommendations.

---

## ⚡ Key Features

- 194-question assessment engine across 6 NIST CSF 2.0 domains
- AI/ML risk classification using Gradient Boosting — 96.6% accuracy
- Automated gap analysis with Critical, High and Medium severity
- Compliance checker — DPDP, GDPR, PCI-DSS, HIPAA, ISO 27001
- 90-day remediation roadmap with Gantt chart
- Executive scorecard with traffic-light domain ratings
- Industry benchmarking against 7 sector averages
- Attack impact simulation for 5 real-world threat scenarios
- Security Program Builder with downloadable policy templates
- Professional PDF report generation
- Multi-user role-based access — Admin, Assessor, Viewer

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| Language | Python 3.10.4 |
| Web Framework | Streamlit 1.35.0 |
| ML Model | Scikit-learn GradientBoostingClassifier |
| Database | SQLite |
| Visualisation | Plotly |
| PDF Generation | ReportLab |
| Authentication | SHA-256 hashing |

---

## 🚀 Setup and Installation

Step 1 — Clone the repository
git clone https://github.com/Menaka-H/CyberMAP.git
cd CyberMAP

Step 2 — Create virtual environment
python -m venv venv
venv\Scripts\activate

Step 3 — Install dependencies
pip install -r requirements.txt

Step 4 — Run the application
streamlit run app.py

Step 5 — Open browser at http://localhost:8501

---

## 🔐 Default Login Accounts

| Username | Password | Role |
|---|---|---|
| admin | admin123 | Administrator |
| menaka | cyber2024 | Assessor |
| viewer | view123 | Viewer |

---

## 📊 Platform Pages

| No | Page | Feature |
|---|---|---|
| 1 | Dashboard | KPI cards, trend chart, risk distribution |
| 2 | New Assessment | 194 questions across 6 NIST domains |
| 3 | Results and Analysis | Gauge, radar, bar charts, PDF download |
| 4 | History | All past assessments with progress bars |
| 5 | AI Advisor | Context-aware security chatbot |
| 6 | Attack Simulation | 5 threat scenario probability gauges |
| 7 | Benchmarking | 7 industry sector comparison |
| 8 | Compliance Checker | DPDP, GDPR, PCI-DSS, HIPAA, ISO 27001 |
| 9 | Remediation Roadmap | 90-day Gantt chart action plan |
| 10 | Executive Scorecard | Traffic-light board-level summary |
| 11 | Security Builder | Step guide, tools, budget, policies |

---

## 🧠 ML Model

| Parameter | Value |
|---|---|
| Algorithm | GradientBoostingClassifier |
| Training Samples | 1200 synthetic profiles |
| Cross-Validation | 5-fold stratified |
| Accuracy | 96.6% |
| Risk Classes | Critical, High, Medium, Low |

---

## 📋 NIST CSF 2.0 Coverage

| Domain | Questions |
|---|---|
| Govern | 35 |
| Identify | 32 |
| Protect | 45 |
| Detect | 30 |
| Respond | 26 |
| Recover | 26 |
| Total | 194 |

---

## 📄 License

For academic and educational use only.