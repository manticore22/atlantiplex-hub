import unittest
import sys
import os
import time
from unittest.mock import Mock, patch

# Add core to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))

class TestBroadcastEngine(unittest.TestCase):
    """Test the broadcast engine functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        from broadcasting.broadcast_engine import BroadcastEngine
        self.engine = BroadcastEngine()
    
    def test_engine_initialization(self):
        """Test that engine initializes correctly"""
        self.assertIsNotNone(self.engine)
        self.assertEqual(self.engine.is_broadcasting, False)
        self.assertEqual(len(self.engine.active_streams), 0)
    
    def test_stream_quality_presets(self):
        """Test stream quality presets"""
        from broadcasting.broadcast_engine import StreamQuality
        
        qualities = StreamQuality.QUALITY_PRESETS
        self.assertIn('720p', qualities)
        self.assertIn('1080p', qualities)
        self.assertIn('480p', qualities)
        
        quality_720p = StreamQuality.get_quality('720p')
        self.assertEqual(quality_720p['width'], 1280)
        self.assertEqual(quality_720p['height'], 720)
    
    def test_initialize_streaming(self):
        """Test streaming initialization"""
        result = self.engine.initialize_streaming('720p')
        self.assertTrue(result['success'])
        self.assertEqual(result['quality']['width'], 1280)
        self.assertEqual(result['quality']['height'], 720)
    
    @patch('subprocess.Popen')
    def test_start_platform_stream(self, mock_popen):
        """Test starting platform stream"""
        mock_popen.return_value = Mock()
        
        config = {
            'rtmp_url': 'rtmp://test.com/live',
            'stream_key': 'test_key'
        }
        
        result = self.engine.start_platform_stream('test_platform', config)
        self.assertTrue(result['success'])
        self.assertIn('test_platform', self.engine.active_streams)
    
    def test_stop_platform_stream(self):
        """Test stopping platform stream"""
        # Add a mock stream
        self.engine.active_streams['test'] = {
            'platform': 'test',
            'process': Mock(),
            'started_at': time.time()
        }
        
        result = self.engine.stop_platform_stream('test')
        self.assertTrue(result['success'])
        self.assertNotIn('test', self.engine.active_streams)

class TestGuestManagement(unittest.TestCase):
    """Test guest management system"""
    
    def setUp(self):
        """Set up test fixtures"""
        from guests.guest_management import GuestManagementSystem
        self.guest_manager = GuestManagementSystem()
    
    def test_add_guest(self):
        """Test adding a guest"""
        guest_data = {
            'name': 'Test Guest',
            'email': 'test@example.com',
            'role': 'guest'
        }
        
        result = self.guest_manager.add_guest(guest_data)
        self.assertTrue(result['success'])
        self.assertIn('guest_id', result)
    
    def test_guest_limits(self):
        """Test guest slot limits"""
        # Add maximum guests
        for i in range(6):
            guest_data = {
                'name': f'Guest {i}',
                'email': f'guest{i}@example.com',
                'role': 'guest'
            }
            self.guest_manager.add_guest(guest_data)
        
        # Try to add one more (should fail)
        guest_data = {
            'name': 'Extra Guest',
            'email': 'extra@example.com',
            'role': 'guest'
        }
        
        result = self.guest_manager.add_guest(guest_data)
        self.assertFalse(result['success'])
        self.assertIn('Guest limit reached', result['error'])

class TestSceneManager(unittest.TestCase):
    """Test scene management system"""
    
    def setUp(self):
        """Set up test fixtures"""
        from scenes.scene_manager import SceneManager
        self.scene_manager = SceneManager()
    
    def test_create_scene(self):
        """Test scene creation"""
        scene_data = {
            'name': 'Test Scene',
            'description': 'Test description'
        }
        
        scene = self.scene_manager.create_scene(scene_data)
        self.assertIsNotNone(scene)
        self.assertEqual(scene.name, 'Test Scene')
    
    def test_switch_scene(self):
        """Test scene switching"""
        # Create test scenes
        scene1 = self.scene_manager.create_scene({'name': 'Scene 1'})
        scene2 = self.scene_manager.create_scene({'name': 'Scene 2'})
        
        # Switch to scene 1
        result = self.scene_manager.switch_scene(scene1.id)
        self.assertTrue(result)
        
        # Switch to scene 2
        result = self.scene_manager.switch_scene(scene2.id)
        self.assertTrue(result)
        self.assertEqual(self.scene_manager.current_scene.id, scene2.id)

class TestPlatformIntegrations(unittest.TestCase):
    """Test platform integration system"""
    
    def setUp(self):
        """Set up test fixtures"""
        from platforms.platform_integrations import MultiPlatformStreamer
        self.platform_streamer = MultiPlatformStreamer()
    
    def test_add_youtube_streamer(self):
        """Test adding YouTube streamer"""
        self.platform_streamer.add_youtube_streamer('test_key', 'test_secret')
        self.assertIn('youtube', self.platform_streamer.streamers)
    
    def test_add_twitch_streamer(self):
        """Test adding Twitch streamer"""
        self.platform_streamer.add_twitch_streamer('test_id', 'test_secret', 'test_token')
        self.assertIn('twitch', self.platform_streamer.streamers)
    
    @patch('requests.post')
    def test_twitch_auth(self, mock_post):
        """Test Twitch authentication"""
        mock_post.return_value.json.return_value = {
            'access_token': 'test_token'
        }
        mock_post.return_value.status_code = 200
        
        self.platform_streamer.add_twitch_streamer('test_id', 'test_secret')
        twitch_streamer = self.platform_streamer.streamers['twitch']
        result = twitch_streamer.authenticate()
        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main(verbosity=2)