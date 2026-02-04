#!/usr/bin/env python3
"""
🌊 MATRIX BROADCAST STUDIO - GUEST MANAGEMENT SYSTEM
Professional multi-guest streaming with StreamYard-like functionality
Features: 6 guest slots, moderator controls, camera/mic configuration
"""

import os
import json
import uuid
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass, asdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GuestRole(Enum):
    """Guest role types"""
    GUEST = "guest"
    MODERATOR = "moderator"
    HOST = "host"
    SPECTATOR = "spectator"

class GuestStatus(Enum):
    """Guest connection status"""
    OFFLINE = "offline"
    CONNECTING = "connecting"
    ONLINE = "online"
    IN_STUDIO = "in_studio"
    ON_AIR = "on_air"
    MUTED = "muted"
    VIDEO_OFF = "video_off"
    KICKED = "kicked"

class MediaState(Enum):
    """Media state for camera/microphone"""
    ON = "on"
    OFF = "off"
    MUTED = "muted"
    DISABLED = "disabled"

@dataclass
class GuestDevice:
    """Guest device configuration"""
    camera_enabled: bool = True
    microphone_enabled: bool = True
    camera_device: str = "default"
    microphone_device: str = "default"
    video_quality: str = "720p"  # 360p, 480p, 720p, 1080p
    audio_quality: str = "high"  # low, medium, high
    background_blur: bool = False
    virtual_background: Optional[str] = None

@dataclass
class GuestPermissions:
    """Guest permission settings"""
    can_speak: bool = True
    can_video: bool = True
    can_share_screen: bool = False
    can_chat: bool = True
    can_moderate: bool = False
    can_invite: bool = False
    can_record: bool = False

