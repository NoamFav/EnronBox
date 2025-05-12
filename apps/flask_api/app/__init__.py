from flask import Flask
from flask_cors import CORS


def create_app():
    app = Flask(__name__)
    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": [
                    "http://localhost:1420",
                    "tauri://localhost",
                    "file://",
                    "null",
                    "*",
                ]
            }
        },
        supports_credentials=True,
        allow_headers=["Content-Type"],
        methods=["POST", "OPTIONS"],
    )

    from app.routes.summarize import summarize_bp
    from app.routes.ner import ner_bp
    from app.routes.classify import classify_bp
    from app.routes.respond import respond_bp
    from app.routes.users import users_bp
    from app.routes.emails import emails_bp

    app.register_blueprint(summarize_bp, url_prefix="/api/summarize")
    app.register_blueprint(ner_bp, url_prefix="/api/ner")
    app.register_blueprint(classify_bp, url_prefix="/api/classify")
    app.register_blueprint(respond_bp, url_prefix="/api/respond")
    app.register_blueprint(users_bp, url_prefix="/api")
    app.register_blueprint(emails_bp, url_prefix="/api")

    return app
