from flask import Blueprint, jsonify
from app.services.db import get_emails, get_email_by_id

emails_bp = Blueprint("emails", __name__)


@emails_bp.route("/users/<username>/folders/<folder>/emails")
def list_emails(username, folder):
    emails = get_emails(username, folder)
    return jsonify([dict(row) for row in emails])


@emails_bp.route("/email/<int:email_id>")
def get_email(email_id):
    email = get_email_by_id(email_id)
    return jsonify(dict(email)) if email else (jsonify({"error": "Not found"}), 404)
