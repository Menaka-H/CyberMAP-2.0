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

**CyberMAP** is a full-stack, AI-powered web application that automates
cybersecurity maturity assessments for large enterprises.

In today's rapidly evolving threat landscape, organisations face increasing
pressure to demonstrate a measurable and evidence-based security posture to
regulators, auditors and board-level stakeholders. Traditional cybersecurity
assessments are manual, time-consuming and inconsistent — often taking weeks
to complete and producing results that vary significantly depending on the
assessor. CyberMAP addresses these challenges by delivering a fully automated,
intelligent and integrated assessment platform.

The platform maps **194 security controls** simultaneously to:
- ✅ **NIST Cybersecurity Framework 2.0 (CSF 2.0)**
- ✅ **ISO/IEC 27001:2022**

Using a **Gradient Boosting ML classifier** with **96.6% cross-validation
accuracy**, CyberMAP automatically classifies organisational risk as Critical,
High, Medium or Low and generates automated gap analysis, compliance reports,
remediation plans and executive scorecards — all within a single thirty-minute
assessment session.

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

## 🏗️ System Architecture

CyberMAP follows a clean **five-layer architecture** where each layer has a
single well-defined responsibility and communicates only with adjacent layers.
This separation ensures that changes to one layer — for example replacing the
ML model — do not affect the UI or database layers.

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

## 🛠️ Tech Stack

CyberMAP is built entirely using free and open-source tools, requiring
no software licensing investment. The complete platform can be deployed
on any standard development machine without specialised infrastructure.

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

> On first launch, CyberMAP automatically creates the SQLite database,
> seeds all 194 questions and trains the ML model. This takes approximately
> 30 seconds and only happens once.

---

## 🔐 Login Accounts

Three role levels are available, each with distinct page access permissions.
The Administrator role has full access to all 11 pages and all platform
features. The Assessor role can run assessments and access all analysis pages.
The Viewer role provides read-only access to dashboard, results and history.

| Username | Password | Role | Access |
|---|---|---|---|
| `admin` | `admin123` | 🔴 Administrator | All 11 pages |
| `menaka` | `cyber2024` | 🔵 Assessor | Assessment and Analysis |
| `viewer` | `view123` | 🟢 Viewer | Read-only |

---

## 📊 Platform Pages

CyberMAP delivers 13 integrated feature modules across 11 pages, covering
the complete cybersecurity assessment lifecycle from data collection through
to board-level reporting.

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

## 🧠 ML Model

The risk classification model uses a **Gradient Boosting Classifier**
trained on 1,200 synthetic organisational profiles. The model takes six
domain maturity scores as input and predicts the overall risk level with
a quantified confidence percentage. This eliminates the subjectivity of
manual risk judgment and produces consistent, reproducible results across
every assessment.

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

The 194 assessment questions are distributed across all six NIST CSF 2.0
functions. Each question is individually tagged with a NIST subcategory
reference code and an ISO/IEC 27001:2022 clause, enabling a single
assessment to satisfy both frameworks simultaneously.

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

The weighted scoring formula ensures that more critical controls
(such as MFA enforcement) have a proportionally greater influence
on the domain score than lower-priority controls.

    Domain Score = (Σ answer × weight) / (Σ 5.0 × weight) × 5.0

    Overall Score = Arithmetic mean of all 6 domain scores

    Gap Severity:
    Critical  →  Score 0.0 – 1.0  →  Days 1–7   (Immediate action)
    High      →  Score 1.0 – 2.0  →  Days 8–30  (Short-term action)
    Medium    →  Score 2.0 – 3.0  →  Days 31–90 (Medium-term action)

---

## 📄 License

For academic and educational use only.