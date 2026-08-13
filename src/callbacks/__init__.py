"""
SMPOOS Callbacks Package
Contains all Dash callback functions organized by feature.
"""

from .auth_callbacks import register_auth_callbacks
from .location_callbacks import register_location_callbacks
from .route_callbacks import register_route_callbacks
from .user_callbacks import register_user_callbacks
from .notification_callbacks import register_notification_callbacks
from .realtime_callbacks import register_realtime_callbacks
from .rbac_callbacks import register_rbac_callbacks


def register_all_callbacks(app, system):
    """
    Register all callback functions with the Dash app.

    Args:
        app: Dash application instance
        system: SMPOOS system instance
    """
    register_auth_callbacks(app, system)
    register_location_callbacks(app, system)
    register_route_callbacks(app, system)
    register_user_callbacks(app, system)
    register_notification_callbacks(app, system)
    register_realtime_callbacks(app, system)
    register_rbac_callbacks(app, system)
