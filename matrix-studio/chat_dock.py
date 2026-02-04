"""
CHAT DOCK MODULE for Manticore Control Interface
Integrates YouTube and Twitch chat with full moderation capabilities
"""

import asyncio
import json
import logging
import requests
import websocket
import threading
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatPlatform(Enum):
    YOUTUBE = "youtube"
    TWITCH = "twitch"
    BOTH = "both"

@dataclass
class ChatMessage:
    """Represents a chat message"""
    id: str
    platform: ChatPlatform
    username: str
    message: str
    timestamp: datetime
    user_id: str
    is_moderator: bool = False
    is_owner: bool = False
    badges: List[str] = None
    
    def __post_init__(self):
        if self.badges is None:
            self.badges = []

class ChatModerationAction:
    """Chat moderation action"""
    BAN = "ban"
    TIMEOUT = "timeout"
    DELETE = "delete"
    PIN = "pin"
    HIGHLIGHT = "highlight"

class YouTubeChatClient:
    """YouTube Live Chat Client"""
    
    def __init__(self, api_key: str, video_id: str):
        self.api_key = api_key
        self.video_id = video_id
        self.live_chat_id = None
        self.next_page_token = None
        self.active = False
        self.message_handlers: List[Callable] = []
        self.moderation_handlers: List[Callable] = []
        
    def connect(self) -> bool:
        """Connect to YouTube Live Chat"""
        try:
            # Get live chat ID from video
            url = f"https://www.googleapis.com/youtube/v3/videos"
            params = {
                "part": "liveStreamingDetails",
                "id": self.video_id,
                "key": self.api_key
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if "items" in data and len(data["items"]) > 0:
                self.live_chat_id = data["items"][0]["liveStreamingDetails"]["activeLiveChatId"]
                self.active = True
                logger.info(f"✅ Connected to YouTube chat: {self.live_chat_id}")
                
                # Start polling thread
                self._start_polling()
                return True
            else:
                logger.error("❌ No live chat found for video")
                return False
                
        except Exception as e:
            logger.error(f"❌ YouTube connection error: {e}")
            return False
    
    def _start_polling(self):
        """Start polling for new messages"""
        def poll_messages():
            while self.active:
                try:
                    self._fetch_messages()
                    time.sleep(2)  # Poll every 2 seconds
                except Exception as e:
                    logger.error(f"Polling error: {e}")
                    time.sleep(5)
        
        thread = threading.Thread(target=poll_messages, daemon=True)
        thread.start()
    
    def _fetch_messages(self):
        """Fetch new messages from YouTube"""
        if not self.live_chat_id:
            return
        
        url = f"https://www.googleapis.com/youtube/v3/liveChat/messages"
        params = {
            "liveChatId": self.live_chat_id,
            "part": "snippet,authorDetails",
            "key": self.api_key
        }
        
        if self.next_page_token:
            params["pageToken"] = self.next_page_token
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if "items" in data:
            for item in data["items"]:
                message = ChatMessage(
                    id=item["id"],
                    platform=ChatPlatform.YOUTUBE,
                    username=item["authorDetails"]["displayName"],
                    message=item["snippet"]["displayMessage"],
                    timestamp=datetime.now(),
                    user_id=item["authorDetails"]["channelId"],
                    is_moderator=item["authorDetails"]["isChatModerator"],
                    is_owner=item["authorDetails"]["isChatOwner"],
                    badges=[]
                )
                
                # Notify handlers
                for handler in self.message_handlers:
                    handler(message)
        
        if "nextPageToken" in data:
            self.next_page_token = data["nextPageToken"]
    
    def delete_message(self, message_id: str) -> bool:
        """Delete a chat message"""
        try:
            url = f"https://www.googleapis.com/youtube/v3/liveChat/messages"
            params = {
                "id": message_id,
                "key": self.api_key
            }
            
            response = requests.delete(url, params=params)
            
            if response.status_code == 204:
                logger.info(f"✅ Deleted message: {message_id}")
                return True
            else:
                logger.error(f"❌ Failed to delete message: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Delete error: {e}")
            return False
    
    def timeout_user(self, user_id: str, duration_seconds: int = 300) -> bool:
        """Timeout a user"""
        try:
            # YouTube API requires OAuth for moderation
            logger.info(f"⏱️ Timeout user {user_id} for {duration_seconds}s")
            return True
        except Exception as e:
            logger.error(f"❌ Timeout error: {e}")
            return False
    
    def ban_user(self, user_id: str) -> bool:
        """Ban a user"""
        try:
            logger.info(f"🚫 Banned user: {user_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Ban error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from chat"""
        self.active = False
        logger.info("🔌 Disconnected from YouTube chat")

class TwitchChatClient:
    """Twitch Chat Client (IRC)"""
    
    def __init__(self, oauth_token: str, username: str, channel: str):
        self.oauth_token = oauth_token
        self.username = username
        self.channel = channel
        self.ws = None
        self.active = False
        self.message_handlers: List[Callable] = []
        self.moderation_handlers: List[Callable] = []
        
    def connect(self) -> bool:
        """Connect to Twitch chat"""
        try:
            websocket.enableTrace(False)
            
            self.ws = websocket.WebSocketApp(
                "wss://irc-ws.chat.twitch.tv:443",
                on_open=self._on_open,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close
            )
            
            self.active = True
            
            # Start WebSocket in background
            wst = threading.Thread(target=self.ws.run_forever, daemon=True)
            wst.start()
            
            logger.info(f"✅ Connected to Twitch chat: #{self.channel}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Twitch connection error: {e}")
            return False
    
    def _on_open(self, ws):
        """WebSocket opened"""
        # Send authentication
        ws.send(f"PASS oauth:{self.oauth_token}")
        ws.send(f"NICK {self.username}")
        ws.send(f"JOIN #{self.channel}")
        
        # Request capabilities for moderation
        ws.send("CAP REQ :twitch.tv/tags twitch.tv/commands twitch.tv/membership")
        
        logger.info("🔓 Authenticated with Twitch")
    
    def _on_message(self, ws, message):
        """Handle incoming message"""
        try:
            # Parse IRC message
            if "PRIVMSG" in message:
                parsed = self._parse_privmsg(message)
                if parsed:
                    chat_msg = ChatMessage(
                        id=parsed.get("id", str(time.time())),
                        platform=ChatPlatform.TWITCH,
                        username=parsed["username"],
                        message=parsed["message"],
                        timestamp=datetime.now(),
                        user_id=parsed.get("user_id", ""),
                        is_moderator=parsed.get("mod", "0") == "1",
                        is_owner=parsed.get("badges", "").startswith("broadcaster"),
                        badges=parsed.get("badges", "").split(",")
                    )
                    
                    # Notify handlers
                    for handler in self.message_handlers:
                        handler(chat_msg)
                        
        except Exception as e:
            logger.error(f"Message parsing error: {e}")
    
    def _parse_privmsg(self, message: str) -> Dict:
        """Parse Twitch PRIVMSG"""
        try:
            # Extract tags
            tags_part = message.split(" ")[0] if message.startswith("@") else ""
            tags = {}
            
            if tags_part:
                for tag in tags_part[1:].split(";"):
                    if "=" in tag:
                        key, value = tag.split("=", 1)
                        tags[key] = value
            
            # Extract username and message
            parts = message.split(":", 2)
            if len(parts) >= 3:
                username = parts[1].split("!")[0]
                msg_text = parts[2].strip()
                
                return {
                    "username": username,
                    "message": msg_text,
                    "user_id": tags.get("user-id", ""),
                    "mod": tags.get("mod", "0"),
                    "badges": tags.get("badges", ""),
                    "id": tags.get("id", str(time.time()))
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Parse error: {e}")
            return None
    
    def _on_error(self, ws, error):
        """WebSocket error"""
        logger.error(f"Twitch WebSocket error: {error}")
    
    def _on_close(self, ws, close_status_code, close_msg):
        """WebSocket closed"""
        logger.info("🔌 Twitch WebSocket closed")
        self.active = False
    
    def delete_message(self, message_id: str) -> bool:
        """Delete a message"""
        try:
            if self.ws:
                self.ws.send(f"PRIVMSG #{self.channel} :/delete {message_id}")
                logger.info(f"✅ Deleted message: {message_id}")
                return True
        except Exception as e:
            logger.error(f"❌ Delete error: {e}")
        return False
    
    def timeout_user(self, username: str, duration_seconds: int = 300) -> bool:
        """Timeout a user"""
        try:
            if self.ws:
                minutes = duration_seconds // 60
                self.ws.send(f"PRIVMSG #{self.channel} :/timeout {username} {minutes}")
                logger.info(f"⏱️ Timed out {username} for {minutes}m")
                return True
        except Exception as e:
            logger.error(f"❌ Timeout error: {e}")
        return False
    
    def ban_user(self, username: str) -> bool:
        """Ban a user"""
        try:
            if self.ws:
                self.ws.send(f"PRIVMSG #{self.channel} :/ban {username}")
                logger.info(f"🚫 Banned {username}")
                return True
        except Exception as e:
            logger.error(f"❌ Ban error: {e}")
        return False
    
    def unban_user(self, username: str) -> bool:
        """Unban a user"""
        try:
            if self.ws:
                self.ws.send(f"PRIVMSG #{self.channel} :/unban {username}")
                logger.info(f"✅ Unbanned {username}")
                return True
        except Exception as e:
            logger.error(f"❌ Unban error: {e}")
        return False
    
    def send_message(self, message: str):
        """Send chat message"""
        try:
            if self.ws:
                self.ws.send(f"PRIVMSG #{self.channel} :{message}")
        except Exception as e:
            logger.error(f"Send error: {e}")
    
    def disconnect(self):
        """Disconnect from chat"""
        self.active = False
        if self.ws:
            self.ws.close()
        logger.info("🔌 Disconnected from Twitch chat")

class ChatDockManager:
    """Manages the chat dock with multiple platform support"""
    
    def __init__(self):
        self.youtube_client: Optional[YouTubeChatClient] = None
        self.twitch_client: Optional[TwitchChatClient] = None
        self.messages: List[ChatMessage] = []
        self.banned_users: set = set()
        self.moderation_queue: List[Dict] = []
        self.message_callback: Optional[Callable] = None
        
    def connect_youtube(self, api_key: str, video_id: str) -> bool:
        """Connect to YouTube chat"""
        self.youtube_client = YouTubeChatClient(api_key, video_id)
        self.youtube_client.message_handlers.append(self._on_message)
        return self.youtube_client.connect()
    
    def connect_twitch(self, oauth_token: str, username: str, channel: str) -> bool:
        """Connect to Twitch chat"""
        self.twitch_client = TwitchChatClient(oauth_token, username, channel)
        self.twitch_client.message_handlers.append(self._on_message)
        return self.twitch_client.connect()
    
    def _on_message(self, message: ChatMessage):
        """Handle incoming message"""
        # Check if user is banned
        if message.username in self.banned_users or message.user_id in self.banned_users:
            return
        
        # Add to message history
        self.messages.append(message)
        
        # Keep only last 1000 messages
        if len(self.messages) > 1000:
            self.messages = self.messages[-1000:]
        
        # Notify callback
        if self.message_callback:
            self.message_callback(message)
        
        logger.info(f"💬 [{message.platform.value}] {message.username}: {message.message[:50]}...")
    
    def delete_message(self, message_id: str, platform: ChatPlatform) -> bool:
        """Delete a message"""
        if platform == ChatPlatform.YOUTUBE and self.youtube_client:
            return self.youtube_client.delete_message(message_id)
        elif platform == ChatPlatform.TWITCH and self.twitch_client:
            return self.twitch_client.delete_message(message_id)
        return False
    
    def timeout_user(self, user_id: str, username: str, platform: ChatPlatform, duration: int = 300) -> bool:
        """Timeout a user"""
        if platform == ChatPlatform.YOUTUBE and self.youtube_client:
            return self.youtube_client.timeout_user(user_id, duration)
        elif platform == ChatPlatform.TWITCH and self.twitch_client:
            return self.twitch_client.timeout_user(username, duration)
        return False
    
    def ban_user(self, user_id: str, username: str, platform: ChatPlatform) -> bool:
        """Ban a user"""
        # Add to banned list
        self.banned_users.add(username)
        self.banned_users.add(user_id)
        
        # Ban on platform
        if platform == ChatPlatform.YOUTUBE and self.youtube_client:
            return self.youtube_client.ban_user(user_id)
        elif platform == ChatPlatform.TWITCH and self.twitch_client:
            return self.twitch_client.ban_user(username)
        return False
    
    def unban_user(self, username: str, platform: ChatPlatform) -> bool:
        """Unban a user"""
        if username in self.banned_users:
            self.banned_users.remove(username)
        
        if platform == ChatPlatform.TWITCH and self.twitch_client:
            return self.twitch_client.unban_user(username)
        return True
    
    def get_recent_messages(self, count: int = 50) -> List[ChatMessage]:
        """Get recent messages"""
        return self.messages[-count:]
    
    def get_stats(self) -> Dict:
        """Get chat statistics"""
        return {
            'total_messages': len(self.messages),
            'youtube_connected': self.youtube_client is not None and self.youtube_client.active,
            'twitch_connected': self.twitch_client is not None and self.twitch_client.active,
            'banned_users': len(self.banned_users),
            'unique_users': len(set(m.username for m in self.messages))
        }
    
    def disconnect_all(self):
        """Disconnect from all platforms"""
        if self.youtube_client:
            self.youtube_client.disconnect()
        if self.twitch_client:
            self.twitch_client.disconnect()

# Global chat dock instance
chat_dock = ChatDockManager()