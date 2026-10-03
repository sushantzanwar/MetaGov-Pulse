"""
==============================================================================
DASHBOARD & COMMAND CENTER REST API + PAGE ROUTES
Maintainer: Person 3 (Flask Backend Engineer)
==============================================================================
Provides Command Center dashboard statistics and HTML page routing.
==============================================================================
"""

from flask import Blueprint, jsonify, render_template
from services.analytics import get_dashboard_statistics

dashboard_bp = Blueprint('dashboard', __name__)


# ------------------------------------------------------------------------------
# JSON REST API ENDPOINT
# ------------------------------------------------------------------------------

@dashboard_bp.route('/api/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    """
    GET /api/dashboard/stats
    Aggregates real-time governance metrics from the 120 Government of India schemes.
    """
    try:
        stats = get_dashboard_statistics()
        return jsonify({
            "success": True,
            "data": stats
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Failed to calculate dashboard statistics.",
            "details": str(e)
        }), 500


# ------------------------------------------------------------------------------
# HTML PAGE ROUTES
# ------------------------------------------------------------------------------

@dashboard_bp.route('/', methods=['GET'])
@dashboard_bp.route('/dashboard', methods=['GET'])
def index():
    """Renders Command Center view."""
    return render_template('index.html', initial_view='command-center')


@dashboard_bp.route('/schemes', methods=['GET'])
def schemes_page():
    """Renders Government Schemes Explorer view."""
    return render_template('index.html', initial_view='schemes')


@dashboard_bp.route('/ministries', methods=['GET'])
def ministries_page():
    """Renders Ministries Intelligence view."""
    return render_template('index.html', initial_view='ministries')


@dashboard_bp.route('/categories', methods=['GET'])
def categories_page():
    """Renders Categories Intelligence view."""
    return render_template('index.html', initial_view='categories')


@dashboard_bp.route('/cross-ministry', methods=['GET'])
def cross_ministry_page():
    """Renders Cross-Ministry Intelligence view."""
    return render_template('index.html', initial_view='cross-ministry')


@dashboard_bp.route('/comparison', methods=['GET'])
def comparison_page():
    """Renders Scheme Comparison view."""
    return render_template('index.html', initial_view='comparison')


@dashboard_bp.route('/data-sources', methods=['GET'])
def data_sources_page():
    """Renders Data Sources view."""
    return render_template('index.html', initial_view='data-sources')
