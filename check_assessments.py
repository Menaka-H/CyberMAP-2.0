from utils.database import get_all_assessments

assessments = get_all_assessments()
print("Total assessments:", len(assessments))
for a in assessments:
    print(" ID", a["id"], "-", a["org_name"], "-", a["maturity_score"], "-", a["created_at"])
