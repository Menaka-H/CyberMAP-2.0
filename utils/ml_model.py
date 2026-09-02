# utils/ml_model.py
# Trains and uses an AI/ML model to classify cybersecurity risk level
# Risk levels: Critical | High | Medium | Low

import os
import pickle
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score

import shap

from utils.questions_data import DOMAINS

# Where to save the trained model files
MODEL_PATH  = os.path.join(os.path.dirname(__file__), "..", "models", "risk_classifier.pkl")
SCALER_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "scaler.pkl")

# Risk level display helpers
RISK_COLORS = {
    "Critical": "#7f1d1d",
    "High":     "#dc2626",
    "Medium":   "#f59e0b",
    "Low":      "#16a34a",
}
RISK_EMOJIS = {
    "Critical": "🚨",
    "High":     "🔴",
    "Medium":   "🟡",
    "Low":      "🟢",
}

# Cached SHAP explainer + background data (built once, reused after)
_shap_explainer = None
_shap_background = None


def _generate_training_data(n=1200):
    """
    Create synthetic training data to teach the ML model.

    Since we don't have real assessment data yet, we generate
    1200 fake organization profiles with known risk levels.

    Each profile = 6 domain scores (one per NIST domain)
    Label = risk level based on average score

    Score ranges → Risk level:
        0.0 – 1.4  → Critical
        1.5 – 2.4  → High
        2.5 – 3.7  → Medium
        3.8 – 5.0  → Low
    """
    rng = np.random.default_rng(42)  # fixed seed = same data every run
    X, y = [], []

    def label_from_avg(avg):
        if avg < 1.5:   return "Critical"
        if avg < 2.5:   return "High"
        if avg < 3.75:  return "Medium"
        return "Low"

    # --- 300 Critical risk profiles (very low scores) ---
    for _ in range(300):
        scores = rng.uniform(0, 2, size=6)
        # Make Protect and Detect especially weak
        scores[2] = rng.uniform(0, 1.5)   # Protect
        scores[3] = rng.uniform(0, 1.5)   # Detect
        X.append(scores.tolist())
        y.append(label_from_avg(scores.mean()))

    # --- 300 High risk profiles ---
    for _ in range(300):
        scores = rng.uniform(1.5, 3.0, size=6)
        X.append(scores.tolist())
        y.append(label_from_avg(scores.mean()))

    # --- 300 Medium risk profiles ---
    for _ in range(300):
        scores = rng.uniform(2.5, 4.0, size=6)
        X.append(scores.tolist())
        y.append(label_from_avg(scores.mean()))

    # --- 300 Low risk profiles (high scores) ---
    for _ in range(300):
        scores = rng.uniform(3.5, 5.0, size=6)
        X.append(scores.tolist())
        y.append(label_from_avg(scores.mean()))

    return np.array(X), np.array(y)


def train_model(force=False):
    """
    Train the ML model and save it to the models/ folder.

    force=False → only train if model doesn't exist yet
    force=True  → always retrain from scratch
    """
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)

    # If model already exists and we're not forcing, just load it
    if os.path.exists(MODEL_PATH) and not force:
        print("Model already exists. Loading from file...")
        return load_model()

    print("Training ML model...")

    # Step 1: Generate training data
    X, y = _generate_training_data()

    # Step 2: Scale the features (important for ML models)
    # StandardScaler converts scores so they have mean=0, std=1
    scaler  = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Step 3: Create and train the model
    clf = GradientBoostingClassifier(
        n_estimators=150,    # number of decision trees
        max_depth=4,         # how deep each tree goes
        learning_rate=0.1,   # how fast it learns
        random_state=42      # fixed seed for reproducibility
    )
    clf.fit(X_scaled, y)

    # Step 4: Check accuracy using cross-validation
    cv_scores = cross_val_score(clf, X_scaled, y, cv=5, scoring="accuracy")
    print(f"Model accuracy: {cv_scores.mean():.1%} (+/- {cv_scores.std():.1%})")

    # Step 5: Save the model and scaler to disk
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(clf, f)
    with open(SCALER_PATH, "wb") as f:
        pickle.dump(scaler, f)

    print("Model saved successfully!")
    return clf, scaler


def load_model():
    """Load the saved model from disk."""
    if not os.path.exists(MODEL_PATH):
        print("No saved model found. Training now...")
        return train_model(force=True)

    with open(MODEL_PATH, "rb") as f:
        clf = pickle.load(f)
    with open(SCALER_PATH, "rb") as f:
        scaler = pickle.load(f)

    return clf, scaler


def predict_risk(feature_vector):
    """
    Predict the risk level from 6 domain scores.

    feature_vector = [govern, identify, protect, detect, respond, recover]
    Example input:  [2.0, 3.1, 1.8, 2.5, 3.0, 2.2]

    Returns a dict like:
    {
        "risk_level":    "High",
        "confidence":    87.5,
        "probabilities": {"Critical": 5.0, "High": 87.5, "Medium": 7.5, "Low": 0.0}
    }
    """
    clf, scaler = load_model()

    # Prepare input
    X = np.array(feature_vector).reshape(1, -1)
    X_scaled = scaler.transform(X)

    # Make prediction
    prediction   = clf.predict(X_scaled)[0]
    probabilities = clf.predict_proba(X_scaled)[0]
    classes      = clf.classes_

    # Build probability dict
    prob_dict  = {
        c: round(float(p) * 100, 1)
        for c, p in zip(classes, probabilities)
    }
    confidence = round(float(probabilities.max()) * 100, 1)

    return {
        "risk_level":    prediction,
        "confidence":    confidence,
        "probabilities": prob_dict,
    }


