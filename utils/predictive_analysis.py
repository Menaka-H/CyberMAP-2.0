# utils/predictive_analysis.py - CyberMAP 2.0 Predictive Maturity Analysis
#
# Uses simple linear regression on an organisation's historical
# assessment scores to project future maturity if the current
# improvement rate continues. This is intentionally a simple,
# transparent model (not a black box) - a straight-line fit is
# appropriate given the small number of data points typically
# available (a handful of assessments per organisation), and its
# assumptions are stated explicitly rather than hidden.

import numpy as np
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression


def get_score_history(org_name, all_assessments):
    """
    Filters assessments for one organisation, sorted oldest to
    newest, returning (dates, scores) as parallel lists.
    """
    org_assessments = [
        a for a in all_assessments if a["org_name"] == org_name
    ]
    org_assessments.sort(key=lambda a: a["created_at"])

    dates = [a["created_at"] for a in org_assessments]
    scores = [a["maturity_score"] for a in org_assessments]
    return dates, scores


def predict_future_maturity(dates, scores, months_ahead=(1, 3, 6)):
    """
    Fits a simple linear regression of score vs. time (in days since
    the first assessment) and projects the score forward by the
    requested number of months.

    Requires at least 2 data points. With only 2, the "trend" is a
    straight line between them - inherently low-confidence, which is
    reflected in the returned confidence label. 3+ points allow the
    regression to average out noise between assessments.

    Returns:
    {
        "has_enough_data": bool,
        "current_score": float,
        "trend_direction": "Improving" | "Declining" | "Stable",
        "rate_per_month": float,
        "projections": {1: float, 3: float, 6: float},
        "confidence": "Low" | "Medium" | "Higher",
        "r_squared": float,
    }
    """
    if len(scores) < 2:
        return {"has_enough_data": False}

    # Convert dates to "days since first assessment"
    parsed_dates = []
    for d in dates:
        try:
            parsed_dates.append(datetime.strptime(d[:19], "%Y-%m-%d %H:%M:%S"))
        except Exception:
            parsed_dates.append(datetime.strptime(d[:10], "%Y-%m-%d"))

    first_date = parsed_dates[0]
    days_since_start = np.array([
        (d - first_date).days for d in parsed_dates
    ]).reshape(-1, 1)
    y = np.array(scores)

    model = LinearRegression()
    model.fit(days_since_start, y)

    r_squared = model.score(days_since_start, y) if len(scores) > 2 else None

    # Rate of change per day, converted to per month (30 days)
    rate_per_day = model.coef_[0]
    rate_per_month = round(rate_per_day * 30, 3)

    if rate_per_month > 0.05:
        direction = "Improving"
    elif rate_per_month < -0.05:
        direction = "Declining"
    else:
        direction = "Stable"

    last_day_offset = days_since_start[-1][0]
    projections = {}
    for months in months_ahead:
        future_day = last_day_offset + (months * 30)
        predicted = model.predict([[future_day]])[0]
        # Clamp to valid maturity score range
        predicted = max(0.0, min(5.0, predicted))
        projections[months] = round(float(predicted), 2)

    if len(scores) == 2:
        confidence = "Low"
    elif len(scores) == 3:
        confidence = "Medium"
    else:
        confidence = "Higher"

    return {
        "has_enough_data": True,
        "current_score": round(scores[-1], 2),
        "trend_direction": direction,
        "rate_per_month": rate_per_month,
        "projections": projections,
        "confidence": confidence,
        "r_squared": round(r_squared, 3) if r_squared is not None else None,
        "data_points_used": len(scores),
    }
