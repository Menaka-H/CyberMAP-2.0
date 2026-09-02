# utils/database.py
# This file creates and manages the SQLite database
# It handles: creating tables, saving assessments, fetching results

import sqlite3    # built into Python - no install needed
import os
import json
import hashlib
from datetime import datetime

# Path to the database file (auto-created inside the data/ folder)
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "cybermap.db")


def get_connection():
    """Open a connection to the database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # lets us access columns by name
    return conn


def init_db():
    """
    Create all tables if they don't exist yet.
    This runs every time the app starts - safe to run multiple times.
    """
    # Make sure the data/ folder exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    conn = get_connection()
    c = conn.cursor()

    # Create all tables
    c.executescript("""

        -- Table 1: Store organization info
        CREATE TABLE IF NOT EXISTS organizations (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            industry    TEXT,
            size        TEXT,
            created_at  TEXT DEFAULT (datetime('now'))
        );

        -- Table 2: Store each assessment and its results
        CREATE TABLE IF NOT EXISTS assessments (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            org_name        TEXT,
            assessor        TEXT,
            created_at      TEXT DEFAULT (datetime('now')),
            maturity_score  REAL,
            risk_level      TEXT,
            answers_json    TEXT,
            scores_json     TEXT,
            gaps_json       TEXT
        );

        -- Table 3: Store the security questions
        CREATE TABLE IF NOT EXISTS questions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            domain      TEXT NOT NULL,
            subdomain   TEXT,
            question    TEXT NOT NULL,
            nist_ref    TEXT,
            iso_ref     TEXT,
            weight      REAL DEFAULT 1.0
        );

        -- Table 4: Evidence uploads (CyberMAP 2.0)
        CREATE TABLE IF NOT EXISTS evidence (
            id                   INTEGER PRIMARY KEY AUTOINCREMENT,
            assessment_id        INTEGER,
            question_id          TEXT NOT NULL,
            filename             TEXT NOT NULL,
            file_path            TEXT NOT NULL,
            file_type            TEXT,
            sha256_hash          TEXT NOT NULL,
            chain_hash           TEXT,
            uploaded_by          TEXT,
            uploaded_at          TEXT DEFAULT (datetime('now')),
            verification_status  TEXT DEFAULT 'Pending',
            auditor_comment      TEXT,
            source               TEXT DEFAULT 'Manual'
        );

                 -- Table 5: Continuous monitoring snapshots (CyberMAP 2.0)
        CREATE TABLE IF NOT EXISTS monitoring_snapshots (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            endpoint_name  TEXT NOT NULL,
            scan_time      TEXT NOT NULL,
            report_json    TEXT NOT NULL,
            created_at     TEXT DEFAULT (datetime('now'))
        );

                -- Table 6: Remediation approvals (CyberMAP 2.0, simulated)
        CREATE TABLE IF NOT EXISTS remediation_log (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            gap_question      TEXT NOT NULL,
            nist_ref          TEXT,
            proposed_fix      TEXT NOT NULL,
            command_preview   TEXT,
            approved_by       TEXT,
            approval_status   TEXT DEFAULT 'Pending',
            simulated         INTEGER DEFAULT 1,
            created_at        TEXT DEFAULT (datetime('now'))
        );

        -- Table 7: CVE lookup cache (CyberMAP 2.0)
        CREATE TABLE IF NOT EXISTS cve_cache (
            nist_ref       TEXT PRIMARY KEY,
            keyword_used   TEXT,
            source         TEXT,
            cves_json      TEXT NOT NULL,
            cached_at      TEXT DEFAULT (datetime('now'))
        );

    """)

    conn.commit()   # save changes
    conn.close()    # close connection
    print("Database initialized successfully!")


def save_assessment(org_name, assessor, answers, scores,
                    maturity_score, risk_level, gaps):
    """Save a completed assessment to the database."""
    conn = get_connection()
    c = conn.cursor()

    c.execute(
        """INSERT INTO assessments
           (org_name, assessor, maturity_score, risk_level,
            answers_json, scores_json, gaps_json)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (
            org_name,
            assessor,
            maturity_score,
            risk_level,
            json.dumps(answers),   # convert dict to text for storage
            json.dumps(scores),
            json.dumps(gaps)
        )
    )

    assessment_id = c.lastrowid   # get the ID of what we just saved
    conn.commit()
    conn.close()
    return assessment_id


