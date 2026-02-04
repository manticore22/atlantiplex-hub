# Core Init
from .unified_broadcast_server import unified_system, app, socketio

# Component Imports
from .broadcasting.broadcast_engine import BroadcastEngine
from .guests.guest_management import GuestManagementSystem
from .scenes.scene_manager import SceneManager
from .platforms.platform_integrations import MultiPlatformStreamer
from .obs.obs_integration import OBSController
from .analytics.analytics import AnalyticsEngine
from .scheduler import StreamScheduler

__version__ = "2.0.0"
__author__ = "Matrix Studio Team"
__description__ = "Professional multi-platform streaming platform"