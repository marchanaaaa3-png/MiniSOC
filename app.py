from flask import Flask, redirect, request, session, url_for

from config import Config
from database.db import init_db

from routes.dashboard import dashboard_bp
from routes.events import events_bp
from routes.alerts import alerts_bp
from routes.logs import logs_bp
from routes.detector_rules import detector_rules_bp
from routes.threat_intelligence import threat_intelligence_bp
from routes.reports import reports_bp
from routes.settings import settings_bp
from routes.simulator import simulator_bp
from routes.auth import auth_bp


def create_app():

    app = Flask(__name__)

    # --------------------------------------------------------
    # Configuration
    # --------------------------------------------------------

    app.config.from_object(Config)

    # --------------------------------------------------------
    # Database
    # --------------------------------------------------------

    init_db(app)

    # --------------------------------------------------------
    # Authentication
    # --------------------------------------------------------

    app.register_blueprint(auth_bp)

    # --------------------------------------------------------
    # Application routes
    # --------------------------------------------------------

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(alerts_bp)
    app.register_blueprint(logs_bp)
    app.register_blueprint(detector_rules_bp)
    app.register_blueprint(threat_intelligence_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(simulator_bp)

    # --------------------------------------------------------
    # Protect the entire MiniSOC application
    # --------------------------------------------------------

    @app.before_request
    def require_login():

        # These endpoints must remain public
        public_endpoints = {
            "auth.login",
            "auth.logout",
            "static",
            "health",
            "favicon"
        }

        if request.endpoint in public_endpoints:
            return None

        # If user is not logged in,
        # send them to the login page.
        if not session.get("user_id"):

            return redirect(
                url_for("auth.login")
            )

        return None

    # --------------------------------------------------------
    # Health check
    # --------------------------------------------------------

    @app.route("/health")
    def health():

        return {
            "status": "ok",
            "service": "MiniSOC"
        }

    # --------------------------------------------------------
    # Favicon
    # --------------------------------------------------------

    @app.route("/favicon.ico")
    def favicon():

        return "", 204

    return app


app = create_app()


if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )