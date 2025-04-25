from .stashpoints import bp as stashpoints_bp


# Register blueprints here so they can be registered with the Flask app in __init__.py
__all__ = [ 'stashpoints_bp']
