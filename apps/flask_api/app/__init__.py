from flask import Flask


def create_app():
    app = Flask(__name__)

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
