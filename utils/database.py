# utils/database.py
# This file creates and manages the SQLite database
# It handles: creating tables, saving assessments, fetching results

import sqlite3    # built into Python - no install needed
import os
import json
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

    # Create all 3 tables
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