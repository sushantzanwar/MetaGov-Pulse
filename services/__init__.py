"""Services package initialization."""
from services.analytics import (
    get_dashboard_statistics,
    get_ministry_statistics,
    get_category_statistics,
    get_scheme_type_statistics,
    search_schemes,
    get_scheme_by_id,
    compare_schemes,
    get_cross_ministry_relationships
)

__all__ = [
    'get_dashboard_statistics',
    'get_ministry_statistics',
    'get_category_statistics',
    'get_scheme_type_statistics',
    'search_schemes',
    'get_scheme_by_id',
    'compare_schemes',
    'get_cross_ministry_relationships'
]
