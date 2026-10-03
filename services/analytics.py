"""
==============================================================================
CORE BUSINESS LOGIC & GOVERNANCE INTELLIGENCE
Maintainer: Person 5 (Core Logic & Analytics Engineer)
==============================================================================
Pure Python + Parameterized SQL analytics layer.
Provides deterministic cross-ministry aggregations, search, comparisons,
and relationship mapping across 120 Government of India central schemes.
Zero external AI APIs, zero machine learning models, 100% offline-ready.
==============================================================================
"""

import math
from database.db import query_db


def get_dashboard_statistics(db_path=None):
    """
    Computes Command Center governance intelligence metrics directly from SQLite.
    Returns counts, distributions, top ministries, and category breakdowns.
    """
    # 1. Total Schemes
    total_schemes_row = query_db("SELECT COUNT(*) as count FROM schemes", one=True, db_path=db_path)
    total_schemes = total_schemes_row['count'] if total_schemes_row else 0

    # 2. Ministries Count
    total_ministries_row = query_db("SELECT COUNT(DISTINCT ministry_id) as count FROM schemes", one=True, db_path=db_path)
    total_ministries = total_ministries_row['count'] if total_ministries_row else 0

    # 3. Categories Count
    total_categories_row = query_db("SELECT COUNT(DISTINCT category_id) as count FROM schemes", one=True, db_path=db_path)
    total_categories = total_categories_row['count'] if total_categories_row else 0

    # 4. Scheme Types Count
    total_types_row = query_db("SELECT COUNT(DISTINCT scheme_type) as count FROM schemes", one=True, db_path=db_path)
    total_types = total_types_row['count'] if total_types_row else 0

    # 5. Schemes by Ministry (Top ministries)
    ministry_stats = query_db("""
        SELECT 
            m.id as ministry_id,
            m.name as ministry_name,
            COUNT(s.id) as scheme_count,
            COUNT(DISTINCT s.category_id) as category_count
        FROM ministries m
        JOIN schemes s ON m.id = s.ministry_id
        GROUP BY m.id, m.name
        ORDER BY scheme_count DESC, m.name ASC
    """, db_path=db_path)

    # 6. Schemes by Category (Category distribution)
    category_stats = query_db("""
        SELECT 
            c.id as category_id,
            c.name as category_name,
            COUNT(s.id) as scheme_count,
            COUNT(DISTINCT s.ministry_id) as ministry_count
        FROM categories c
        JOIN schemes s ON c.id = s.category_id
        GROUP BY c.id, c.name
        ORDER BY scheme_count DESC, c.name ASC
    """, db_path=db_path)

    # 7. Schemes by Scheme Type
    scheme_type_stats = query_db("""
        SELECT 
            scheme_type,
            COUNT(id) as scheme_count
        FROM schemes
        GROUP BY scheme_type
        ORDER BY scheme_count DESC
    """, db_path=db_path)

    # 8. Schemes by Government Level
    gov_level_stats = query_db("""
        SELECT 
            government_level,
            COUNT(id) as scheme_count
        FROM schemes
        GROUP BY government_level
        ORDER BY scheme_count DESC
    """, db_path=db_path)

    # 9. Cross-Ministry Intersections (Categories shared by >= 2 ministries)
    shared_categories = [c for c in category_stats if c['ministry_count'] > 1]

    return {
        "total_schemes": total_schemes,
        "total_ministries": total_ministries,
        "total_categories": total_categories,
        "total_scheme_types": total_types,
        "ministry_distribution": ministry_stats,
        "top_ministries": ministry_stats[:8],
        "category_distribution": category_stats,
        "top_categories": category_stats[:10],
        "scheme_type_distribution": scheme_type_stats,
        "government_level_distribution": gov_level_stats,
        "cross_ministry_collaborations_count": len(shared_categories)
    }


