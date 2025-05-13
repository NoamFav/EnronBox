from flask import Blueprint, request, jsonify
from app.services.enron_classifier import EnronEmailClassifier
from app.services.emotion_enhancer import EmotionEnhancer
from app.services.db import get_email_by_id, store_data
import pandas as pd
import traceback
import os, pickle
from pathlib import Path

classify_bp = Blueprint("classify", __name__)
classifier = EnronEmailClassifier()
emotion_enhancer = EmotionEnhancer()

# Initialize the classifier (you might want to call train() elsewhere)
# Can be initialized during app startup or the first time it's needed


@classify_bp.route("/email/<int:email_id>", methods=["GET"])
def classify_email(email_id):
    """Classify a single email by ID"""
    try:
        # Get the email from database
        email = get_email_by_id(email_id)

        if not email:
            return jsonify({"error": f"Email with id {email_id} not found"}), 404

        # Convert to a format the classifier expects
        email_data = {
            "subject": email.get("subject", ""),
            "body": email.get("body", ""),
            "sender": email.get("sender", ""),
            "has_attachment": email.get("has_attachment", False),
            "num_recipients": email.get("num_recipients", 1),
            "time_sent": pd.to_datetime(email.get("time_sent", "2000-01-01")),
        }

        # Predict using the classifier
        prediction = classifier.predict(email_data)

        # Store prediction result in database
        prediction_data = serialize_prediction(str(email_id), prediction)
        store_data("email_classifications", [prediction_data])

        return jsonify({"email_id": email_id, "classification": prediction})

    except Exception as e:
        return (
            jsonify(
                {
                    "error": f"Classification failed: {str(e)}",
                    "traceback": traceback.format_exc(),
                }
            ),
            500,
        )


@classify_bp.route("/batch", methods=["POST"])
def classify_batch():
    """Classify a batch of emails provided in the request"""
    try:
        data = request.get_json()

        if not data or not isinstance(data, list):
            return jsonify({"error": "Expected a list of email objects"}), 400

        results = []
        for email_data in data:
            # Ensure time_sent is in datetime format
            if "time_sent" in email_data:
                email_data["time_sent"] = pd.to_datetime(email_data["time_sent"])

            prediction = classifier.predict(email_data)

            # Prepare result
            result = {
                "email_id": email_data.get("id", "unknown"),
                "classification": prediction,
            }
            results.append(result)

            # TODO save the thing inside the DB
            # Store prediction if email_id is provided
            # if "id" in email_data:
            # prediction_data = serialize_prediction(
            #       str(email_data["id"]), prediction
            #  )
            # store_data("email_classifications", [prediction_data])

        return jsonify(results)

    except Exception as e:
        return (
            jsonify(
                {
                    "error": f"Batch classification failed: {str(e)}",
                    "traceback": traceback.format_exc(),
                }
            ),
            500,
        )


@classify_bp.route("/folder/<username>/<folder>", methods=["POST"])
def classify_folder(username, folder):
    """Classify all emails in a specific folder for a user"""
    from app.services.db import get_emails

    try:
        emails = get_emails(username, folder)

        if not emails:
            return (
                jsonify(
                    {
                        "message": f"No emails found in folder {folder} for user {username}"
                    }
                ),
                404,
            )

        results = []
        for email in emails:
            # Convert to format expected by classifier
            email_data = {
                "subject": email.get("subject", ""),
                "body": email.get("body", ""),
                "sender": email.get("sender", ""),
                "has_attachment": email.get("has_attachment", False),
                "num_recipients": email.get("num_recipients", 1),
                "time_sent": pd.to_datetime(email.get("time_sent", "2000-01-01")),
            }

            # Classify email
            prediction = classifier.predict(email_data)

            # Store result
            email_id = str(email.get("id", "unknown"))
            prediction_data = serialize_prediction(email_id, prediction)
            store_data("email_classifications", [prediction_data])

            # Add to results
            results.append(
                {
                    "email_id": email_id,
                    "subject": email.get("subject", ""),
                    "classification": prediction,
                }
            )

        return jsonify(
            {
                "username": username,
                "folder": folder,
                "classified_count": len(results),
                "results": results,
            }
        )

    except Exception as e:
        return (
            jsonify(
                {
                    "error": f"Folder classification failed: {str(e)}",
                    "traceback": traceback.format_exc(),
                }
            ),
            500,
        )


