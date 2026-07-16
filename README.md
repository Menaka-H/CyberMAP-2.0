<div align="center">

# 🛡️ CyberMAP
### Cybersecurity Maturity Assessment Automation Platform

![Python](https://img.shields.io/badge/Python-3.10.4-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35.0-red?style=for-the-badge&logo=streamlit)
![Scikit-learn](https://img.shields.io/badge/ML-96.6%25_Accuracy-green?style=for-the-badge&logo=scikit-learn)
![SQLite](https://img.shields.io/badge/Database-SQLite-lightblue?style=for-the-badge&logo=sqlite)
![NIST](https://img.shields.io/badge/NIST-CSF_2.0-navy?style=for-the-badge)
![ISO](https://img.shields.io/badge/ISO-27001:2022-orange?style=for-the-badge)

</div>

---

## 📌 Overview

**CyberMAP** is a full-stack, AI-powered web application that automates
cybersecurity maturity assessments for large enterprises.

The platform maps **194 security controls** to:
- ✅ **NIST Cybersecurity Framework 2.0 (CSF 2.0)**
- ✅ **ISO/IEC 27001:2022**

Using a **Gradient Boosting ML classifier** with **96.6% accuracy**, it
automatically classifies organisational risk as Critical, High, Medium or Low
and generates automated gap analysis, compliance reports and remediation plans.

---

## ⚡ Key Features

| Feature | Description |
|---|---|
| 📋 Assessment Engine | 194 questions across 6 NIST CSF 2.0 domains |
| 🤖 AI/ML Classification | Gradient Boosting — 96.6% cross-validation accuracy |
| 🔍 Gap Analysis | Automated Critical, High, Medium severity classification |
| ✅ Compliance Checker | DPDP, GDPR, PCI-DSS, HIPAA, ISO 27001 |
| 🗺️ Remediation Roadmap | Auto-generated 90-day plan with Gantt chart |
| 📋 Executive Scorecard | Traffic-light domain ratings for board level |
| 📈 Benchmarking | Compare against 7 industry sector averages |
| 💥 Attack Simulation | 5 real-world threat scenario gauges |
| 🏗️ Security Builder | Step guide, tools, budget, policy templates |
| 📄 PDF Reports | Professional multi-page report generation |
| 🔐 Role-Based Access | Admin, Assessor, Viewer with distinct permissions |

---

## 🛠️ Tech Stack

Python 3.10.4  →  Core Language
Streamlit      →  Web Application Framework
Scikit-learn   →  GradientBoostingClassifier (ML)
SQLite         →  Database
Plotly         →  Interactive Charts
ReportLab      →  PDF Generation
SHA-256        →  Password Hashing

---

## 🚀 Quick Start

**1. Clone the repository**
```bash
git clone https://github.com/Menaka-H/CyberMAP.git
cd CyberMAP
```

**2. Create virtual environment**
```bash
python -m venv venv
venv\Scripts\activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Run the application**
```bash
streamlit run app.py
```

**5. Open browser**

---

## 🔐 Login Accounts

| Username | Password | Role | Access |
|---|---|---|---|
| `admin` | `admin123` | 🔴 Administrator | All 11 pages |
| `menaka` | `cyber2024` | 🔵 Assessor | Assessment + Analysis |
| `viewer` | `view123` | 🟢 Viewer | Read-only |

---

## 📊 Platform Pages

🏠  Dashboard          →  KPI cards, trend charts, risk distribution
📋  New Assessment     →  194 questions across 6 NIST CSF 2.0 domains
📊  Results            →  Gauge, radar, bar charts + PDF download
📁  History            →  All past assessments with progress bars
🤖  AI Advisor         →  Context-aware security chatbot
💥  Attack Simulation  →  5 threat scenario probability gauges
📈  Benchmarking       →  7 industry sector radar comparison
✅  Compliance         →  DPDP, GDPR, PCI-DSS, HIPAA, ISO 27001
🗺️  Roadmap            →  90-day Gantt chart remediation plan
📋  Scorecard          →  Traffic-light board-level summary
🏗️  Security Builder   →  Step guide, tools, budget, policies

---

## 🧠 ML Model
Algorithm      :  GradientBoostingClassifier (Scikit-learn)
Training Data  :  1,200 synthetic organisational profiles
Per Class      :  300 profiles × 4 classes
Cross-Val      :  5-fold stratified
Accuracy       :  96.6% (± 5.4%)
Risk Classes   :  Critical | High | Medium | Low
Features       :  6 NIST domain maturity scores (0.0 – 5.0)
Prediction     :  < 0.1 seconds per assessment

---

## 🏗️ System Architecture


---

## 📋 NIST CSF 2.0 Coverage

| Domain | Function | Questions | Focus Area |
|---|---|---|---|
| Govern | GV | 35 | Policy, roles, risk strategy |
| Identify | ID | 32 | Asset inventory, risk assessment |
| Protect | PR | 45 | Access control, data security |
| Detect | DE | 30 | Monitoring, SIEM, logging |
| Respond | RS | 26 | Incident management |
| Recover | RC | 26 | BCP, DRP, backup testing |
| **Total** | **6** | **194** | **Full NIST CSF 2.0 + ISO 27001** |

---

## 📈 Maturity Scoring Formula

Domain Score = (Σ answer_i × weight_i) / (Σ 5.0 × weight_i) × 5.0
Overall Score = Mean of all 6 domain scores
Gap Severity:
Critical  →  Score 0.0 – 1.0  →  Immediate action (Days 1–7)
High      →  Score 1.0 – 2.0  →  Short-term action (Days 8–30)
Medium    →  Score 2.0 – 3.0  →  Medium-term action (Days 31–90)

