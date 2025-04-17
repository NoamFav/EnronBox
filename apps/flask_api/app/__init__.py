from flask import Flask


def create_app():
    app = Flask(__name__)

    from app.routes.summarize import summarize_bp
    from app.routes.ner import ner_bp
    from app.routes.classify import classify_bp
    from app.routes.respond import respond_bp

    app.register_blueprint(summarize_bp, url_prefix="/api/summarize")
    app.register_blueprint(ner_bp, url_prefix="/api/ner")
    app.register_blueprint(classify_bp, url_prefix="/api/classify")
    app.register_blueprint(respond_bp, url_prefix="/api/respond")

    return app
