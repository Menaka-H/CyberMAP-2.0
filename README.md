<div align="center">

# 🛡️ CyberMAP
### Cybersecurity Maturity Assessment Automation Platform

![Python](https://img.shields.io/badge/Python-3.10.4-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35.0-red?style=for-the-badge&logo=streamlit)
![ML](https://img.shields.io/badge/ML-96.6%25_Accuracy-green?style=for-the-badge)
![SQLite](https://img.shields.io/badge/Database-SQLite-lightblue?style=for-the-badge&logo=sqlite)
![NIST](https://img.shields.io/badge/NIST-CSF_2.0-darkblue?style=for-the-badge)
![ISO](https://img.shields.io/badge/ISO-27001:2022-orange?style=for-the-badge)

</div>

---

## 📌 Overview

**CyberMAP** is a full-stack, AI-powered web application that automates cybersecurity maturity assessments for large enterprises. The platform maps **194 security controls** to **NIST Cybersecurity Framework 2.0** and **ISO/IEC 27001:2022** simultaneously. Using a **Gradient Boosting ML classifier** with **96.6% accuracy**, it automatically classifies organisational risk and generates gap analysis, compliance reports and remediation plans.

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

## 🚀 Quick Start

**1. Clone the repository**

    git clone https://github.com/Menaka-H/CyberMAP.git
    cd CyberMAP

**2. Create virtual environment**

    python -m venv venv
    venv\Scripts\activate

**3. Install dependencies**

    pip install -r requirements.txt

**4. Run the application**

    streamlit run app.py

**5. Open browser at** http://localhost:8501

---

## 🔐 Login Accounts

| Username | Password | Role | Access |
|---|---|---|---|
| `admin` | `admin123` | 🔴 Administrator | All 11 pages |
| `menaka` | `cyber2024` | 🔵 Assessor | Assessment and Analysis |
| `viewer` | `view123` | 🟢 Viewer | Read-only |

---

## 📊 Platform Pages

| No | Page | Feature |
|---|---|---|
| 1 | 🏠 Dashboard | KPI cards, trend chart, risk distribution |
| 2 | 📋 New Assessment | 194 questions across 6 NIST domains |
| 3 | 📊 Results and Analysis | Gauge, radar, bar charts, PDF download |
| 4 | 📁 History | All past assessments with progress bars |
| 5 | 🤖 AI Advisor | Context-aware security chatbot |
| 6 | 💥 Attack Simulation | 5 threat scenario probability gauges |
| 7 | 📈 Benchmarking | 7 industry sector comparison |
| 8 | ✅ Compliance Checker | DPDP, GDPR, PCI-DSS, HIPAA, ISO 27001 |
| 9 | 🗺️ Remediation Roadmap | 90-day Gantt chart action plan |
| 10 | 📋 Executive Scorecard | Traffic-light board-level summary |
| 11 | 🏗️ Security Builder | Step guide, tools, budget, policies |

---

## 🏗️ System Architecture

    ┌─────────────────────────────────────┐
    │        PRESENTATION LAYER           │
    │         11 Streamlit Pages          │
    └──────────────┬──────────────────────┘
                   │
    ┌──────────────▼──────────────────────┐
    │        APPLICATION LAYER            │
    │        app.py + auth.py             │
    │   Login │ Sessions │ Role Routing   │
    └──────────────┬──────────────────────┘
                   │
    ┌──────────────▼──────────────────────┐
    │        PROCESSING LAYER             │
    │           scoring.py                │
    │  Weighted Scoring │ Gap Analysis    │
    └──────────────┬──────────────────────┘
                   │
    ┌──────────────▼──────────────────────┐
    │        INTELLIGENCE LAYER           │
    │          ml_model.py                │
    │  GradientBoosting Risk Classifier   │
    └──────────────┬──────────────────────┘
                   │
    ┌──────────────▼──────────────────────┐
    │           DATA LAYER                │
    │    database.py + cybermap.db        │
    │       SQLite Persistent Storage     │
    └─────────────────────────────────────┘

---

## 🧠 ML Model

| Parameter | Value |
|---|---|
| Algorithm | GradientBoostingClassifier |
| Training Samples | 1,200 synthetic profiles |
| Per Class | 300 profiles × 4 classes |
| Cross-Validation | 5-fold stratified |
| Accuracy | 96.6% (± 5.4%) |
| Risk Classes | Critical, High, Medium, Low |
| Prediction Time | < 0.1 seconds |

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
| **Total** | **6** | **194** | **NIST CSF 2.0 + ISO 27001** |

---

## 📈 Maturity Scoring Formula

    Domain Score = (Σ answer × weight) / (Σ 5.0 × weight) × 5.0

    Gap Severity Classification:
    Critical  →  Score 0.0 – 1.0  →  Days 1–7   (Immediate)
    High      →  Score 1.0 – 2.0  →  Days 8–30  (Short-term)
    Medium    →  Score 2.0 – 3.0  →  Days 31–90 (Medium-term)

---

## 📄 License

For academic and educational use only.