def get_ministry_statistics(ministry_id=None, db_path=None):
    """
    Returns statistics for all ministries or a deep dive into one ministry.
    """
    if ministry_id is None:
        return query_db("""
            SELECT 
                m.id,
                m.name,
                COUNT(s.id) as scheme_count,
                COUNT(DISTINCT s.category_id) as category_count,
                GROUP_CONCAT(DISTINCT s.scheme_type) as scheme_types
            FROM ministries m
            LEFT JOIN schemes s ON m.id = s.ministry_id
            GROUP BY m.id, m.name
            ORDER BY scheme_count DESC, m.name ASC
        """, db_path=db_path)

    ministry = query_db("SELECT id, name FROM ministries WHERE id = ?", (ministry_id,), one=True, db_path=db_path)
    if not ministry:
        return None

    schemes = query_db("""
        SELECT 
            s.id,
            s.scheme_id,
            s.scheme_name,
            c.name as category,
            s.scheme_type,
            s.government_level,
            s.source_name,
            s.source_url,
            s.last_verified,
            sm.status,
            sm.beneficiary_type
        FROM schemes s
        JOIN categories c ON s.category_id = c.id
        LEFT JOIN scheme_metadata sm ON s.scheme_id = sm.scheme_id
        WHERE s.ministry_id = ?
        ORDER BY s.scheme_name ASC
    """, (ministry_id,), db_path=db_path)

    categories_covered = query_db("""
        SELECT c.id, c.name, COUNT(s.id) as count
        FROM categories c
        JOIN schemes s ON c.id = s.category_id
        WHERE s.ministry_id = ?
        GROUP BY c.id, c.name
        ORDER BY count DESC
    """, (ministry_id,), db_path=db_path)

    scheme_types = query_db("""
        SELECT scheme_type, COUNT(id) as count
        FROM schemes
        WHERE ministry_id = ?
        GROUP BY scheme_type
        ORDER BY count DESC
    """, (ministry_id,), db_path=db_path)

    return {
        "ministry": ministry,
        "total_schemes": len(schemes),
        "categories_covered": categories_covered,
        "scheme_types": scheme_types,
        "schemes": schemes
    }


def get_category_statistics(category_id=None, db_path=None):
    """
    Returns statistics for all categories or a deep dive into one category.
    """
    if category_id is None:
        return query_db("""
            SELECT 
                c.id,
                c.name,
                COUNT(s.id) as scheme_count,
                COUNT(DISTINCT s.ministry_id) as ministry_count,
                GROUP_CONCAT(DISTINCT s.scheme_type) as scheme_types
            FROM categories c
            LEFT JOIN schemes s ON c.id = s.category_id
            GROUP BY c.id, c.name
            ORDER BY scheme_count DESC, c.name ASC
        """, db_path=db_path)

    category = query_db("SELECT id, name FROM categories WHERE id = ?", (category_id,), one=True, db_path=db_path)
    if not category:
        return None

    schemes = query_db("""
        SELECT 
            s.id,
            s.scheme_id,
            s.scheme_name,
            m.name as ministry,
            s.scheme_type,
            s.government_level,
            s.source_name,
            s.source_url,
            s.last_verified,
            sm.status,
            sm.beneficiary_type
        FROM schemes s
        JOIN ministries m ON s.ministry_id = m.id
        LEFT JOIN scheme_metadata sm ON s.scheme_id = sm.scheme_id
        WHERE s.category_id = ?
        ORDER BY s.scheme_name ASC
    """, (category_id,), db_path=db_path)

    ministries_working = query_db("""
        SELECT m.id, m.name, COUNT(s.id) as count
        FROM ministries m
        JOIN schemes s ON m.id = s.ministry_id
        WHERE s.category_id = ?
        GROUP BY m.id, m.name
        ORDER BY count DESC
    """, (category_id,), db_path=db_path)

    scheme_types = query_db("""
        SELECT scheme_type, COUNT(id) as count
        FROM schemes
        WHERE category_id = ?
        GROUP BY scheme_type
        ORDER BY count DESC
    """, (category_id,), db_path=db_path)

    return {
        "category": category,
        "total_schemes": len(schemes),
        "ministries_working": ministries_working,
        "scheme_types": scheme_types,
        "schemes": schemes
    }


def get_scheme_type_statistics(db_path=None):
    """Returns scheme type breakdown across all 120 schemes."""
    return query_db("""
        SELECT 
            scheme_type,
            COUNT(id) as count,
            ROUND(COUNT(id) * 100.0 / (SELECT COUNT(*) FROM schemes), 1) as percentage
        FROM schemes
        GROUP BY scheme_type
        ORDER BY count DESC
    """, db_path=db_path)


