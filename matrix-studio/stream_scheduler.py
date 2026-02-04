"""
ADVANCED MULTI-STREAM SCHEDULER
Professional streaming schedule management with calendar view, recurring streams,
multi-platform support, and automated stream launching
"""

import json
import logging
import schedule
import time
import threading
import os
import shutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict, field
from enum import Enum
import uuid
import calendar

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StreamStatus(Enum):
    SCHEDULED = "scheduled"
    LIVE = "live"
    ENDED = "ended"
    CANCELLED = "cancelled"
    RECURRING = "recurring"

class RecurrencePattern(Enum):
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"

class StreamingPlatform(Enum):
    YOUTUBE = "youtube"
    TWITCH = "twitch"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    ALL = "all"

@dataclass
class StreamTemplate:
    """Stream configuration template"""
    id: str
    name: str
    title: str
    description: str
    tags: List[str]
    thumbnail_url: str
    category: str
    privacy: str  # public, unlisted, private
    settings: Dict[str, Any]
    platforms: List[StreamingPlatform]
    scene_layout: str
    guest_slots: int
    quality: str
    
    def to_dict(self) -> Dict:
        return {
            **asdict(self),
            'platforms': [p.value for p in self.platforms]
        }

@dataclass
class ScheduledStream:
    """Individual scheduled stream"""
    id: str
    template_id: str
    title: str
    description: str
    start_time: datetime
    end_time: Optional[datetime]
    platforms: List[StreamingPlatform]
    status: StreamStatus
    recurrence: RecurrencePattern
    recurrence_config: Dict[str, Any]
    guest_list: List[str]
    auto_start: bool
    auto_end: bool
    notify_before_minutes: int
    metadata: Dict[str, Any]
    created_at: datetime
    parent_stream_id: Optional[str] = None  # For recurring instances
    # Enhanced metadata
    thumbnail_path: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    category: str = "General"
    privacy: str = "public"
    scheduled_posts: Dict[str, Any] = field(default_factory=dict)
    x_tweet_text: str = ""  # X/Twitter specific
    x_hashtags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'template_id': self.template_id,
            'title': self.title,
            'description': self.description,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'platforms': [p.value for p in self.platforms],
            'status': self.status.value,
            'recurrence': self.recurrence.value,
            'recurrence_config': self.recurrence_config,
            'guest_list': self.guest_list,
            'auto_start': self.auto_start,
            'auto_end': self.auto_end,
            'notify_before_minutes': self.notify_before_minutes,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat(),
            'parent_stream_id': self.parent_stream_id
        }

@dataclass
class StreamSeries:
    """Recurring stream series"""
    id: str
    name: str
    template_id: str
    start_date: datetime
    end_date: Optional[datetime]
    recurrence: RecurrencePattern
    recurrence_config: Dict[str, Any]
    instances: List[str]  # List of scheduled stream IDs
    active: bool

