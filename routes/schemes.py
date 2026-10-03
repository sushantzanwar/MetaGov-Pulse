"""
==============================================================================
SCHEMES REST API BLUEPRINT
Maintainer: Person 3 (Flask Backend Engineer)
==============================================================================
Provides REST endpoints for querying, filtering, pagination, detail viewing,
and comparative analysis across 120 Government of India central schemes.
==============================================================================
"""

from flask import Blueprint, request, jsonify
from services.analytics import search_schemes, get_scheme_by_id, compare_schemes

schemes_bp = Blueprint('schemes_api', __name__, url_prefix='/api')


@schemes_bp.route('/schemes', methods=['GET'])
def list_schemes():
    """
    GET /api/schemes
    Query params:
    - q: keyword search (name, ID, ministry, category, type)
    - ministry_id: int or 'all'
    - category_id: int or 'all'
    - scheme_type: str or 'all'
    - sort_by: 'scheme_name' | 'scheme_id' | 'ministry' | 'category' | 'scheme_type'
    - sort_dir: 'asc' | 'desc'
    - page: int (default 1)
    - per_page: int (default 20)
    """
    try:
        q = request.args.get('q', '').strip()
        ministry_id = request.args.get('ministry_id')
        category_id = request.args.get('category_id')
        scheme_type = request.args.get('scheme_type')
        sort_by = request.args.get('sort_by', 'scheme_name').strip()
        sort_dir = request.args.get('sort_dir', 'asc').strip()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        results = search_schemes(
            query=q,
            ministry_id=ministry_id,
            category_id=category_id,
            scheme_type=scheme_type,
            sort_by=sort_by,
            sort_dir=sort_dir,
            page=page,
            per_page=per_page
        )

        return jsonify({
            "success": True,
            **results
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Failed to retrieve schemes.",
            "details": str(e)
        }), 500


@schemes_bp.route('/schemes/<scheme_id>', methods=['GET'])
def get_single_scheme(scheme_id):
    """
    GET /api/schemes/<scheme_id>
    Fetches full scheme details with official verified source URL and metadata.
    """
    try:
        scheme = get_scheme_by_id(scheme_id)
        if not scheme:
            return jsonify({
                "success": False,
                "error": f"Scheme '{scheme_id}' was not found in the database."
            }), 404

        return jsonify({
            "success": True,
            "data": scheme
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Database error while fetching scheme details.",
            "details": str(e)
        }), 500


@schemes_bp.route('/search', methods=['GET'])
def global_search():
    """
    GET /api/search?q=...
    Direct search endpoint returning matching scheme records.
    """
    try:
        q = request.args.get('q', '').strip()
        if not q:
            return jsonify({
                "success": True,
                "query": "",
                "total": 0,
                "schemes": []
            }), 200

        results = search_schemes(query=q, per_page=50)
        return jsonify({
            "success": True,
            "query": q,
            **results
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Search failed.",
            "details": str(e)
        }), 500


@schemes_bp.route('/compare', methods=['POST'])
def compare_schemes_endpoint():
    """
    POST /api/compare
    Body: { "scheme_ids": ["SCH001", "SCH002"] }
    Returns factual side-by-side comparison without subjective scoring.
    """
    try:
        data = request.get_json(silent=True) or {}
        scheme_ids = data.get('scheme_ids', [])

        if not scheme_ids or len(scheme_ids) < 2:
            return jsonify({
                "success": False,
                "error": "Please provide at least 2 scheme IDs to compare."
            }), 400

        result = compare_schemes(scheme_ids)
        if "error" in result:
            return jsonify({
                "success": False,
                "error": result["error"]
            }), 400

        return jsonify({
            "success": True,
            "data": result
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Comparison failed.",
            "details": str(e)
        }), 500
