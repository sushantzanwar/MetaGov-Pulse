"""Routes package initialization."""
from routes.schemes import schemes_bp
from routes.analytics import analytics_bp
from routes.dashboard import dashboard_bp

__all__ = ['schemes_bp', 'analytics_bp', 'dashboard_bp']
