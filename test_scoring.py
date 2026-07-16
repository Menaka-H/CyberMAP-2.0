# test_scoring.py
from utils.scoring import (compute_domain_scores, compute_overall_score,
                           get_maturity_label, identify_gaps, build_feature_vector)
from utils.database import get_questions

# Simulate answers — everyone scores 2 out of 5
questions = get_questions()
answers = {str(q['id']): 2 for q in questions}

# Run the scoring engine
domain_scores = compute_domain_scores(answers, questions)
overall       = compute_overall_score(domain_scores)
label, emoji, color = get_maturity_label(overall)
gaps          = identify_gaps(answers, questions, threshold=3)
feature_vec   = build_feature_vector(domain_scores)

print("Domain Scores:")
for d, v in domain_scores.items():
    print(f"  {d}: {v['score']}/5.00")
print(f"Overall Score : {overall}")
print(f"Maturity Level: {emoji} {label}")
print(f"Gaps Found    : {len(gaps)}")
print(f"Feature Vector: {feature_vec}")