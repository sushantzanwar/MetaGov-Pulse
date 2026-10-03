"""
==============================================================================
ANALYTICS & GOVERNANCE INTELLIGENCE REST API BLUEPRINT
Maintainer: Person 3 (Flask Backend Engineer)
==============================================================================
Provides REST endpoints for ministry stats, category distribution,
scheme type classifications, and cross-ministry relationship networks.
==============================================================================
"""

from flask import Blueprint, jsonify
from services.analytics import (
    get_ministry_statistics,
    get_category_statistics,
    get_scheme_type_statistics,
    get_cross_ministry_relationships
)

analytics_bp = Blueprint('analytics_api', __name__, url_prefix='/api')


@analytics_bp.route('/ministries', methods=['GET'])
def list_ministries():
    """
    GET /api/ministries
    Lists all Government of India ministries with scheme counts and covered categories.
    """
    try:
        data = get_ministry_statistics()
        return jsonify({
            "success": True,
            "count": len(data),
            "data": data
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@analytics_bp.route('/ministries/<int:ministry_id>', methods=['GET'])
def ministry_detail(ministry_id):
    """
    GET /api/ministries/<id>
    Returns detailed schemes and category coverage for a specific ministry.
    """
    try:
        data = get_ministry_statistics(ministry_id=ministry_id)
        if not data:
            return jsonify({"success": False, "error": "Ministry not found."}), 404
        return jsonify({
            "success": True,
            "data": data
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@analytics_bp.route('/categories', methods=['GET'])
def list_categories():
    """
    GET /api/categories
    Lists all governance categories with scheme counts and participating ministries.
    """
    try:
        data = get_category_statistics()
        return jsonify({
            "success": True,
            "count": len(data),
            "data": data
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@analytics_bp.route('/categories/<int:category_id>', methods=['GET'])
def category_detail(category_id):
    """
    GET /api/categories/<id>
    Returns detailed schemes and ministries operating in a specific category.
    """
    try:
        data = get_category_statistics(category_id=category_id)
        if not data:
            return jsonify({"success": False, "error": "Category not found."}), 404
        return jsonify({
            "success": True,
            "data": data
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@analytics_bp.route('/analytics/ministry', methods=['GET'])
def analytics_by_ministry():
    """
    GET /api/analytics/ministry
    Returns breakdown of schemes by ministry.
    """
    try:
        data = get_ministry_statistics()
        return jsonify({
            "success": True,
            "data": data
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@analytics_bp.route('/analytics/category', methods=['GET'])
def analytics_by_category():
    """
    GET /api/analytics/category
    Returns breakdown of schemes by category.
    """
    try:
        data = get_category_statistics()
        return jsonify({
            "success": True,
            "data": data
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@analytics_bp.route('/analytics/scheme-type', methods=['GET'])
def analytics_by_scheme_type():
    """
    GET /api/analytics/scheme-type
    Returns breakdown of schemes by funding/scheme type.
    """
    try:
        data = get_scheme_type_statistics()
        return jsonify({
            "success": True,
            "data": data
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@analytics_bp.route('/analytics/cross-ministry', methods=['GET'])
def analytics_cross_ministry():
    """
    GET /api/analytics/cross-ministry
    Returns multi-ministry categories and relationship networks.
    """
    try:
        data = get_cross_ministry_relationships()
        return jsonify({
            "success": True,
            "data": data
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