def search_schemes(query='', ministry_id=None, category_id=None, scheme_type=None,
                   sort_by='scheme_name', sort_dir='asc', page=1, per_page=20, db_path=None):
    """
    Search and filter schemes using parameterized SQL queries.
    Supports multi-field keyword search across scheme name, ID, ministry, category, type.
    """
    base_query = """
        SELECT 
            s.id,
            s.scheme_id,
            s.scheme_name,
            m.name as ministry,
            m.id as ministry_id,
            c.name as category,
            c.id as category_id,
            s.scheme_type,
            s.government_level,
            s.source_name,
            s.source_url,
            s.last_verified,
            s.data_note,
            sm.status,
            sm.objective,
            sm.beneficiary_type
        FROM schemes s
        JOIN ministries m ON s.ministry_id = m.id
        JOIN categories c ON s.category_id = c.id
        LEFT JOIN scheme_metadata sm ON s.scheme_id = sm.scheme_id
        WHERE 1=1
    """
    count_query = """
        SELECT COUNT(*) as count
        FROM schemes s
        JOIN ministries m ON s.ministry_id = m.id
        JOIN categories c ON s.category_id = c.id
        WHERE 1=1
    """

    params = []
    count_params = []

    if query and query.strip():
        search_pattern = f"%{query.strip()}%"
        condition = """ AND (
            s.scheme_name LIKE ? OR 
            s.scheme_id LIKE ? OR 
            m.name LIKE ? OR 
            c.name LIKE ? OR 
            s.scheme_type LIKE ?
        )"""
        base_query += condition
        count_query += condition
        params.extend([search_pattern] * 5)
        count_params.extend([search_pattern] * 5)

    if ministry_id and str(ministry_id).lower() != 'all':
        base_query += " AND s.ministry_id = ?"
        count_query += " AND s.ministry_id = ?"
        params.append(int(ministry_id))
        count_params.append(int(ministry_id))

    if category_id and str(category_id).lower() != 'all':
        base_query += " AND s.category_id = ?"
        count_query += " AND s.category_id = ?"
        params.append(int(category_id))
        count_params.append(int(category_id))

    if scheme_type and str(scheme_type).lower() != 'all':
        base_query += " AND s.scheme_type = ?"
        count_query += " AND s.scheme_type = ?"
        params.append(scheme_type)
        count_params.append(scheme_type)

    # Total match count
    total_row = query_db(count_query, count_params, one=True, db_path=db_path)
    total_count = total_row['count'] if total_row else 0

    # Whitelist sorting columns to prevent SQL injection
    sort_column_map = {
        'scheme_name': 's.scheme_name',
        'scheme_id': 's.scheme_id',
        'ministry': 'm.name',
        'category': 'c.name',
        'scheme_type': 's.scheme_type'
    }
    sql_sort_col = sort_column_map.get(sort_by, 's.scheme_name')
    sql_sort_dir = 'DESC' if str(sort_dir).lower() == 'desc' else 'ASC'

    base_query += f" ORDER BY {sql_sort_col} {sql_sort_dir}"

    # Pagination
    page = max(int(page), 1)
    per_page = max(int(per_page), 1)
    offset = (page - 1) * per_page
    base_query += " LIMIT ? OFFSET ?"
    params.extend([per_page, offset])

    results = query_db(base_query, params, db_path=db_path)
    total_pages = math.ceil(total_count / per_page) if per_page else 1

    return {
        "schemes": results,
        "total": total_count,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages
    }


def get_scheme_by_id(scheme_id_or_num, db_path=None):
    """
    Fetches full detail for a single scheme by either scheme_id ('SCH001') or database id (int).
    """
    query = """
        SELECT 
            s.id,
            s.scheme_id,
            s.scheme_name,
            m.id as ministry_id,
            m.name as ministry_name,
            c.id as category_id,
            c.name as category_name,
            s.scheme_type,
            s.government_level,
            s.source_name,
            s.source_url,
            s.last_verified,
            s.data_note,
            s.created_at,
            s.updated_at,
            sm.department,
            sm.description,
            sm.objective,
            sm.beneficiary_type,
            sm.implementation_level,
            sm.geographic_scope,
            sm.launch_year,
            sm.status,
            sm.funding_pattern
        FROM schemes s
        JOIN ministries m ON s.ministry_id = m.id
        JOIN categories c ON s.category_id = c.id
        LEFT JOIN scheme_metadata sm ON s.scheme_id = sm.scheme_id
        WHERE s.scheme_id = ? OR s.id = ?
    """
    return query_db(query, (scheme_id_or_num, scheme_id_or_num), one=True, db_path=db_path)


def compare_schemes(scheme_ids, db_path=None):
    """
    Compares 2 or 3 schemes side-by-side using factual verified attributes.
    Does NOT assign subjective winners or arbitrary scores.
    """
    if not scheme_ids or not isinstance(scheme_ids, (list, tuple)):
        return {"error": "scheme_ids must be a list of 2 or 3 scheme IDs"}

    # Limit to 3 max
    selected_ids = [str(sid).strip() for sid in scheme_ids[:3] if str(sid).strip()]
    if len(selected_ids) < 2:
        return {"error": "Please provide at least 2 scheme IDs to compare"}

    schemes = []
    for sid in selected_ids:
        rec = get_scheme_by_id(sid, db_path=db_path)
        if rec:
            schemes.append(rec)

    if len(schemes) < 2:
        return {"error": "Could not find matching records for the selected scheme IDs"}

    # List of comparison attributes
    attribute_definitions = [
        {"key": "scheme_name", "label": "Scheme Name"},
        {"key": "scheme_id", "label": "Scheme ID"},
        {"key": "ministry_name", "label": "Ministry"},
        {"key": "category_name", "label": "Category"},
        {"key": "scheme_type", "label": "Scheme Type"},
        {"key": "government_level", "label": "Government Level"},
        {"key": "source_name", "label": "Official Source"},
        {"key": "last_verified", "label": "Last Verified Date"},
        {"key": "objective", "label": "Objective"},
        {"key": "beneficiary_type", "label": "Beneficiary Type"},
        {"key": "implementation_level", "label": "Implementation Level"},
        {"key": "geographic_scope", "label": "Geographic Scope"},
        {"key": "launch_year", "label": "Launch Year"},
        {"key": "status", "label": "Status"},
        {"key": "funding_pattern", "label": "Funding Pattern"}
    ]

    # Filter attributes where at least one scheme has a non-null, non-empty value
    active_attributes = []
    for attr in attribute_definitions:
        has_value = any(s.get(attr['key']) is not None and str(s.get(attr['key'])).strip() != '' for s in schemes)
        if has_value:
            active_attributes.append(attr)

    return {
        "schemes": schemes,
        "attributes": active_attributes,
        "count": len(schemes)
    }