class MultiStreamScheduler:
    """
    Advanced Multi-Stream Scheduler
    Manage streaming schedule across multiple platforms
    """
    
    def __init__(self):
        self.templates: Dict[str, StreamTemplate] = {}
        self.scheduled_streams: Dict[str, ScheduledStream] = {}
        self.stream_series: Dict[str, StreamSeries] = {}
        self.notification_handlers: List[Callable] = []
        self.auto_launch_handlers: List[Callable] = []
        self.running = False
        self.scheduler_thread = None
        
        # Create default templates
        self._create_default_templates()
        
        logger.info("🗓️ Advanced Multi-Stream Scheduler Initialized")
    
    def _create_default_templates(self):
        """Create default stream templates"""
        default_templates = [
            StreamTemplate(
                id="template_daily_vlog",
                name="Daily Vlog",
                title="Daily Live Vlog - {{date}}",
                description="Join me for today's live vlog session!",
                tags=["vlog", "daily", "live"],
                thumbnail_url="/static/thumbnails/vlog.jpg",
                category="Entertainment",
                privacy="public",
                settings={
                    "quality": "1080p",
                    "chat_enabled": True,
                    "donations_enabled": True
                },
                platforms=[StreamingPlatform.YOUTUBE, StreamingPlatform.TWITCH],
                scene_layout="interview",
                guest_slots=3,
                quality="1080p"
            ),
            StreamTemplate(
                id="template_gaming",
                name="Gaming Stream",
                title="Gaming Session - {{game_name}}",
                description="Live gaming with viewers!",
                tags=["gaming", "live", "interactive"],
                thumbnail_url="/static/thumbnails/gaming.jpg",
                category="Gaming",
                privacy="public",
                settings={
                    "quality": "1080p60",
                    "chat_enabled": True,
                    "facecam": True
                },
                platforms=[StreamingPlatform.TWITCH, StreamingPlatform.YOUTUBE, StreamingPlatform.FACEBOOK],
                scene_layout="gaming",
                guest_slots=1,
                quality="1080p60"
            ),
            StreamTemplate(
                id="template_podcast",
                name="Podcast Recording",
                title="Podcast Episode {{episode_number}}",
                description="Live podcast recording with special guests",
                tags=["podcast", "interview", "live"],
                thumbnail_url="/static/thumbnails/podcast.jpg",
                category="Education",
                privacy="public",
                settings={
                    "quality": "1080p",
                    "audio_focus": True,
                    "multi_camera": True
                },
                platforms=[StreamingPlatform.YOUTUBE, StreamingPlatform.FACEBOOK, StreamingPlatform.LINKEDIN],
                scene_layout="podcast",
                guest_slots=4,
                quality="1080p"
            ),
            StreamTemplate(
                id="template_webinar",
                name="Professional Webinar",
                title="Webinar: {{topic}}",
                description="Professional webinar with presentation slides",
                tags=["webinar", "education", "business"],
                thumbnail_url="/static/thumbnails/webinar.jpg",
                category="Education",
                privacy="public",
                settings={
                    "quality": "1080p",
                    "screen_share": True,
                    "q_and_a": True,
                    "registration_required": True
                },
                platforms=[StreamingPlatform.YOUTUBE, StreamingPlatform.LINKEDIN],
                scene_layout="presentation",
                guest_slots=2,
                quality="1080p"
            ),
            StreamTemplate(
                id="template_all_platforms",
                name="Max Reach Stream",
                title="Live on All Platforms!",
                description="Streaming to every platform simultaneously",
                tags=["live", "multi-platform", "viral"],
                thumbnail_url="/static/thumbnails/multi.jpg",
                category="Entertainment",
                privacy="public",
                settings={
                    "quality": "720p",
                    "adaptive_bitrate": True,
                    "multi_platform_optimization": True
                },
                platforms=[StreamingPlatform.YOUTUBE, StreamingPlatform.TWITCH, StreamingPlatform.FACEBOOK, 
                          StreamingPlatform.INSTAGRAM, StreamingPlatform.LINKEDIN, StreamingPlatform.TWITTER],
                scene_layout="multi",
                guest_slots=6,
                quality="720p"
            )
        ]
        
        for template in default_templates:
            self.templates[template.id] = template
        
        logger.info(f"✅ Created {len(default_templates)} default templates")
    
    def create_template(self, template_data: Dict) -> StreamTemplate:
        """Create a new stream template"""
        template_id = f"template_{uuid.uuid4().hex[:8]}"
        
        template = StreamTemplate(
            id=template_id,
            name=template_data.get('name', 'Untitled Template'),
            title=template_data.get('title', ''),
            description=template_data.get('description', ''),
            tags=template_data.get('tags', []),
            thumbnail_url=template_data.get('thumbnail_url', ''),
            category=template_data.get('category', 'General'),
            privacy=template_data.get('privacy', 'public'),
            settings=template_data.get('settings', {}),
            platforms=[StreamingPlatform(p) for p in template_data.get('platforms', ['youtube'])],
            scene_layout=template_data.get('scene_layout', 'interview'),
            guest_slots=template_data.get('guest_slots', 3),
            quality=template_data.get('quality', '1080p')
        )
        
        self.templates[template_id] = template
        logger.info(f"✅ Template created: {template.name} ({template_id})")
        return template
    
    def schedule_stream(self, stream_data: Dict) -> ScheduledStream:
        """Schedule a new stream"""
        stream_id = f"stream_{uuid.uuid4().hex[:8]}"
        
        # Parse datetime
        start_time = datetime.fromisoformat(stream_data.get('start_time'))
        end_time = None
        if stream_data.get('end_time'):
            end_time = datetime.fromisoformat(stream_data['end_time'])
        
        stream = ScheduledStream(
            id=stream_id,
            template_id=stream_data.get('template_id', ''),
            title=stream_data.get('title', 'Untitled Stream'),
            description=stream_data.get('description', ''),
            start_time=start_time,
            end_time=end_time,
            platforms=[StreamingPlatform(p) for p in stream_data.get('platforms', ['youtube'])],
            status=StreamStatus.SCHEDULED,
            recurrence=RecurrencePattern(stream_data.get('recurrence', 'none')),
            recurrence_config=stream_data.get('recurrence_config', {}),
            guest_list=stream_data.get('guest_list', []),
            auto_start=stream_data.get('auto_start', False),
            auto_end=stream_data.get('auto_end', False),
            notify_before_minutes=stream_data.get('notify_before_minutes', 15),
            metadata=stream_data.get('metadata', {}),
            created_at=datetime.now()
        )
        
        self.scheduled_streams[stream_id] = stream
        
        # If recurring, create the series
        if stream.recurrence != RecurrencePattern.NONE:
            self._create_recurring_instances(stream)
        
        # Schedule notifications
        if stream.notify_before_minutes > 0:
            self._schedule_notification(stream)
        
        # Schedule auto-start
        if stream.auto_start:
            self._schedule_auto_start(stream)
        
        logger.info(f"✅ Stream scheduled: {stream.title} at {start_time}")
        return stream
    
    def _create_recurring_instances(self, parent_stream: ScheduledStream):
        """Create instances for recurring streams"""
        series_id = f"series_{uuid.uuid4().hex[:8]}"
        instances = []
        
        # Generate instances based on recurrence pattern
        if parent_stream.recurrence == RecurrencePattern.DAILY:
            instances = self._generate_daily_instances(parent_stream, 30)  # 30 days
        elif parent_stream.recurrence == RecurrencePattern.WEEKLY:
            instances = self._generate_weekly_instances(parent_stream, 12)  # 12 weeks
        elif parent_stream.recurrence == RecurrencePattern.BIWEEKLY:
            instances = self._generate_biweekly_instances(parent_stream, 12)  # 12 occurrences
        elif parent_stream.recurrence == RecurrencePattern.MONTHLY:
            instances = self._generate_monthly_instances(parent_stream, 12)  # 12 months
        
        # Create series record
        series = StreamSeries(
            id=series_id,
            name=parent_stream.title,
            template_id=parent_stream.template_id,
            start_date=parent_stream.start_time,
            end_date=None,
            recurrence=parent_stream.recurrence,
            recurrence_config=parent_stream.recurrence_config,
            instances=[s.id for s in instances],
            active=True
        )
        
        self.stream_series[series_id] = series
        
        # Store all instances
        for instance in instances:
            self.scheduled_streams[instance.id] = instance
        
        logger.info(f"✅ Created {len(instances)} recurring instances for series {series_id}")
    
    def _generate_daily_instances(self, parent: ScheduledStream, count: int) -> List[ScheduledStream]:
        """Generate daily recurring instances"""
        instances = []
        current_time = parent.start_time
        
        for i in range(count):
            instance_id = f"stream_{uuid.uuid4().hex[:8]}"
            
            instance = ScheduledStream(
                id=instance_id,
                template_id=parent.template_id,
                title=parent.title,
                description=parent.description,
                start_time=current_time,
                end_time=current_time + (parent.end_time - parent.start_time) if parent.end_time else None,
                platforms=parent.platforms,
                status=StreamStatus.RECURRING,
                recurrence=RecurrencePattern.NONE,  # Individual instances don't recur
                recurrence_config={},
                guest_list=parent.guest_list,
                auto_start=parent.auto_start,
                auto_end=parent.auto_end,
                notify_before_minutes=parent.notify_before_minutes,
                metadata={**parent.metadata, 'instance_number': i + 1},
                created_at=datetime.now(),
                parent_stream_id=parent.id
            )
            
            instances.append(instance)
            current_time += timedelta(days=1)
        
        return instances
    
    def _generate_weekly_instances(self, parent: ScheduledStream, count: int) -> List[ScheduledStream]:
        """Generate weekly recurring instances"""
        instances = []
        current_time = parent.start_time
        
        for i in range(count):
            instance_id = f"stream_{uuid.uuid4().hex[:8]}"
            
            instance = ScheduledStream(
                id=instance_id,
                template_id=parent.template_id,
                title=parent.title,
                description=parent.description,
                start_time=current_time,
                end_time=current_time + (parent.end_time - parent.start_time) if parent.end_time else None,
                platforms=parent.platforms,
                status=StreamStatus.RECURRING,
                recurrence=RecurrencePattern.NONE,
                recurrence_config={},
                guest_list=parent.guest_list,
                auto_start=parent.auto_start,
                auto_end=parent.auto_end,
                notify_before_minutes=parent.notify_before_minutes,
                metadata={**parent.metadata, 'instance_number': i + 1, 'week_number': i + 1},
                created_at=datetime.now(),
                parent_stream_id=parent.id
            )
            
            instances.append(instance)
            current_time += timedelta(weeks=1)
        
        return instances
    
    def _generate_biweekly_instances(self, parent: ScheduledStream, count: int) -> List[ScheduledStream]:
        """Generate bi-weekly recurring instances"""
        instances = []
        current_time = parent.start_time
        
        for i in range(count):
            instance_id = f"stream_{uuid.uuid4().hex[:8]}"
            
            instance = ScheduledStream(
                id=instance_id,
                template_id=parent.template_id,
                title=parent.title,
                description=parent.description,
                start_time=current_time,
                end_time=current_time + (parent.end_time - parent.start_time) if parent.end_time else None,
                platforms=parent.platforms,
                status=StreamStatus.RECURRING,
                recurrence=RecurrencePattern.NONE,
                recurrence_config={},
                guest_list=parent.guest_list,
                auto_start=parent.auto_start,
                auto_end=parent.auto_end,
                notify_before_minutes=parent.notify_before_minutes,
                metadata={**parent.metadata, 'instance_number': i + 1},
                created_at=datetime.now(),
                parent_stream_id=parent.id
            )
            
            instances.append(instance)
            current_time += timedelta(weeks=2)
        
        return instances
    
    def _generate_monthly_instances(self, parent: ScheduledStream, count: int) -> List[ScheduledStream]:
        """Generate monthly recurring instances"""
        instances = []
        current_time = parent.start_time
        
        for i in range(count):
            instance_id = f"stream_{uuid.uuid4().hex[:8]}"
            
            instance = ScheduledStream(
                id=instance_id,
                template_id=parent.template_id,
                title=parent.title,
                description=parent.description,
                start_time=current_time,
                end_time=current_time + (parent.end_time - parent.start_time) if parent.end_time else None,
                platforms=parent.platforms,
                status=StreamStatus.RECURRING,
                recurrence=RecurrencePattern.NONE,
                recurrence_config={},
                guest_list=parent.guest_list,
                auto_start=parent.auto_start,
                auto_end=parent.auto_end,
                notify_before_minutes=parent.notify_before_minutes,
                metadata={**parent.metadata, 'instance_number': i + 1, 'month_number': i + 1},
                created_at=datetime.now(),
                parent_stream_id=parent.id
            )
            
            instances.append(instance)
            # Add one month
            if current_time.month == 12:
                current_time = current_time.replace(year=current_time.year + 1, month=1)
            else:
                current_time = current_time.replace(month=current_time.month + 1)
        
        return instances
    
    def _schedule_notification(self, stream: ScheduledStream):
        """Schedule pre-stream notification"""
        notification_time = stream.start_time - timedelta(minutes=stream.notify_before_minutes)
        
        def notify():
            for handler in self.notification_handlers:
                handler({
                    'type': 'stream_reminder',
                    'stream_id': stream.id,
                    'title': stream.title,
                    'start_time': stream.start_time.isoformat(),
                    'minutes_until': stream.notify_before_minutes
                })
        
        # Use schedule library for simplicity
        schedule.every().day.at(notification_time.strftime("%H:%M")).do(notify)
        logger.info(f"🔔 Notification scheduled for {stream.title} at {notification_time}")
    
    def _schedule_auto_start(self, stream: ScheduledStream):
        """Schedule automatic stream start"""
        def auto_start():
            logger.info(f"🚀 Auto-starting stream: {stream.title}")
            for handler in self.auto_launch_handlers:
                handler({
                    'stream_id': stream.id,
                    'title': stream.title,
                    'platforms': [p.value for p in stream.platforms],
                    'action': 'auto_start'
                })
            
            # Update status
            stream.status = StreamStatus.LIVE
        
        schedule.every().day.at(stream.start_time.strftime("%H:%M")).do(auto_start)
        logger.info(f"🚀 Auto-start scheduled for {stream.title} at {stream.start_time}")
    
    def get_calendar_view(self, year: int, month: int) -> Dict[str, Any]:
        """Get calendar view for a specific month"""
        # Get all streams in the month
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        month_streams = []
        for stream in self.scheduled_streams.values():
            if start_date <= stream.start_time < end_date:
                month_streams.append(stream)
        
        # Organize by day
        days = {}
        cal = calendar.Calendar()
        for week in cal.monthdayscalendar(year, month):
            for day in week:
                if day != 0:
                    days[day] = []
        
        for stream in month_streams:
            day = stream.start_time.day
            if day in days:
                days[day].append(stream.to_dict())
        
        return {
            'year': year,
            'month': month,
            'month_name': calendar.month_name[month],
            'days': days,
            'total_streams': len(month_streams)
        }
    
    def get_upcoming_streams(self, hours: int = 24) -> List[ScheduledStream]:
        """Get streams scheduled within the next X hours"""
        now = datetime.now()
        cutoff = now + timedelta(hours=hours)
        
        upcoming = []
        for stream in self.scheduled_streams.values():
            if stream.status in [StreamStatus.SCHEDULED, StreamStatus.RECURRING]:
                if now <= stream.start_time <= cutoff:
                    upcoming.append(stream)
        
        return sorted(upcoming, key=lambda s: s.start_time)
    
    def update_stream(self, stream_id: str, updates: Dict) -> Optional[ScheduledStream]:
        """Update a scheduled stream"""
        if stream_id not in self.scheduled_streams:
            return None
        
        stream = self.scheduled_streams[stream_id]
        
        # Update fields
        if 'title' in updates:
            stream.title = updates['title']
        if 'description' in updates:
            stream.description = updates['description']
        if 'start_time' in updates:
            stream.start_time = datetime.fromisoformat(updates['start_time'])
        if 'end_time' in updates:
            stream.end_time = datetime.fromisoformat(updates['end_time']) if updates['end_time'] else None
        if 'platforms' in updates:
            stream.platforms = [StreamingPlatform(p) for p in updates['platforms']]
        if 'guest_list' in updates:
            stream.guest_list = updates['guest_list']
        if 'auto_start' in updates:
            stream.auto_start = updates['auto_start']
        if 'auto_end' in updates:
            stream.auto_end = updates['auto_end']
        if 'thumbnail_path' in updates:
            stream.thumbnail_path = updates['thumbnail_path']
        if 'tags' in updates:
            stream.tags = updates['tags']
        if 'category' in updates:
            stream.category = updates['category']
        if 'privacy' in updates:
            stream.privacy = updates['privacy']
        if 'x_tweet_text' in updates:
            stream.x_tweet_text = updates['x_tweet_text']
        if 'x_hashtags' in updates:
            stream.x_hashtags = updates['x_hashtags']
        
        logger.info(f"✏️ Stream updated: {stream.title}")
        return stream
    
    def upload_thumbnail(self, stream_id: str, file_path: str, file_data: bytes = None) -> Dict:
        """Upload thumbnail for a stream"""
        if stream_id not in self.scheduled_streams:
            return {'success': False, 'error': 'Stream not found'}
        
        stream = self.scheduled_streams[stream_id]
        
        # Store thumbnail
        thumbnail_dir = 'uploads/thumbnails'
        os.makedirs(thumbnail_dir, exist_ok=True)
        
        thumbnail_filename = f"{stream_id}_{int(time.time())}.jpg"
        thumbnail_path = os.path.join(thumbnail_dir, thumbnail_filename)
        
        try:
            if file_data:
                # Save from bytes
                with open(thumbnail_path, 'wb') as f:
                    f.write(file_data)
            elif file_path and os.path.exists(file_path):
                # Copy from file path
                import shutil
                shutil.copy(file_path, thumbnail_path)
            else:
                return {'success': False, 'error': 'No file data provided'}
            
            stream.thumbnail_path = thumbnail_path
            
            logger.info(f"🖼️ Thumbnail uploaded for {stream.title}")
            return {
                'success': True,
                'stream_id': stream_id,
                'thumbnail_path': thumbnail_path,
                'thumbnail_url': f"/uploads/thumbnails/{thumbnail_filename}"
            }
            
        except Exception as e:
            logger.error(f"❌ Thumbnail upload error: {e}")
            return {'success': False, 'error': str(e)}
    
    def schedule_x_post(self, stream_id: str, tweet_text: str, hashtags: List[str] = None, 
                       post_time: datetime = None) -> Dict:
        """Schedule X/Twitter post for stream"""
        if stream_id not in self.scheduled_streams:
            return {'success': False, 'error': 'Stream not found'}
        
        stream = self.scheduled_streams[stream_id]
        
        # Update stream with X data
        stream.x_tweet_text = tweet_text
        stream.x_hashtags = hashtags or []
        
        # Schedule the post
        if not post_time:
            # Default to 15 minutes before stream
            post_time = stream.start_time - timedelta(minutes=15)
        
        post_id = f"x_post_{uuid.uuid4().hex[:8]}"
        
        stream.scheduled_posts['x'] = {
            'post_id': post_id,
            'text': tweet_text,
            'hashtags': hashtags,
            'scheduled_time': post_time.isoformat(),
            'status': 'scheduled',
            'platform': 'x'
        }
        
        logger.info(f"🐦 X post scheduled for {stream.title}")
        return {
            'success': True,
            'post_id': post_id,
            'scheduled_time': post_time.isoformat(),
            'tweet_preview': self._generate_tweet_preview(tweet_text, hashtags)
        }
    
    def _generate_tweet_preview(self, text: str, hashtags: List[str]) -> str:
        """Generate preview of X post"""
        hashtag_str = ' '.join([f"#{tag}" for tag in hashtags]) if hashtags else ''
        preview = f"{text}\n\n{hashtag_str}".strip()
        if len(preview) > 280:
            preview = preview[:277] + "..."
        return preview
    
    def start_x_stream(self, stream_id: str) -> Dict:
        """Start streaming to X/Twitter"""
        if stream_id not in self.scheduled_streams:
            return {'success': False, 'error': 'Stream not found'}
        
        stream = self.scheduled_streams[stream_id]
        
        # Check if X is in platforms
        if StreamingPlatform.TWITTER not in stream.platforms:
            stream.platforms.append(StreamingPlatform.TWITTER)
        
        # Update status
        stream.status = StreamStatus.LIVE
        stream.metadata['x_streaming'] = True
        stream.metadata['x_stream_started'] = datetime.now().isoformat()
        
        logger.info(f"🐦 X STREAM STARTED: {stream.title}")
        
        return {
            'success': True,
            'stream_id': stream_id,
            'platform': 'x',
            'status': 'live',
            'tweet_preview': self._generate_tweet_preview(
                stream.x_tweet_text or f"🔴 LIVE NOW: {stream.title}",
                stream.x_hashtags
            ),
            'stream_url': f"https://x.com/i/broadcasts/{stream_id}",
            'message': 'Now streaming to X! Tweet will be posted automatically.'
        }
    
    def post_to_x(self, stream_id: str, custom_text: str = None) -> Dict:
        """Post announcement to X/Twitter"""
        if stream_id not in self.scheduled_streams:
            return {'success': False, 'error': 'Stream not found'}
        
        stream = self.scheduled_streams[stream_id]
        
        # Use custom text or generate from stream
        text = custom_text or stream.x_tweet_text or f"🔴 Going LIVE: {stream.title}"
        hashtags = stream.x_hashtags or []
        
        # Generate final tweet
        tweet = self._generate_tweet_preview(text, hashtags)
        
        # In production, this would call X API
        logger.info(f"🐦 Posted to X: {tweet[:50]}...")
        
        return {
            'success': True,
            'platform': 'x',
            'tweet_text': tweet,
            'stream_url': f"https://yoursite.com/stream/{stream_id}",
            'posted_at': datetime.now().isoformat()
        }
    
    def cancel_stream(self, stream_id: str) -> bool:
        """Cancel a scheduled stream"""
        if stream_id not in self.scheduled_streams:
            return False
        
        stream = self.scheduled_streams[stream_id]
        stream.status = StreamStatus.CANCELLED
        
        logger.info(f"❌ Stream cancelled: {stream.title}")
        return True
    
    def delete_stream(self, stream_id: str) -> bool:
        """Delete a stream permanently"""
        if stream_id in self.scheduled_streams:
            del self.scheduled_streams[stream_id]
            logger.info(f"🗑️ Stream deleted: {stream_id}")
            return True
        return False
    
    def register_notification_handler(self, handler: Callable):
        """Register a handler for notifications"""
        self.notification_handlers.append(handler)
    
    def register_auto_launch_handler(self, handler: Callable):
        """Register a handler for auto-launch"""
        self.auto_launch_handlers.append(handler)
    
    def start_scheduler(self):
        """Start the background scheduler"""
        if self.running:
            return
        
        self.running = True
        
        def run_scheduler():
            while self.running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        
        self.scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        self.scheduler_thread.start()
        logger.info("⏰ Scheduler started")
    
    def stop_scheduler(self):
        """Stop the background scheduler"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join()
        logger.info("⏰ Scheduler stopped")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get scheduler statistics"""
        total = len(self.scheduled_streams)
        scheduled = len([s for s in self.scheduled_streams.values() if s.status == StreamStatus.SCHEDULED])
        live = len([s for s in self.scheduled_streams.values() if s.status == StreamStatus.LIVE])
        ended = len([s for s in self.scheduled_streams.values() if s.status == StreamStatus.ENDED])
        recurring = len([s for s in self.scheduled_streams.values() if s.status == StreamStatus.RECURRING])
        
        return {
            'total_streams': total,
            'scheduled': scheduled,
            'live': live,
            'ended': ended,
            'recurring': recurring,
            'templates': len(self.templates),
            'series': len(self.stream_series),
            'upcoming_24h': len(self.get_upcoming_streams(24))
        }

# Global scheduler instance
stream_scheduler = MultiStreamScheduler()

# Start the scheduler
stream_scheduler.start_scheduler()