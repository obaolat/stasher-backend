from .stashpoints import bp as stashpoints_bp
from .stashpoint_search import bp as stashpoint_search_bp

# Register blueprints here so they can be registered with the Flask app in __init__.py
__all__ = ['stashpoint_search_bp', 'stashpoints_bp']