@classify_bp.route("/analyze/text", methods=["POST"])
def analyze_text():
    """Analyze text for emotional content using EmotionEnhancer"""
    try:
        data = request.get_json()

        if not data or "text" not in data:
            return jsonify({"error": "Expected JSON with 'text' field"}), 400

        text = data["text"]
        analysis = emotion_enhancer.enhance_emotion_analysis(text)
        dominant = get_dominant_tone(analysis)
        # return a new dict so we don't run into TypedDict __setitem__ issues
        return jsonify({**analysis, "dominant_tone": dominant})

    except Exception as e:
        return (
            jsonify(
                {
                    "error": f"Text analysis failed: {str(e)}",
                    "traceback": traceback.format_exc(),
                }
            ),
            500,
        )


@classify_bp.route("/train", methods=["POST"])
def train_classifier():
    """Train the classifier from the SQLite Enron DB at the given path"""
    try:
        data = request.get_json()
        if not data or "enron_dir" not in data:
            return (
                jsonify(
                    {"error": "Expected JSON with 'enron_dir' pointing to enron.db"}
                ),
                400,
            )

        # We’re really passing the .db file here
        enron_db = data["enron_dir"]
        max_emails = data.get("max_emails", 5000)

        # This will now call your SQLite loader
        email_df, labels = classifier.load_enron_emails(enron_db, max_emails=max_emails)
        classifier.train(email_df, labels)

        # Persist the pickled models
        model_dir = os.environ.get("MODEL_DIR", "/app/models")
        Path(model_dir).mkdir(parents=True, exist_ok=True)

        with open(Path(model_dir) / "text_model.pkl", "wb") as f:
            pickle.dump(classifier.text_model, f)
        with open(Path(model_dir) / "num_model.pkl", "wb") as f:
            pickle.dump(classifier.numerical_model, f)

        return jsonify(
            {
                "status": "success",
                "message": f"Classifier trained on {len(email_df)} emails",
                "categories": classifier.categories,
                "email_count": len(email_df),
            }
        )

    except Exception as e:
        return (
            jsonify(
                {
                    "error": f"Training failed: {str(e)}",
                    "traceback": traceback.format_exc(),
                }
            ),
            500,
        )


@classify_bp.route("/model/status", methods=["GET"])
def model_status():
    """Get the current status of the classifier model"""
    is_trained = (
        classifier.text_model is not None and classifier.numerical_model is not None
    )

    return jsonify(
        {
            "is_trained": is_trained,
            "categories": classifier.categories if is_trained else None,
        }
    )


def get_dominant_tone(analysis):
    """Determine the dominant tone based on analysis scores"""
    # Get the highest scoring tone
    tone_scores = {
        "casual": analysis.get("casual_score", 0),
        "formal": analysis.get("formal_score", 0),
        "sarcastic": analysis.get("sarcasm_score", 0),
    }

    # Default to the detected tone if available
    if "tone" in analysis and analysis["tone"] != "unknown":
        return analysis["tone"]

    # Otherwise find the highest score
    dominant_tone = max(tone_scores.items(), key=lambda x: x[1])[0]

    # If highest score is very low, check emotion scores
    if tone_scores[dominant_tone] < 30:
        if analysis.get("stress_score", 0) > 0.5:
            return "stressed"
        elif analysis.get("relaxation_score", 0) > 0.5:
            return "relaxed"
        elif analysis.get("polarity", 0) > 0.5:
            return "positive"
        elif analysis.get("polarity", 0) < -0.3:
            return "negative"
        else:
            return "neutral"

    return dominant_tone


def serialize_prediction(email_id: str, prediction):
    """
    Serialize model prediction results for storage.

    Args:
        email_id (str): The ID of the email.
        prediction (Dict[str, Any]): The prediction result from the model.

    Returns:
        Dict[str, Any]: A dictionary ready for storage in the database.
    """
    return {
        "email_id": email_id,
        "category": prediction["category"],
        "confidence": prediction["confidence"],
        "polarity": prediction["emotion"]["polarity"],
        "subjectivity": prediction["emotion"]["subjectivity"],
        "stress_score": prediction["emotion"]["stress_score"],
        "relaxation_score": prediction["emotion"]["relaxation_score"],
    }
