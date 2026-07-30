"""Create and configure the Flask web application."""

import hmac
import secrets
from flask import Flask, abort, request, session
from config.logging_config import configure_logging
from config.settings import get_settings
from orchestration.graph_builder import build_graph


def create_app(testing: bool = False) -> Flask:
    """Build the application, register routes, and enable shared safeguards."""
    configure_logging()
    settings = get_settings()
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.update(SECRET_KEY=settings.secret_key, TESTING=testing)
    app.extensions["buildsense_graph"] = build_graph()

    @app.context_processor
    def csrf_context():
        """Expose one session-backed CSRF token to all HTML templates."""
        token = session.get("_csrf_token")
        if not token:
            token = secrets.token_urlsafe(32)
            session["_csrf_token"] = token
        return {"csrf_token": token}

    @app.before_request
    def protect_html_forms():
        """Reject browser form posts that do not include the session token."""
        if request.method == "POST" and not request.path.startswith("/api/"):
            expected = session.get("_csrf_token", "")
            supplied = request.form.get("_csrf_token", "")
            if not expected or not hmac.compare_digest(expected, supplied):
                abort(400, description="Invalid or missing CSRF token")

    from app.routes.dashboard_routes import dashboard_bp
    from app.routes.approval_routes import approval_bp
    from app.routes.api_routes import api_bp
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(approval_bp, url_prefix="/approval")
    app.register_blueprint(api_bp, url_prefix="/api")
    return app
