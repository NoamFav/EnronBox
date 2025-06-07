from flask import Blueprint, request, jsonify
from app.services.ner_engine import Extractor

ner_bp = Blueprint("ner", __name__)

@ner_bp.route("", methods=["POST"])
def extract_entities():
    """
    POST /api/ner
    Body (JSON):
    {
        "email_text": "<full email text>",
        "email_id":   "abc123"
    }

    Response (200):
    {
        "entities": {
            "names": ["John Doe"],
            "orgs":  ["ACME Corp"],
            "dates": ["8 June 2025"]
        }
    }
    """
    data = request.get_json()

    # ── validation ───────────────────────────────────────────────────────────
    if not data or "email_text" not in data:
        return jsonify({"error": "Missing required parameter: email_text"}), 400

    email_text = data["email_text"]
    email_id   = data.get("email_id")

    # ── run NER ──────────────────────────────────────────────────────────────
    extractor = Extractor()
    entities  = extractor.extract_entities(email_text)

    if email_id:
        try:
            extractor.save_entities_to_db(email_id, email_text)
        except Exception as exc:
            print(f"[NER] Could not store entities for email {email_id}: {exc}")

    return jsonify({"entities": entities})