def get_all_assessments():
    """Fetch all assessments for the history page."""
    conn = get_connection()
    rows = conn.execute(
        """SELECT id, org_name, assessor, created_at,
                  maturity_score, risk_level
           FROM assessments
           ORDER BY id DESC"""   # newest first
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_assessment_by_id(assessment_id):
    """Fetch one specific assessment by its ID."""
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM assessments WHERE id = ?",
        (assessment_id,)
    ).fetchone()
    conn.close()

    if row:
        d = dict(row)
        # Convert stored text back to Python dicts
        d["answers"] = json.loads(d["answers_json"])
        d["scores"]  = json.loads(d["scores_json"])
        d["gaps"]    = json.loads(d["gaps_json"])
        return d
    return None


def get_questions():
    """Fetch all questions from the database."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM questions ORDER BY domain, id"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def seed_questions(questions_list):
    """
    Add questions to the database if the table is empty.
    We only do this once — on first run.
    """
    conn = get_connection()
    c = conn.cursor()

    # Check if questions already exist
    count = c.execute("SELECT COUNT(*) FROM questions").fetchone()[0]

    if count == 0:
        print("Adding questions to database...")
        for q in questions_list:
            c.execute(
                """INSERT INTO questions
                   (domain, subdomain, question, nist_ref, iso_ref, weight)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    q["domain"],
                    q["subdomain"],
                    q["question"],
                    q["nist_ref"],
                    q["iso_ref"],
                    q.get("weight", 1.0)
                )
            )
        conn.commit()
        print(f"{len(questions_list)} questions added!")
    else:
        print(f"Questions already exist ({count} found). Skipping.")

    conn.close()


# ══════════════════════════════════════════════════════════════
# EVIDENCE FUNCTIONS — CyberMAP 2.0
# ══════════════════════════════════════════════════════════════

def get_last_chain_hash():
    """
    Get the chain_hash of the most recently inserted evidence row.
    Used to build the next link in the hash chain.
    Returns an empty string if no evidence exists yet (first entry).
    """
    conn = get_connection()
    row = conn.execute(
        "SELECT chain_hash FROM evidence ORDER BY id DESC LIMIT 1"
    ).fetchone()
    conn.close()
    if row and row["chain_hash"]:
        return row["chain_hash"]
    return ""


