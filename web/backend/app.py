"""Flask application factory for Dynasty FIRE web app"""

import os
from pathlib import Path

from flask import Flask, send_from_directory
from flask_cors import CORS

from .api.routes import api_bp


def create_app(config_name: str = None) -> Flask:
    """Create and configure Flask application

    Args:
        config_name: 'development' or 'production'

    Returns:
        Configured Flask app
    """
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")

    # Static folder for production (React build)
    static_folder = Path(__file__).parent.parent / "frontend" / "dist"

    app = Flask(
        __name__,
        static_folder=str(static_folder) if static_folder.exists() else None,
        static_url_path="/",
    )

    # CORS for development (React dev server on :5173)
    if config_name == "development":
        CORS(app, origins=["http://localhost:5173", "http://127.0.0.1:5173"])

    # Register API blueprint
    app.register_blueprint(api_bp, url_prefix="/api/v1")

    # Serve React app for non-API routes (production)
    if static_folder.exists():

        @app.route("/", defaults={"path": ""})
        @app.route("/<path:path>")
        def serve_react(path):
            if path.startswith("api/"):
                return {"error": "Not found"}, 404
            if path and (static_folder / path).exists():
                return send_from_directory(static_folder, path)
            return send_from_directory(static_folder, "index.html")

    return app


# For running directly with `python -m web.backend.app`
app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5001)
