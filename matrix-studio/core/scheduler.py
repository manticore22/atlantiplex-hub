from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from datetime import datetime, timedelta
import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import json

logger = logging.getLogger(__name__)

@dataclass
class ScheduleData:
    """Schedule data structure"""
    id: str
    title: str
    description: str
    platforms: List[str]
    scheduled_start: datetime
    duration_minutes: int
    recurrence_type: str  # 'none', 'daily', 'weekly', 'monthly'
    recurrence_data: Dict = None
    thumbnail_path: str = None
    is_active: bool = True
    notification_sent: bool = False
    reminder_minutes: int = 15  # Minutes before stream to send reminder
    
    def __post_init__(self):
        if self.recurrence_data is None:
            self.recurrence_data = {}

class StreamScheduler:
    """Advanced stream scheduling system"""
    
    def __init__(self, app=None):
        self.scheduler = AsyncIOScheduler()
        self.schedules = {}
        self.notification_handlers = []
        self.app = app
        
        # Start scheduler (with error handling)
        try:
            self.scheduler.start()
        except RuntimeError as e:
            if "no running event loop" in str(e):
                logger.warning("No event loop running, scheduler will be started later")
            else:
                raise
        
        # Add job to check for upcoming streams
        self.scheduler.add_job(
            self._check_upcoming_streams,
            'interval',
            minutes=1,
            id='check_upcoming_streams'
        )
    
    def add_notification_handler(self, handler):
        """Add a notification handler for reminders"""
        self.notification_handlers.append(handler)
    
    async def _check_upcoming_streams(self):
        """Check for upcoming streams and send notifications"""
        now = datetime.utcnow()
        
        for schedule_id, schedule in self.schedules.items():
            if not schedule.is_active or schedule.notification_sent:
                continue
            
            # Check if stream is scheduled
            notification_time = schedule.scheduled_start - timedelta(minutes=schedule.reminder_minutes)
            
            if now >= notification_time and now < schedule.scheduled_start:
                await self._send_notification(schedule)
                schedule.notification_sent = True
    
    async def _send_notification(self, schedule: ScheduleData):
        """Send notification for scheduled stream"""
        try:
            notification_data = {
                'type': 'stream_reminder',
                'schedule_id': schedule.id,
                'title': schedule.title,
                'scheduled_start': schedule.scheduled_start.isoformat(),
                'platforms': schedule.platforms,
                'description': schedule.description,
                'thumbnail_path': schedule.thumbnail_path
            }
            
            # Call all notification handlers
            for handler in self.notification_handlers:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(notification_data)
                    else:
                        handler(notification_data)
                except Exception as e:
                    logger.error(f"Error in notification handler: {e}")
            
            logger.info(f"Sent notification for stream: {schedule.title}")
            
        except Exception as e:
            logger.error(f"Failed to send notification for schedule {schedule.id}: {e}")
    
    def add_schedule(self, schedule_data: Dict) -> str:
        """Add a new stream schedule"""
        try:
            # Create ScheduleData object
            schedule = ScheduleData(
                id=schedule_data.get('id'),
                title=schedule_data['title'],
                description=schedule_data.get('description', ''),
                platforms=schedule_data['platforms'],
                scheduled_start=datetime.fromisoformat(
                    schedule_data['scheduled_start'].replace('Z', '+00:00')
                ),
                duration_minutes=schedule_data.get('duration_minutes', 60),
                recurrence_type=schedule_data.get('recurrence_type', 'none'),
                recurrence_data=schedule_data.get('recurrence_data', {}),
                thumbnail_path=schedule_data.get('thumbnail_path'),
                reminder_minutes=schedule_data.get('reminder_minutes', 15)
            )
            
            self.schedules[schedule.id] = schedule
            
            # Schedule the stream
            self._schedule_stream(schedule)
            
            logger.info(f"Added schedule: {schedule.title} at {schedule.scheduled_start}")
            return schedule.id
            
        except Exception as e:
            logger.error(f"Failed to add schedule: {e}")
            raise
    
    def _schedule_stream(self, schedule: ScheduleData):
        """Schedule a stream based on its data"""
        try:
            # Remove existing job if present
            job_id = f"stream_{schedule.id}"
            if self.scheduler.get_job(job_id):
                self.scheduler.remove_job(job_id)
            
            # Determine trigger based on recurrence
            if schedule.recurrence_type == 'none':
                trigger = DateTrigger(run_date=schedule.scheduled_start)
            elif schedule.recurrence_type == 'daily':
                trigger = CronTrigger(
                    hour=schedule.scheduled_start.hour,
                    minute=schedule.scheduled_start.minute
                )
            elif schedule.recurrence_type == 'weekly':
                trigger = CronTrigger(
                    day_of_week=schedule.scheduled_start.weekday(),
                    hour=schedule.scheduled_start.hour,
                    minute=schedule.scheduled_start.minute
                )
            elif schedule.recurrence_type == 'monthly':
                trigger = CronTrigger(
                    day=schedule.scheduled_start.day,
                    hour=schedule.scheduled_start.hour,
                    minute=schedule.scheduled_start.minute
                )
            else:
                trigger = DateTrigger(run_date=schedule.scheduled_start)
            
            # Add job to scheduler
            self.scheduler.add_job(
                self._execute_scheduled_stream,
                trigger,
                args=[schedule],
                id=job_id,
                replace_existing=True
            )
            
            logger.info(f"Scheduled stream {schedule.title} for {schedule.scheduled_start}")
            
        except Exception as e:
            logger.error(f"Failed to schedule stream {schedule.id}: {e}")
    
    async def _execute_scheduled_stream(self, schedule: ScheduleData):
        """Execute a scheduled stream"""
        try:
            logger.info(f"Executing scheduled stream: {schedule.title}")
            
            # Reset notification for next occurrence if recurring
            if schedule.recurrence_type != 'none':
                schedule.notification_sent = False
            
            # Call stream execution handler
            for handler in self.notification_handlers:
                if hasattr(handler, '__self__') and hasattr(handler.__self__, 'start_scheduled_stream'):
                    try:
                        if asyncio.iscoroutinefunction(handler):
                            await handler.__self__.start_scheduled_stream(schedule)
                        else:
                            handler.__self__.start_scheduled_stream(schedule)
                    except Exception as e:
                        logger.error(f"Error executing scheduled stream: {e}")
                        break
            
            logger.info(f"Successfully started scheduled stream: {schedule.title}")
            
        except Exception as e:
            logger.error(f"Failed to execute scheduled stream {schedule.id}: {e}")
    
    def update_schedule(self, schedule_id: str, updates: Dict) -> bool:
        """Update an existing schedule"""
        try:
            if schedule_id not in self.schedules:
                return False
            
            schedule = self.schedules[schedule_id]
            
            # Update fields
            for key, value in updates.items():
                if hasattr(schedule, key):
                    if key == 'scheduled_start' and isinstance(value, str):
                        setattr(schedule, key, datetime.fromisoformat(value.replace('Z', '+00:00')))
                    else:
                        setattr(schedule, key, value)
            
            # Reschedule
            self._schedule_stream(schedule)
            
            logger.info(f"Updated schedule: {schedule.title}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update schedule {schedule_id}: {e}")
            return False
    
    def delete_schedule(self, schedule_id: str) -> bool:
        """Delete a schedule"""
        try:
            if schedule_id not in self.schedules:
                return False
            
            # Remove from schedules
            del self.schedules[schedule_id]
            
            # Remove job from scheduler
            job_id = f"stream_{schedule_id}"
            if self.scheduler.get_job(job_id):
                self.scheduler.remove_job(job_id)
            
            logger.info(f"Deleted schedule: {schedule_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete schedule {schedule_id}: {e}")
            return False
    
    def get_schedule(self, schedule_id: str) -> Optional[ScheduleData]:
        """Get a specific schedule"""
        return self.schedules.get(schedule_id)
    
    def get_all_schedules(self) -> List[ScheduleData]:
        """Get all schedules"""
        return list(self.schedules.values())
    
    def get_upcoming_schedules(self, hours: int = 24) -> List[ScheduleData]:
        """Get schedules within next X hours"""
        now = datetime.utcnow()
        end_time = now + timedelta(hours=hours)
        
        upcoming = []
        for schedule in self.schedules.values():
            if schedule.is_active and now <= schedule.scheduled_start <= end_time:
                upcoming.append(schedule)
        
        return sorted(upcoming, key=lambda x: x.scheduled_start)
    
    def get_active_schedules(self) -> List[ScheduleData]:
        """Get all active schedules"""
        return [s for s in self.schedules.values() if s.is_active]
    
    def toggle_schedule(self, schedule_id: str) -> bool:
        """Toggle a schedule active/inactive"""
        try:
            if schedule_id not in self.schedules:
                return False
            
            schedule = self.schedules[schedule_id]
            schedule.is_active = not schedule.is_active
            
            if not schedule.is_active:
                # Remove job if deactivating
                job_id = f"stream_{schedule_id}"
                if self.scheduler.get_job(job_id):
                    self.scheduler.remove_job(job_id)
            else:
                # Reschedule if activating
                self._schedule_stream(schedule)
            
            logger.info(f"Toggled schedule {schedule_id}: {'active' if schedule.is_active else 'inactive'}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to toggle schedule {schedule_id}: {e}")
            return False
    
    def create_recurring_schedule(
        self,
        base_schedule: Dict,
        recurrence_type: str,
        occurrences: int = None,
        end_date: datetime = None
    ) -> List[str]:
        """Create recurring schedules"""
        try:
            schedules_created = []
            base_time = datetime.fromisoformat(
                base_schedule['scheduled_start'].replace('Z', '+00:00')
            )
            
            current_time = base_time
            count = 0
            
            while True:
                # Check termination conditions
                if occurrences and count >= occurrences:
                    break
                if end_date and current_time > end_date:
                    break
                
                # Create schedule for this occurrence
                schedule_data = base_schedule.copy()
                schedule_data['scheduled_start'] = current_time.isoformat()
                schedule_data['recurrence_type'] = 'none'  # Individual schedules are non-recurring
                schedule_data['id'] = f"{base_schedule.get('id', '')}_{count}"
                
                schedule_id = self.add_schedule(schedule_data)
                schedules_created.append(schedule_id)
                
                # Calculate next occurrence
                if recurrence_type == 'daily':
                    current_time += timedelta(days=1)
                elif recurrence_type == 'weekly':
                    current_time += timedelta(weeks=1)
                elif recurrence_type == 'monthly':
                    current_time += timedelta(days=30)  # Approximate month
                
                count += 1
                
                # Safety limit
                if count >= 100:
                    break
            
            logger.info(f"Created {len(schedules_created)} recurring schedules")
            return schedules_created
            
        except Exception as e:
            logger.error(f"Failed to create recurring schedules: {e}")
            return []
    
    def get_schedule_conflicts(self, schedule_data: Dict) -> List[ScheduleData]:
        """Check for scheduling conflicts"""
        try:
            new_start = datetime.fromisoformat(
                schedule_data['scheduled_start'].replace('Z', '+00:00')
            )
            duration = schedule_data.get('duration_minutes', 60)
            new_end = new_start + timedelta(minutes=duration)
            
            conflicts = []
            
            for schedule in self.schedules.values():
                if not schedule.is_active:
                    continue
                
                existing_start = schedule.scheduled_start
                existing_end = existing_start + timedelta(minutes=schedule.duration_minutes)
                
                # Check for overlap
                if (new_start < existing_end and new_end > existing_start):
                    conflicts.append(schedule)
            
            return conflicts
            
        except Exception as e:
            logger.error(f"Failed to check schedule conflicts: {e}")
            return []
    
    def export_schedules(self) -> Dict:
        """Export all schedules"""
        try:
            export_data = {
                'schedules': {},
                'exported_at': datetime.utcnow().isoformat(),
                'version': '1.0'
            }
            
            for schedule_id, schedule in self.schedules.items():
                schedule_dict = asdict(schedule)
                schedule_dict['scheduled_start'] = schedule.scheduled_start.isoformat()
                export_data['schedules'][schedule_id] = schedule_dict
            
            return export_data
            
        except Exception as e:
            logger.error(f"Failed to export schedules: {e}")
            return {}
    
    def import_schedules(self, import_data: Dict) -> List[str]:
        """Import schedules from export data"""
        try:
            imported_schedules = []
            
            for schedule_id, schedule_dict in import_data.get('schedules', {}).items():
                try:
                    schedule_id = self.add_schedule(schedule_dict)
                    imported_schedules.append(schedule_id)
                except Exception as e:
                    logger.error(f"Failed to import schedule {schedule_id}: {e}")
            
            logger.info(f"Imported {len(imported_schedules)} schedules")
            return imported_schedules
            
        except Exception as e:
            logger.error(f"Failed to import schedules: {e}")
            return []
    
    def get_scheduler_stats(self) -> Dict:
        """Get scheduler statistics"""
        try:
            now = datetime.utcnow()
            
            stats = {
                'total_schedules': len(self.schedules),
                'active_schedules': len([s for s in self.schedules.values() if s.is_active]),
                'scheduled_jobs': len(self.scheduler.get_jobs()),
                'upcoming_24h': len(self.get_upcoming_schedules(24)),
                'upcoming_7d': len(self.get_upcoming_schedules(168)),  # 7 days
                'recurrence_types': {},
                'next_stream': None
            }
            
            # Count recurrence types
            for schedule in self.schedules.values():
                recurrence = schedule.recurrence_type
                if recurrence not in stats['recurrence_types']:
                    stats['recurrence_types'][recurrence] = 0
                stats['recurrence_types'][recurrence] += 1
            
            # Find next stream
            upcoming = self.get_upcoming_schedules(168)
            if upcoming:
                stats['next_stream'] = {
                    'id': upcoming[0].id,
                    'title': upcoming[0].title,
                    'scheduled_start': upcoming[0].scheduled_start.isoformat()
                }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get scheduler stats: {e}")
            return {}