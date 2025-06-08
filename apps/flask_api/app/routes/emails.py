from flask import Blueprint, jsonify, request
from app.services.db import get_emails, get_email_by_id, store_email_status

print("=== emails.py loaded ===")

emails_bp = Blueprint("emails", __name__)

@emails_bp.route("/users/<username>/folders/<folder>/emails")
def list_emails(username, folder):
    emails = get_emails(username, folder)
    return jsonify([dict(row) for row in emails])

@emails_bp.route("/email/<int:email_id>")
def get_email(email_id):
    email = get_email_by_id(email_id)
    return jsonify(dict(email)) if email else (jsonify({"error": "Not found"}), 404)

@emails_bp.route("/emails/<int:email_id>/status", methods=["POST", "OPTIONS"])
def update_email_status(email_id):
    if request.method == "OPTIONS":
        return '', 200

    status_update = request.json
    print(f"Received status update for email {email_id}:", status_update)

    success = store_email_status(email_id, status_update)
    if success:
        return jsonify({"message": "Email status updated successfully"}), 200
    return jsonify({"message": "Failed to update email status"}), 400