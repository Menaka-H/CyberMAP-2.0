# test_ml.py
from utils.ml_model import train_model, predict_risk, get_risk_emoji

# Step 1: Train the model
print("=== Training ML Model ===")
train_model(force=True)

# Step 2: Test with different score profiles
print("\n=== Risk Predictions ===")

test_profiles = [
    ([1.0, 0.5, 0.8, 1.0, 0.5, 0.8], "Should be Critical"),
    ([2.0, 2.0, 2.0, 2.0, 2.0, 2.0], "Should be High"),
    ([3.0, 3.5, 3.0, 3.2, 3.0, 3.5], "Should be Medium"),
    ([4.5, 4.0, 4.5, 4.0, 4.5, 4.0], "Should be Low"),
]

for scores, expected in test_profiles:
    result = predict_risk(scores)
    emoji  = get_risk_emoji(result["risk_level"])
    print(f"{expected}")
    print(f"  Scores   : {scores}")
    print(f"  Predicted: {emoji} {result['risk_level']} ({result['confidence']}% confidence)")
    print()