def save_evidence(assessment_id, question_id, filename, file_path,
                   file_type, file_bytes, uploaded_by, source="Manual"):
    """
    Save one evidence file's metadata to the database.
    Computes:
      - sha256_hash  : hash of this file alone
      - chain_hash   : hash of (this file's hash + previous chain_hash)
                       this is what makes tampering detectable
    """
    # Hash of this file alone
    file_hash = hashlib.sha256(file_bytes).hexdigest()

    # Build the chain — link to the previous entry's chain_hash
    previous_chain_hash = get_last_chain_hash()
    chain_input = (file_hash + previous_chain_hash).encode()
    chain_hash = hashlib.sha256(chain_input).hexdigest()

    conn = get_connection()
    c = conn.cursor()
    c.execute(
        """INSERT INTO evidence
           (assessment_id, question_id, filename, file_path, file_type,
            sha256_hash, chain_hash, uploaded_by, source)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            assessment_id,
            question_id,
            filename,
            file_path,
            file_type,
            file_hash,
            chain_hash,
            uploaded_by,
            source,
        )
    )
    evidence_id = c.lastrowid
    conn.commit()
    conn.close()
    return evidence_id, file_hash, chain_hash


def get_evidence_for_question(question_id, assessment_id=None):
    """Fetch all evidence files attached to a specific question."""
    conn = get_connection()
    if assessment_id:
        rows = conn.execute(
            """SELECT * FROM evidence
               WHERE question_id = ? AND assessment_id = ?
               ORDER BY uploaded_at DESC""",
            (question_id, assessment_id)
        ).fetchall()
    else:
        rows = conn.execute(
            """SELECT * FROM evidence
               WHERE question_id = ?
               ORDER BY uploaded_at DESC""",
            (question_id,)
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_evidence(assessment_id=None):
    """Fetch all evidence — for the Evidence Repository page."""
    conn = get_connection()
    if assessment_id:
        rows = conn.execute(
            """SELECT * FROM evidence
               WHERE assessment_id = ?
               ORDER BY id ASC""",
            (assessment_id,)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM evidence ORDER BY id ASC"
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_evidence_status(evidence_id, status, comment=""):
    """
    Update an evidence file's verification status.
    status should be one of: 'Pending', 'Verified', 'Partial', 'Rejected'
    """
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        """UPDATE evidence
           SET verification_status = ?, auditor_comment = ?
           WHERE id = ?""",
        (status, comment, evidence_id)
    )
    conn.commit()
    conn.close()


def verify_evidence_chain():
    """
    Walk through all evidence rows in order and recompute the chain
    to confirm nothing has been tampered with or deleted out of order.
    Returns (is_valid: bool, broken_at_id: int or None)
    """
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM evidence ORDER BY id ASC"
    ).fetchall()
    conn.close()

    previous_chain_hash = ""
    for row in rows:
        expected_chain_input = (row["sha256_hash"] + previous_chain_hash).encode()
        expected_chain_hash = hashlib.sha256(expected_chain_input).hexdigest()

        if expected_chain_hash != row["chain_hash"]:
            return False, row["id"]

        previous_chain_hash = row["chain_hash"]

    return True, None

def link_evidence_to_assessment(evidence_ids, assessment_id):
    """
    After an assessment is submitted, link all evidence uploaded
    during that session to the newly created assessment ID.
    """
    if not evidence_ids:
        return
    conn = get_connection()
    c = conn.cursor()
    placeholders = ",".join("?" * len(evidence_ids))
    c.execute(
        f"UPDATE evidence SET assessment_id = ? WHERE id IN ({placeholders})",
        (assessment_id, *evidence_ids)
    )
    conn.commit()
    conn.close()

# ══════════════════════════════════════════════════════════════
# SCANNER REPORT IMPORT — CyberMAP 2.0
# ══════════════════════════════════════════════════════════════

import glob

INCOMING_SCANS_FOLDER = os.path.join(
    os.path.dirname(__file__), "..", "incoming_scans"
)


def get_nist_ref_to_question_map(questions):
    """Build a lookup: nist_ref -> question dict, for fast matching."""
    mapping = {}
    for q in questions:
        ref = q.get("nist_ref")
        if ref:
            mapping[ref] = q
    return mapping


def import_single_scan_report(json_path, questions, uploaded_by="Scanner"):
    """
    Reads one scanner JSON report, matches each result to a question
    by nist_ref, and returns:
      - endpoint_name
      - list of matched answers: [{question_id, score, check, status}, ...]
      - the raw report dict (for saving as evidence)
    """
    with open(json_path, "r", encoding="utf-8") as f:
        report = json.load(f)

    endpoint_name = report["scan_metadata"].get("hostname", "Unknown")
    nist_map = get_nist_ref_to_question_map(questions)

    status_to_score = {"PASS": 5, "PARTIAL": 2, "FAIL": 0, "ERROR": 0}

    matched_answers = []
    for result in report["results"]:
        ref = result.get("nist_ref")
        matched_question = nist_map.get(ref)
        if matched_question:
            matched_answers.append({
                "question_id": str(matched_question["id"]),
                "question_text": matched_question["question"],
                "score": status_to_score.get(result["status"], 0),
                "check": result["check"],
                "status": result["status"],
            })

    return {
        "endpoint_name": endpoint_name,
        "json_path": json_path,
        "matched_answers": matched_answers,
        "summary": report.get("summary", {}),
        "raw_report": report,
    }


def bulk_import_scan_reports(questions, folder=None):
    """
    Scans a folder for all CyberMAP_ScanReport_*.json files and
    imports every one of them.
    Returns a list of import results, one per file/endpoint.
    """
    if folder is None:
        folder = INCOMING_SCANS_FOLDER

    os.makedirs(folder, exist_ok=True)
    pattern = os.path.join(folder, "CyberMAP_ScanReport_*.json")
    json_files = glob.glob(pattern)

    results = []
    for path in sorted(json_files):
        try:
            result = import_single_scan_report(path, questions)
            results.append(result)
        except Exception as e:
            results.append({
                "endpoint_name": os.path.basename(path),
                "json_path": path,
                "error": str(e),
            })

    return results


def save_scan_report_as_evidence(import_result, assessment_id, uploaded_by="Scanner"):
    """
    For one imported scan report, save it as evidence (hashed +
    chained) against EVERY question it matched, tagging source
    as 'Scanner' instead of 'Manual'.
    """
    json_path = import_result["json_path"]
    with open(json_path, "rb") as f:
        file_bytes = f.read()

    evidence_ids = []
    for match in import_result["matched_answers"]:
        evidence_id, file_hash, chain_hash = save_evidence(
            assessment_id = assessment_id,
            question_id   = match["question_id"],
            filename      = os.path.basename(json_path),
            file_path     = json_path,
            file_type     = "application/json",
            file_bytes    = file_bytes,
            uploaded_by   = uploaded_by,
            source        = "Scanner",
        )
        evidence_ids.append(evidence_id)

    return evidence_ids

# ══════════════════════════════════════════════════════════════
# CONTINUOUS MONITORING — CyberMAP 2.0
# ══════════════════════════════════════════════════════════════

def save_monitoring_snapshot(endpoint_name, scan_report):
    """
    Save a scanner report as a monitoring snapshot, timestamped,
    so future scans can be compared against it.
    """
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        """INSERT INTO monitoring_snapshots
           (endpoint_name, scan_time, report_json)
           VALUES (?, ?, ?)""",
        (endpoint_name, scan_report["scan_metadata"]["scan_time"], json.dumps(scan_report))
    )
    conn.commit()
    snapshot_id = c.lastrowid
    conn.close()
    return snapshot_id

def get_latest_snapshot(endpoint_name):
    """Get the most recent stored snapshot for a given endpoint."""
    conn = get_connection()
    row = conn.execute(
        """SELECT * FROM monitoring_snapshots
           WHERE endpoint_name = ?
           ORDER BY id DESC LIMIT 1""",
        (endpoint_name,)
    ).fetchone()
    conn.close()
    if row:
        d = dict(row)
        d["report"] = json.loads(d["report_json"])
        return d
    return None


def get_all_snapshots(endpoint_name=None):
    """Get all monitoring snapshots, optionally filtered by endpoint."""
    conn = get_connection()
    if endpoint_name:
        rows = conn.execute(
            """SELECT * FROM monitoring_snapshots
               WHERE endpoint_name = ?
               ORDER BY id ASC""",
            (endpoint_name,)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM monitoring_snapshots ORDER BY id ASC"
        ).fetchall()
    conn.close()
    results = []
    for row in rows:
        d = dict(row)
        d["report"] = json.loads(d["report_json"])
        results.append(d)
    return results


def detect_drift(endpoint_name, new_report):
    """
    Compare a new scan report against the latest stored snapshot
    for the same endpoint. Returns a list of drift events — checks
    whose status changed between the two scans.

    Returns:
    [
        {
            "check": "Firewall Status",
            "previous_status": "PASS",
            "current_status": "FAIL",
            "previous_time": "...",
            "current_time": "...",
        },
        ...
    ]
    If there's no previous snapshot, returns an empty list
    (nothing to compare against yet — this becomes the baseline).
    """
    previous = get_latest_snapshot(endpoint_name)

    if previous is None:
        return []  # first scan for this endpoint — becomes baseline

    prev_results = {r["check"]: r["status"] for r in previous["report"]["results"]}
    new_results  = {r["check"]: r["status"] for r in new_report["results"]}

    drift_events = []
    for check_name, new_status in new_results.items():
        prev_status = prev_results.get(check_name)
        if prev_status and prev_status != new_status:
            drift_events.append({
                "check": check_name,
                "previous_status": prev_status,
                "current_status": new_status,
                "previous_time": previous["scan_time"],
                "current_time": new_report["scan_metadata"]["scan_time"],
            })

    return drift_events
# =====================================================================
# CVE CACHE - CyberMAP 2.0
# =====================================================================

def get_cached_cve_result(nist_ref, max_age_hours=24):
    """
    Returns a cached CVE result for this NIST ref if one exists and
    is younger than max_age_hours. Returns None if no cache exists
    or the cache has expired (caller should then do a live lookup
    and call save_cve_cache() to refresh it).
    """
    import json
    from datetime import datetime

    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM cve_cache WHERE nist_ref = ?",
        (nist_ref,)
    ).fetchone()
    conn.close()

    if not row:
        return None

    cached_at = datetime.strptime(row["cached_at"][:19], "%Y-%m-%d %H:%M:%S")
    age_hours = (datetime.now() - cached_at).total_seconds() / 3600

    if age_hours > max_age_hours:
        return None  # expired

    return {
        "source": "cache-db",
        "keyword_used": row["keyword_used"],
        "cves": json.loads(row["cves_json"]),
        "error": None,
        "cached_at": row["cached_at"],
        "age_hours": round(age_hours, 1),
    }


def save_cve_cache(nist_ref, keyword_used, source, cves):
    """
    Saves (or overwrites) the CVE lookup result for a NIST ref, with
    a fresh timestamp. Only live or cached-fallback results should be
    saved here - not error/none results, so a temporary API failure
    doesn't get permanently cached.
    """
    import json
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        """INSERT INTO cve_cache (nist_ref, keyword_used, source, cves_json, cached_at)
           VALUES (?, ?, ?, ?, datetime('now'))
           ON CONFLICT(nist_ref) DO UPDATE SET
             keyword_used = excluded.keyword_used,
             source = excluded.source,
             cves_json = excluded.cves_json,
             cached_at = excluded.cached_at""",
        (nist_ref, keyword_used, source, json.dumps(cves))
    )
    conn.commit()
    conn.close()