def get_risk_color(risk_level):
    """Return the hex color for a risk level."""
    return RISK_COLORS.get(risk_level, "#6b7280")


def get_risk_emoji(risk_level):
    """Return the emoji for a risk level."""
    return RISK_EMOJIS.get(risk_level, "⚪")


# ══════════════════════════════════════════════════════════════
# EXPLAINABLE ML — CyberMAP 2.0 (SHAP)
# ══════════════════════════════════════════════════════════════

def _get_shap_explainer():
    """
    Build (once) and cache a SHAP explainer for the trained model.

    NOTE: GradientBoostingClassifier with more than 2 classes is not
    supported by shap.TreeExplainer in this SHAP version. Instead we
    use the model-agnostic shap.Explainer wrapped around predict_proba,
    which works correctly for any multiclass model. A small background
    sample (drawn from the same synthetic training distribution) is
    required as a reference point for the explainer.
    """
    global _shap_explainer, _shap_background

    if _shap_explainer is not None:
        return _shap_explainer

    clf, scaler = load_model()

    # Build a small background reference set from the training
    # distribution (deterministic, same seed as training data)
    X_train, _ = _generate_training_data()
    X_train_scaled = scaler.transform(X_train)

    rng = np.random.default_rng(42)
    idx = rng.choice(len(X_train_scaled), size=60, replace=False)
    background = X_train_scaled[idx]

    _shap_background = background
    _shap_explainer = shap.Explainer(
        clf.predict_proba, background, algorithm="permutation"
    )
    return _shap_explainer


def explain_prediction(feature_vector):
    """
    Explain WHY the model predicted a given risk level, using SHAP.

    feature_vector = [govern, identify, protect, detect, respond, recover]

    Returns a dict like:
    {
        "predicted_class": "High",
        "domain_contributions": {
            "Govern":   0.05,   # positive = pulled toward this class
            "Identify": 0.03,
            "Protect":  0.18,
            "Detect":  -0.42,   # negative = pulled away from this class
            "Respond": -0.35,
            "Recover": -0.02,
        },
        "top_positive": ["Protect"],   # domains supporting the prediction
        "top_negative": ["Detect", "Respond"],  # domains opposing it
        "explanation_text": "Classified as High Risk primarily because
                              Detect (1.20/5.00) and Respond (1.90/5.00)
                              are pulling the prediction toward higher risk.
                              Protect (4.10/5.00) is the strongest domain
                              but is outweighed by the other weaknesses."
    }
    """
    clf, scaler = load_model()

    X = np.array(feature_vector).reshape(1, -1)
    X_scaled = scaler.transform(X)

    prediction = clf.predict(X_scaled)[0]
    class_index = list(clf.classes_).index(prediction)

    explainer = _get_shap_explainer()
    shap_result = explainer(X_scaled, max_evals=500)

    # shap_result.values shape: (1, n_features, n_classes)
    values = shap_result.values
    if values.ndim == 3:
        contributions = values[0, :, class_index]
    else:
        # fallback for older/newer shap output shapes
        contributions = np.ravel(values)[:len(DOMAINS)]

    domain_contributions = {
        domain: round(float(val), 3)
        for domain, val in zip(DOMAINS, contributions)
    }

    # Sort domains by contribution
    sorted_domains = sorted(
        domain_contributions.items(), key=lambda x: x[1]
    )
    top_negative = [d for d, v in sorted_domains if v < 0][:2]   # pulling toward risk
    top_positive = [d for d, v in reversed(sorted_domains) if v > 0][:2]  # pulling away

    # Build a human-readable explanation
    domain_scores = dict(zip(DOMAINS, feature_vector))

    if top_negative:
        neg_text = " and ".join(
            f"{d} ({domain_scores[d]:.2f}/5.00)" for d in top_negative
        )
        verb = "is" if len(top_negative) == 1 else "are"
        explanation = f"Classified as {prediction} Risk primarily because {neg_text} "
        explanation += f"{verb} pulling the prediction toward higher risk."
        if top_positive:
            pos_text = " and ".join(
                f"{d} ({domain_scores[d]:.2f}/5.00)" for d in top_positive
            )
            was_were = "was" if len(top_positive) == 1 else "were"
            explanation += (
                f" {pos_text} scored better but {was_were} outweighed by these "
                f"weaknesses."
            )
    else:
        explanation = (
            f"Classified as {prediction} Risk based on a balanced "
            f"profile across all six domains, with no single domain "
            f"driving the classification."
        )

    return {
        "predicted_class": prediction,
        "domain_contributions": domain_contributions,
        "top_positive": top_positive,
        "top_negative": top_negative,
        "explanation_text": explanation,
    }