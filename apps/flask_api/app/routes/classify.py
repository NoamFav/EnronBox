from flask import Blueprint, request, jsonify
from app.services.enron_classifier import EnronEmailClassifier

classify_bp = Blueprint("classify", __name__)