@dataclass
class StreamGuest:
    """Stream guest with full functionality"""
    id: str
    name: str
    email: str
    role: GuestRole
    status: GuestStatus
    join_time: Optional[datetime] = None
    last_active: Optional[datetime] = None
    device: GuestDevice = None
    permissions: GuestPermissions = None
    invite_code: str = None
    slot_number: int = 0
    is_hand_raised: bool = False
    is_pinned: bool = False
    notes: str = ""
    ip_address: str = ""
    user_agent: str = ""
    avatar_url: Optional[str] = None
    avatar_id: Optional[str] = None
    display_name: Optional[str] = None
    
    def __post_init__(self):
        if not self.device:
            self.device = GuestDevice()
        if not self.permissions:
            self.permissions = GuestPermissions()
        if not self.invite_code:
            self.invite_code = str(uuid.uuid4())[:8].upper()
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        # Convert datetime objects to ISO strings
        if self.join_time:
            data['join_time'] = self.join_time.isoformat()
        if self.last_active:
            data['last_active'] = self.last_active.isoformat()
        # Convert enums to values
        data['role'] = self.role.value
        data['status'] = self.status.value
        return data
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create from dictionary"""
        data['role'] = GuestRole(data.get('role', 'guest'))
        data['status'] = GuestStatus(data.get('status', 'offline'))
        # Convert ISO strings back to datetime
        if data.get('join_time'):
            data['join_time'] = datetime.fromisoformat(data['join_time'])
        if data.get('last_active'):
            data['last_active'] = datetime.fromisoformat(data['last_active'])
        return cls(**data)

class GuestManager:
    """Professional guest management system"""
    
    def __init__(self, max_guests: int = 6):
        self.max_guests = max_guests
        self.guests: Dict[str, StreamGuest] = {}
        self.guest_slots: Dict[int, str] = {}  # slot_number -> guest_id
        self.waiting_room: List[str] = []  # guest_ids waiting to join
        self.invite_codes: Dict[str, str] = {}  # invite_code -> guest_id
        self.moderator_controls = {
            'global_mute': False,
            'lock_studio': False,
            'auto_admit': False,
            'waiting_room_enabled': True
        }
        
        logger.info(f"🌊 Guest Manager initialized with {max_guests} guest slots")
    
    def create_guest_invite(self, name: str, email: str, role: GuestRole = GuestRole.GUEST) -> dict:
        """Create a guest invitation"""
        guest_id = str(uuid.uuid4())
        invite_code = str(uuid.uuid4())[:8].upper()
        
        guest = StreamGuest(
            id=guest_id,
            name=name,
            email=email,
            role=role,
            status=GuestStatus.OFFLINE,
            invite_code=invite_code
        )
        
        self.guests[guest_id] = guest
        self.invite_codes[invite_code] = guest_id
        
        logger.info(f"✅ Created invite for {name} ({email}) with code: {invite_code}")
        
        return {
            'guest_id': guest_id,
            'invite_code': invite_code,
            'invite_url': f"https://localhost:8080/join/{invite_code}",
            'guest': guest.to_dict()
        }
    
    def join_via_invite(self, invite_code: str, ip_address: str = "", user_agent: str = "") -> dict:
        """Guest joins via invite code"""
        if invite_code not in self.invite_codes:
            raise ValueError("Invalid invite code")
        
        guest_id = self.invite_codes[invite_code]
        guest = self.guests[guest_id]
        
        if guest.status not in [GuestStatus.OFFLINE, GuestStatus.KICKED]:
            raise ValueError("Guest already connected")
        
        # Check if studio is full
        if len(self.get_active_guests()) >= self.max_guests:
            # Add to waiting room
            if guest_id not in self.waiting_room:
                self.waiting_room.append(guest_id)
            guest.status = GuestStatus.CONNECTING
            return {'status': 'waiting_room', 'message': 'Studio is full, you are in the waiting room'}
        
        # Assign slot
        slot_number = self._get_available_slot()
        if slot_number is None:
            self.waiting_room.append(guest_id)
            guest.status = GuestStatus.CONNECTING
            return {'status': 'waiting_room', 'message': 'No available slots'}
        
        guest.slot_number = slot_number
        self.guest_slots[slot_number] = guest_id
        guest.status = GuestStatus.CONNECTING
        guest.join_time = datetime.utcnow()
        guest.ip_address = ip_address
        guest.user_agent = user_agent
        guest.last_active = datetime.utcnow()
        
        logger.info(f"👤 Guest {guest.name} joined via invite {invite_code}")
        
        return {
            'status': 'connected',
            'guest': guest.to_dict(),
            'slot_number': slot_number
        }
    
    def _get_available_slot(self) -> Optional[int]:
        """Get next available guest slot"""
        for slot in range(1, self.max_guests + 1):
            if slot not in self.guest_slots:
                return slot
        return None
    
    def get_active_guests(self) -> List[StreamGuest]:
        """Get all active guests"""
        return [guest for guest in self.guests.values() 
                if guest.status in [GuestStatus.ONLINE, GuestStatus.IN_STUDIO, GuestStatus.ON_AIR]]
    
    def get_guest_in_slot(self, slot_number: int) -> Optional[StreamGuest]:
        """Get guest in specific slot"""
        if slot_number in self.guest_slots:
            guest_id = self.guest_slots[slot_number]
            return self.guests.get(guest_id)
        return None
    
    def moderator_mute_guest(self, guest_id: str, moderator_id: str) -> bool:
        """Moderator mutes a guest"""
        if guest_id not in self.guests:
            return False
        
        guest = self.guests[guest_id]
        guest.status = GuestStatus.MUTED
        guest.device.microphone_enabled = False
        guest.last_active = datetime.utcnow()
        
        logger.info(f"🔇 Moderator {moderator_id} muted guest {guest.name}")
        return True
    
    def moderator_stop_camera(self, guest_id: str, moderator_id: str) -> bool:
        """Moderator stops guest camera"""
        if guest_id not in self.guests:
            return False
        
        guest = self.guests[guest_id]
        guest.device.camera_enabled = False
        guest.status = GuestStatus.VIDEO_OFF
        guest.last_active = datetime.utcnow()
        
        logger.info(f"📹 Moderator {moderator_id} stopped camera for guest {guest.name}")
        return True
    
    def moderator_kick_guest(self, guest_id: str, moderator_id: str, reason: str = "") -> bool:
        """Moderator kicks a guest"""
        if guest_id not in self.guests:
            return False
        
        guest = self.guests[guest_id]
        
        # Free up the slot
        if guest.slot_number in self.guest_slots:
            del self.guest_slots[guest.slot_number]
        
        guest.status = GuestStatus.KICKED
        guest.last_active = datetime.utcnow()
        
        # Remove from waiting room if there
        if guest_id in self.waiting_room:
            self.waiting_room.remove(guest_id)
        
        # Admit next person from waiting room
        self._admit_from_waiting_room()
        
        logger.info(f"👢 Moderator {moderator_id} kicked guest {guest.name}. Reason: {reason}")
        return True
    
    def _admit_from_waiting_room(self):
        """Admit next guest from waiting room"""
        if self.waiting_room and len(self.get_active_guests()) < self.max_guests:
            next_guest_id = self.waiting_room.pop(0)
            next_guest = self.guests[next_guest_id]
            
            slot_number = self._get_available_slot()
            if slot_number:
                next_guest.slot_number = slot_number
                self.guest_slots[slot_number] = next_guest_id
                next_guest.status = GuestStatus.ONLINE
                next_guest.last_active = datetime.utcnow()
                
                logger.info(f"✅ Admitted {next_guest.name} from waiting room to slot {slot_number}")
    
    def set_guest_media_state(self, guest_id: str, camera: MediaState = None, microphone: MediaState = None) -> bool:
        """Update guest media state"""
        if guest_id not in self.guests:
            return False
        
        guest = self.guests[guest_id]
        
        if camera:
            if camera == MediaState.ON:
                guest.device.camera_enabled = True
                guest.status = GuestStatus.ONLINE
            elif camera == MediaState.OFF:
                guest.device.camera_enabled = False
                guest.status = GuestStatus.VIDEO_OFF
            elif camera == MediaState.DISABLED:
                guest.device.camera_enabled = False
                guest.permissions.can_video = False
        
        if microphone:
            if microphone == MediaState.ON:
                guest.device.microphone_enabled = True
                if guest.status != GuestStatus.VIDEO_OFF:
                    guest.status = GuestStatus.ONLINE
            elif microphone == MediaState.OFF:
                guest.device.microphone_enabled = True
                guest.status = GuestStatus.MUTED
            elif microphone == MediaState.MUTED:
                guest.device.microphone_enabled = False
                guest.status = GuestStatus.MUTED
            elif microphone == MediaState.DISABLED:
                guest.device.microphone_enabled = False
                guest.permissions.can_speak = False
        
        guest.last_active = datetime.utcnow()
        return True
    
    def update_guest_device_config(self, guest_id: str, device_config: dict) -> bool:
        """Update guest device configuration"""
        if guest_id not in self.guests:
            return False
        
        guest = self.guests[guest_id]
        
        if 'video_quality' in device_config:
            guest.device.video_quality = device_config['video_quality']
        if 'audio_quality' in device_config:
            guest.device.audio_quality = device_config['audio_quality']
        if 'background_blur' in device_config:
            guest.device.background_blur = device_config['background_blur']
        if 'virtual_background' in device_config:
            guest.device.virtual_background = device_config['virtual_background']
        if 'camera_device' in device_config:
            guest.device.camera_device = device_config['camera_device']
        if 'microphone_device' in device_config:
            guest.device.microphone_device = device_config['microphone_device']
        
        guest.last_active = datetime.utcnow()
        logger.info(f"⚙️ Updated device config for guest {guest.name}")
        return True
    
    def raise_hand(self, guest_id: str) -> bool:
        """Guest raises hand"""
        if guest_id not in self.guests:
            return False
        
        guest = self.guests[guest_id]
        guest.is_hand_raised = True
        guest.last_active = datetime.utcnow()
        
        logger.info(f"✋ Guest {guest.name} raised hand")
        return True
    
    def lower_hand(self, guest_id: str) -> bool:
        """Guest lowers hand"""
        if guest_id not in self.guests:
            return False
        
        guest = self.guests[guest_id]
        guest.is_hand_raised = False
        guest.last_active = datetime.utcnow()
        
        logger.info(f"👇 Guest {guest.name} lowered hand")
        return True
    
    def pin_guest(self, guest_id: str, moderator_id: str) -> bool:
        """Moderator pins a guest"""
        if guest_id not in self.guests:
            return False
        
        guest = self.guests[guest_id]
        guest.is_pinned = True
        guest.last_active = datetime.utcnow()
        
        logger.info(f"📌 Moderator {moderator_id} pinned guest {guest.name}")
        return True
    
    def get_studio_status(self) -> dict:
        """Get current studio status"""
        active_guests = self.get_active_guests()
        waiting_count = len(self.waiting_room)
        
        return {
            'total_slots': self.max_guests,
            'occupied_slots': len(active_guests),
            'available_slots': self.max_guests - len(active_guests),
            'waiting_room_count': waiting_count,
            'guests_in_studio': [guest.to_dict() for guest in active_guests],
            'waiting_room': [self.guests[guest_id].to_dict() for guest_id in self.waiting_room],
            'moderator_controls': self.moderator_controls,
            'slot_layout': self._get_slot_layout()
        }
    
    def _get_slot_layout(self) -> dict:
        """Get current slot layout"""
        layout = {}
        for slot_num in range(1, self.max_guests + 1):
            if slot_num in self.guest_slots:
                guest_id = self.guest_slots[slot_num]
                guest = self.guests.get(guest_id)
                if guest:
                    layout[f'slot_{slot_num}'] = {
                        'guest_id': guest_id,
                        'name': guest.name,
                        'status': guest.status.value,
                        'role': guest.role.value,
                        'camera_enabled': guest.device.camera_enabled,
                        'microphone_enabled': guest.device.microphone_enabled,
                        'is_pinned': guest.is_pinned,
                        'is_hand_raised': guest.is_hand_raised
                    }
                else:
                    layout[f'slot_{slot_num}'] = None
            else:
                layout[f'slot_{slot_num}'] = None
        
        return layout
    
    def export_guest_list(self) -> dict:
        """Export guest list for reporting"""
        return {
            'total_guests': len(self.guests),
            'active_guests': len(self.get_active_guests()),
            'waiting_guests': len(self.waiting_room),
            'guests': [guest.to_dict() for guest in self.guests.values()],
            'export_time': datetime.utcnow().isoformat()
        }

# Global guest manager instance
guest_manager = GuestManager(max_guests=6)

# Flask API endpoints for guest management
def setup_guest_api(app):
    """Setup guest management API endpoints"""
    
    @app.route('/api/guests/invite', methods=['POST'])
    def create_guest_invite():
        """Create a new guest invitation"""
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        role = data.get('role', 'guest')
        
        try:
            guest_role = GuestRole(role.lower())
        except ValueError:
            return jsonify({'error': 'Invalid role'}), 400
        
        result = guest_manager.create_guest_invite(name, email, guest_role)
        return jsonify(result)
    
    @app.route('/api/guests/join/<invite_code>', methods=['POST'])
    def join_via_invite(invite_code):
        """Guest joins via invite code"""
        data = request.get_json() or {}
        ip_address = data.get('ip_address', request.remote_addr)
        user_agent = data.get('user_agent', request.headers.get('User-Agent', ''))
        
        try:
            result = guest_manager.join_via_invite(invite_code, ip_address, user_agent)
            return jsonify(result)
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
    
    @app.route('/api/guests/status', methods=['GET'])
    def get_studio_status():
        """Get current studio status"""
        return jsonify(guest_manager.get_studio_status())
    
    @app.route('/api/guests/<guest_id>/moderate/mute', methods=['POST'])
    def moderator_mute_guest(guest_id):
        """Moderator mutes a guest"""
        data = request.get_json()
        moderator_id = data.get('moderator_id')
        
        if not moderator_id:
            return jsonify({'error': 'Moderator ID required'}), 400
        
        success = guest_manager.moderator_mute_guest(guest_id, moderator_id)
        return jsonify({'success': success})
    
    @app.route('/api/guests/<guest_id>/moderate/camera', methods=['POST'])
    def moderator_stop_camera(guest_id):
        """Moderator stops guest camera"""
        data = request.get_json()
        moderator_id = data.get('moderator_id')
        
        if not moderator_id:
            return jsonify({'error': 'Moderator ID required'}), 400
        
        success = guest_manager.moderator_stop_camera(guest_id, moderator_id)
        return jsonify({'success': success})
    
    @app.route('/api/guests/<guest_id>/moderate/kick', methods=['POST'])
    def moderator_kick_guest(guest_id):
        """Moderator kicks a guest"""
        data = request.get_json()
        moderator_id = data.get('moderator_id')
        reason = data.get('reason', '')
        
        if not moderator_id:
            return jsonify({'error': 'Moderator ID required'}), 400
        
        success = guest_manager.moderator_kick_guest(guest_id, moderator_id, reason)
        return jsonify({'success': success})
    
    @app.route('/api/guests/<guest_id>/media', methods=['PUT'])
    def update_guest_media(guest_id):
        """Update guest media state"""
        data = request.get_json()
        camera_state = data.get('camera')
        microphone_state = data.get('microphone')
        
        camera = MediaState(camera_state) if camera_state else None
        microphone = MediaState(microphone_state) if microphone_state else None
        
        success = guest_manager.set_guest_media_state(guest_id, camera, microphone)
        return jsonify({'success': success})
    
    @app.route('/api/guests/<guest_id>/device', methods=['PUT'])
    def update_guest_device(guest_id):
        """Update guest device configuration"""
        data = request.get_json()
        success = guest_manager.update_guest_device_config(guest_id, data)
        return jsonify({'success': success})
    
    @app.route('/api/guests/<guest_id>/hand/raise', methods=['POST'])
    def raise_guest_hand(guest_id):
        """Guest raises hand"""
        success = guest_manager.raise_hand(guest_id)
        return jsonify({'success': success})
    
    @app.route('/api/guests/<guest_id>/hand/lower', methods=['POST'])
    def lower_guest_hand(guest_id):
        """Guest lowers hand"""
        success = guest_manager.lower_hand(guest_id)
        return jsonify({'success': success})
    
    @app.route('/api/guests/<guest_id>/pin', methods=['POST'])
    def pin_guest(guest_id):
        """Moderator pins a guest"""
        data = request.get_json()
        moderator_id = data.get('moderator_id')
        
        if not moderator_id:
            return jsonify({'error': 'Moderator ID required'}), 400
        
        success = guest_manager.pin_guest(guest_id, moderator_id)
        return jsonify({'success': success})
    
    @app.route('/api/guests/export', methods=['GET'])
    def export_guest_list():
        """Export guest list"""
        return jsonify(guest_manager.export_guest_list())

if __name__ == "__main__":
    # Demo usage
    print("🌊 Matrix Broadcast Studio - Guest Management System")
    print("=" * 60)
    
    # Create some test guests
    guest1 = guest_manager.create_guest_invite("John Doe", "john@example.com", GuestRole.GUEST)
    guest2 = guest_manager.create_guest_invite("Jane Smith", "jane@example.com", GuestRole.MODERATOR)
    
    print(f"✅ Created guest invite for John: {guest1['invite_code']}")
    print(f"✅ Created guest invite for Jane: {guest2['invite_code']}")
    
    # Simulate guest joining
    join_result = guest_manager.join_via_invite(guest1['invite_code'])
    print(f"👤 Guest join result: {join_result}")
    
    # Get studio status
    status = guest_manager.get_studio_status()
    print(f"📊 Studio status: {status['occupied_slots']}/{status['total_slots']} slots occupied")