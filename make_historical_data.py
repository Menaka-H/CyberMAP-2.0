from utils.database import save_assessment
from utils.questions_data import DOMAINS
import random
import sqlite3, os, json
from datetime import datetime, timedelta

DB_PATH = os.path.join("data", "cybermap.db")

def make_fake_assessment(org_name, assessor, target_avg, days_ago):
    domain_scores = {}
    scores = {}
    for d in DOMAINS:
        s = round(random.uniform(target_avg - 0.3, target_avg + 0.3), 2)
        s = max(0, min(5, s))
        scores[d] = s

    overall = round(sum(scores.values()) / len(scores), 2)

    aid = save_assessment(
        org_name=org_name,
        assessor=assessor,
        answers={},
        scores=scores,
        maturity_score=overall,
        risk_level="Medium",
        gaps=[],
    )

    fake_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "UPDATE assessments SET created_at = ? WHERE id = ?",
        (fake_date, aid)
    )
    conn.commit()
    conn.close()
    print(f"Created assessment ID {aid}: {org_name} - avg {overall} - dated {fake_date}")

make_fake_assessment("Acme Corp", "Menaka H", 1.8, days_ago=90)
make_fake_assessment("Acme Corp", "Menaka H", 2.3, days_ago=60)
make_fake_assessment("Acme Corp", "Menaka H", 2.7, days_ago=30)
make_fake_assessment("Acme Corp", "Menaka H", 3.1, days_ago=5)
