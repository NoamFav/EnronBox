from flask import Blueprint, jsonify
from app.services.db import get_all_users, get_folders_for_user

users_bp = Blueprint("users", __name__)


@users_bp.route("/users")
def list_users():
    users = get_all_users()
    return jsonify([dict(row) for row in users])


@users_bp.route("/users/<username>/folders")
def list_folders(username):
    folders = get_folders_for_user(username)
    return jsonify([row["name"] for row in folders])