def get_cross_ministry_relationships(db_path=None):
    """
    Builds deterministic cross-ministry governance relationship mapping:
    - Multi-ministry categories (e.g. Social Security, Education, Healthcare across departments)
    - Ministry -> Category -> Schemes graph
    """
    # Categories with multiple ministries working within them
    cross_categories = query_db("""
        SELECT 
            c.id as category_id,
            c.name as category_name,
            COUNT(s.id) as scheme_count,
            COUNT(DISTINCT s.ministry_id) as ministry_count
        FROM categories c
        JOIN schemes s ON c.id = s.category_id
        GROUP BY c.id, c.name
        HAVING COUNT(DISTINCT s.ministry_id) > 1
        ORDER BY ministry_count DESC, scheme_count DESC
    """, db_path=db_path)

    # For each cross-cutting category, list the ministries and their schemes
    enhanced_cross_categories = []
    for cat in cross_categories:
        cat_id = cat['category_id']
        ministries = query_db("""
            SELECT 
                m.id as ministry_id,
                m.name as ministry_name,
                COUNT(s.id) as scheme_count,
                GROUP_CONCAT(s.scheme_name, ' || ') as scheme_names_concat,
                GROUP_CONCAT(s.scheme_id, ' || ') as scheme_ids_concat
            FROM ministries m
            JOIN schemes s ON m.id = s.ministry_id
            WHERE s.category_id = ?
            GROUP BY m.id, m.name
            ORDER BY scheme_count DESC
        """, (cat_id,), db_path=db_path)

        ministry_nodes = []
        for m in ministries:
            names = m['scheme_names_concat'].split(' || ')
            ids = m['scheme_ids_concat'].split(' || ')
            schemes_list = [{"scheme_id": ids[i], "scheme_name": names[i]} for i in range(len(ids))]
            ministry_nodes.append({
                "ministry_id": m['ministry_id'],
                "ministry_name": m['ministry_name'],
                "scheme_count": m['scheme_count'],
                "schemes": schemes_list
            })

        enhanced_cross_categories.append({
            "category_id": cat_id,
            "category_name": cat['category_name'],
            "total_schemes": cat['scheme_count'],
            "ministry_count": cat['ministry_count'],
            "ministries": ministry_nodes
        })

    # Hierarchical tree structure: Ministry -> Categories -> Schemes
    ministries_tree = []
    all_ministries = query_db("SELECT id, name FROM ministries ORDER BY name ASC", db_path=db_path)
    for m in all_ministries:
        m_id = m['id']
        cats = query_db("""
            SELECT 
                c.id as category_id,
                c.name as category_name,
                COUNT(s.id) as scheme_count
            FROM categories c
            JOIN schemes s ON c.id = s.category_id
            WHERE s.ministry_id = ?
            GROUP BY c.id, c.name
            ORDER BY scheme_count DESC
        """, (m_id,), db_path=db_path)

        category_nodes = []
        total_m_schemes = 0
        for c in cats:
            total_m_schemes += c['scheme_count']
            schemes = query_db("""
                SELECT id, scheme_id, scheme_name, scheme_type, source_url
                FROM schemes
                WHERE ministry_id = ? AND category_id = ?
                ORDER BY scheme_name ASC
            """, (m_id, c['category_id']), db_path=db_path)
            category_nodes.append({
                "category_id": c['category_id'],
                "category_name": c['category_name'],
                "scheme_count": c['scheme_count'],
                "schemes": schemes
            })

        if total_m_schemes > 0:
            ministries_tree.append({
                "ministry_id": m_id,
                "ministry_name": m['name'],
                "total_schemes": total_m_schemes,
                "categories_count": len(category_nodes),
                "categories": category_nodes
            })

    return {
        "cross_cutting_categories": enhanced_cross_categories,
        "ministries_hierarchy": ministries_tree
    }
