from flask import Blueprint, request, jsonify
from app.services.summarizer import EmailSummarizer

summarize_bp = Blueprint("summarize", __name__)
