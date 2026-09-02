from utils.database import get_all_assessments
from utils.predictive_analysis import get_score_history, predict_future_maturity

all_assessments = get_all_assessments()
dates, scores = get_score_history("Acme Corp", all_assessments)

print("Dates:", dates)
print("Scores:", scores)
print()

result = predict_future_maturity(dates, scores)
print("Has enough data:", result["has_enough_data"])
print("Current score:", result["current_score"])
print("Trend direction:", result["trend_direction"])
print("Rate per month:", result["rate_per_month"])
print("Projections:", result["projections"])
print("Confidence:", result["confidence"])
print("R-squared:", result["r_squared"])
