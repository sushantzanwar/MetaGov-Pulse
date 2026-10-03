"""
==============================================================================
GOVERNANCE INTELLIGENCE PLATFORM (Flask Full-Stack App)
Maintainer: Person 3 (Backend) & Person 6 (Integration)
==============================================================================
"""

import os
from flask import Flask, jsonify, render_template, request
from database.db import close_db, init_db, seed_db, DEFAULT_DB_PATH
from routes.schemes import schemes_bp
from routes.analytics import analytics_bp
from routes.dashboard import dashboard_bp


def create_app(test_config=None):
    """Application factory pattern for testability and clean architecture."""
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-only-change-me'),
        DATABASE=os.environ.get('DATABASE_PATH', DEFAULT_DB_PATH),
        JSON_SORT_KEYS=False
    )

    if test_config is not None:
        app.config.update(test_config)

    # Register database teardown
    app.teardown_appcontext(close_db)

    # Register API & Page Blueprints
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(schemes_bp)
    app.register_blueprint(analytics_bp)

    # Initialize and seed database if not already present
    with app.app_context():
        try:
            init_db()
            seed_db()
        except Exception as e:
            app.logger.error(f"Error during database initialization: {e}")

    # --------------------------------------------------------------------------
    # HEALTH CHECK ENDPOINT
    # --------------------------------------------------------------------------
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            "status": "healthy",
            "platform": "Government Schemes Governance Intelligence Platform",
            "database": "SQLite (Normalized)",
            "schemes_source": "data/government_schemes_120.csv",
            "mode": "100% offline-ready"
        }), 200

    @app.route('/favicon.ico')
    def favicon():
        svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect width="100" height="100" rx="20" fill="#1e3a8a"/><text x="50%" y="55%" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-weight="bold" font-size="60" fill="white">G</text></svg>'
        return app.response_class(svg, mimetype='image/svg+xml')

    # --------------------------------------------------------------------------
    # ERROR HANDLERS (JSON for API, HTML for browser)
    # --------------------------------------------------------------------------
    @app.errorhandler(400)
    def bad_request(error):
        if request.path.startswith('/api/') or request.is_json:
            return jsonify({
                "success": False,
                "error": "Bad Request",
                "details": str(error)
            }), 400
        return render_template('404.html', error_title="400 - Bad Request", error_message=str(error)), 400

    @app.errorhandler(404)
    def not_found(error):
        if request.path.startswith('/api/') or request.is_json:
            return jsonify({
                "success": False,
                "error": "Resource Not Found",
                "path": request.path
            }), 404
        return render_template('404.html', error_title="404 - Resource Not Found", error_message="The requested scheme or page does not exist."), 404

    @app.errorhandler(500)
    def internal_error(error):
        if request.path.startswith('/api/') or request.is_json:
            return jsonify({
                "success": False,
                "error": "Internal Server Error",
                "details": "An unexpected server error occurred."
            }), 500
        return render_template('404.html', error_title="500 - Server Error", error_message="An internal server error occurred."), 500

    return app


app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("\n" + "=" * 65)
    print(f"[*] Governance Intelligence Platform running on http://127.0.0.1:{port}")
    print(f"[*] Command Center & Explorer: http://127.0.0.1:{port}")
    print(f"[*] API Health Check: http://127.0.0.1:{port}/api/health")
    print(f"[*] Offline Mode: Active (No external CDN/AI dependencies)")
    print("=" * 65 + "\n")
    host = os.environ.get('HOST', '127.0.0.1')
    debug = os.environ.get('FLASK_DEBUG') == '1'
    app.run(host=host, port=port, debug=debug)
