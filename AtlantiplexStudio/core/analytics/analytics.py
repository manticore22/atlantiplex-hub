import requests
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import asyncio

logger = logging.getLogger(__name__)

@dataclass
class StreamMetrics:
    """Stream analytics data structure"""
    platform: str
    stream_id: str
    timestamp: datetime
    viewer_count: int = 0
    peak_viewers: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    revenue: float = 0.0
    watch_time_minutes: int = 0
    new_subscribers: int = 0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary with ISO timestamp"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

class StreamAnalytics:
    """Stream analytics and monitoring system"""
    
    def __init__(self):
        self.metrics_storage = {}  # In production, use a database
        self.active_streams = {}
        self.platform_clients = {}
        
    def add_platform_client(self, platform: str, client):
        """Add a platform client for fetching analytics"""
        self.platform_clients[platform] = client
    
    async def start_monitoring(self, stream_id: str, platforms: List[str], interval: int = 30):
        """Start monitoring analytics for a stream"""
        try:
            self.active_streams[stream_id] = {
                'platforms': platforms,
                'interval': interval,
                'start_time': datetime.utcnow(),
                'metrics': []
            }
            
            # Start monitoring task
            asyncio.create_task(self._monitor_stream(stream_id))
            
            logger.info(f"Started monitoring stream {stream_id} on platforms: {platforms}")
            
        except Exception as e:
            logger.error(f"Failed to start monitoring stream {stream_id}: {e}")
    
    async def stop_monitoring(self, stream_id: str):
        """Stop monitoring analytics for a stream"""
        try:
            if stream_id in self.active_streams:
                del self.active_streams[stream_id]
                logger.info(f"Stopped monitoring stream {stream_id}")
            
        except Exception as e:
            logger.error(f"Failed to stop monitoring stream {stream_id}: {e}")
    
    async def _monitor_stream(self, stream_id: str):
        """Monitor stream analytics continuously"""
        try:
            while stream_id in self.active_streams:
                stream_data = self.active_streams[stream_id]
                
                for platform in stream_data['platforms']:
                    try:
                        metrics = await self._fetch_platform_metrics(platform, stream_id)
                        if metrics:
                            self._store_metrics(stream_id, metrics)
                            
                    except Exception as e:
                        logger.error(f"Failed to fetch {platform} metrics for stream {stream_id}: {e}")
                
                # Wait for next interval
                await asyncio.sleep(stream_data['interval'])
                
        except Exception as e:
            logger.error(f"Error monitoring stream {stream_id}: {e}")
    
    async def _fetch_platform_metrics(self, platform: str, stream_id: str) -> Optional[StreamMetrics]:
        """Fetch metrics from a specific platform"""
        try:
            if platform == 'youtube' and platform in self.platform_clients:
                return await self._fetch_youtube_metrics(stream_id)
            elif platform == 'twitch' and platform in self.platform_clients:
                return await self._fetch_twitch_metrics(stream_id)
            elif platform == 'facebook' and platform in self.platform_clients:
                return await self._fetch_facebook_metrics(stream_id)
            elif platform == 'linkedin' and platform in self.platform_clients:
                return await self._fetch_linkedin_metrics(stream_id)
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching {platform} metrics: {e}")
            return None
    
    async def _fetch_youtube_metrics(self, stream_id: str) -> Optional[StreamMetrics]:
        """Fetch YouTube stream metrics"""
        try:
            client = self.platform_clients.get('youtube')
            if not client:
                return None
            
            # Get broadcast analytics
            broadcast_data = client.get_broadcast_analytics(stream_id)
            
            if not broadcast_data:
                return None
            
            # Parse statistics
            stats = broadcast_data.get('statistics', {})
            
            return StreamMetrics(
                platform='youtube',
                stream_id=stream_id,
                timestamp=datetime.utcnow(),
                viewer_count=int(stats.get('concurrentViewers', 0)),
                peak_viewers=int(stats.get('peakConcurrentViewers', 0)),
                likes=int(stats.get('likeCount', 0)),
                comments=int(stats.get('commentCount', 0))
            )
            
        except Exception as e:
            logger.error(f"Error fetching YouTube metrics: {e}")
            return None
    
    async def _fetch_twitch_metrics(self, stream_id: str) -> Optional[StreamMetrics]:
        """Fetch Twitch stream metrics"""
        try:
            client = self.platform_clients.get('twitch')
            if not client:
                return None
            
            # Get stream info
            stream_info = client.get_stream_info()
            
            if not stream_info:
                return None
            
            return StreamMetrics(
                platform='twitch',
                stream_id=stream_id,
                timestamp=datetime.utcnow(),
                viewer_count=int(stream_info.get('viewer_count', 0)),
                likes=int(stream_info.get('follower_count', 0))  # Approximate likes as followers
            )
            
        except Exception as e:
            logger.error(f"Error fetching Twitch metrics: {e}")
            return None
    
    async def _fetch_facebook_metrics(self, stream_id: str) -> Optional[StreamMetrics]:
        """Fetch Facebook Live metrics"""
        try:
            # In a real implementation, this would use Facebook Graph API
            # For now, return mock data
            return StreamMetrics(
                platform='facebook',
                stream_id=stream_id,
                timestamp=datetime.utcnow(),
                viewer_count=100,  # Mock data
                likes=25,
                comments=10,
                shares=5
            )
            
        except Exception as e:
            logger.error(f"Error fetching Facebook metrics: {e}")
            return None
    
    async def _fetch_linkedin_metrics(self, stream_id: str) -> Optional[StreamMetrics]:
        """Fetch LinkedIn Live metrics"""
        try:
            # In a real implementation, this would use LinkedIn API
            # For now, return mock data
            return StreamMetrics(
                platform='linkedin',
                stream_id=stream_id,
                timestamp=datetime.utcnow(),
                viewer_count=50,  # Mock data
                likes=15,
                comments=8,
                shares=3
            )
            
        except Exception as e:
            logger.error(f"Error fetching LinkedIn metrics: {e}")
            return None
    
    def _store_metrics(self, stream_id: str, metrics: StreamMetrics):
        """Store metrics for a stream"""
        try:
            if stream_id not in self.metrics_storage:
                self.metrics_storage[stream_id] = []
            
            self.metrics_storage[stream_id].append(metrics.to_dict())
            
            # Keep only last 1000 data points to prevent memory issues
            if len(self.metrics_storage[stream_id]) > 1000:
                self.metrics_storage[stream_id] = self.metrics_storage[stream_id][-1000:]
                
        except Exception as e:
            logger.error(f"Error storing metrics for stream {stream_id}: {e}")
    
    def get_stream_metrics(self, stream_id: str, hours: int = 24) -> List[Dict]:
        """Get metrics for a stream within the last N hours"""
        try:
            if stream_id not in self.metrics_storage:
                return []
            
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            filtered_metrics = []
            
            for metric in self.metrics_storage[stream_id]:
                metric_time = datetime.fromisoformat(metric['timestamp'].replace('Z', '+00:00'))
                if metric_time >= cutoff_time:
                    filtered_metrics.append(metric)
            
            return sorted(filtered_metrics, key=lambda x: x['timestamp'])
            
        except Exception as e:
            logger.error(f"Error getting metrics for stream {stream_id}: {e}")
            return []
    
    def get_aggregated_metrics(self, stream_id: str) -> Dict:
        """Get aggregated metrics for a stream"""
        try:
            if stream_id not in self.metrics_storage:
                return {}
            
            metrics = self.metrics_storage[stream_id]
            if not metrics:
                return {}
            
            # Aggregate by platform
            platform_data = {}
            
            for metric in metrics:
                platform = metric['platform']
                if platform not in platform_data:
                    platform_data[platform] = {
                        'total_viewers': 0,
                        'peak_viewers': 0,
                        'total_likes': 0,
                        'total_comments': 0,
                        'total_shares': 0,
                        'data_points': 0
                    }
                
                data = platform_data[platform]
                data['total_viewers'] += metric['viewer_count']
                data['peak_viewers'] = max(data['peak_viewers'], metric['viewer_count'])
                data['total_likes'] += metric['likes']
                data['total_comments'] += metric['comments']
                data['total_shares'] += metric['shares']
                data['data_points'] += 1
            
            # Calculate averages and final stats
            result = {
                'stream_id': stream_id,
                'platforms': {},
                'total_viewers': 0,
                'total_likes': 0,
                'total_comments': 0,
                'total_shares': 0
            }
            
            for platform, data in platform_data.items():
                avg_viewers = data['total_viewers'] / max(data['data_points'], 1)
                
                result['platforms'][platform] = {
                    'avg_viewers': round(avg_viewers, 2),
                    'peak_viewers': data['peak_viewers'],
                    'total_likes': data['total_likes'],
                    'total_comments': data['total_comments'],
                    'total_shares': data['total_shares'],
                    'data_points': data['data_points']
                }
                
                result['total_viewers'] += data['total_viewers']
                result['total_likes'] += data['total_likes']
                result['total_comments'] += data['total_comments']
                result['total_shares'] += data['total_shares']
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting aggregated metrics for stream {stream_id}: {e}")
            return {}
    
    def get_realtime_metrics(self, stream_id: str) -> Dict:
        """Get real-time metrics for a stream"""
        try:
            if stream_id not in self.metrics_storage:
                return {}
            
            metrics = self.metrics_storage[stream_id]
            if not metrics:
                return {}
            
            # Get the latest metrics
            latest_metrics = {}
            
            for metric in reversed(metrics):
                platform = metric['platform']
                if platform not in latest_metrics:
                    latest_metrics[platform] = metric
                    if len(latest_metrics) >= 4:  # Max 4 platforms
                        break
            
            # Calculate real-time totals
            total_viewers = sum(metric['viewer_count'] for metric in latest_metrics.values())
            
            return {
                'stream_id': stream_id,
                'timestamp': datetime.utcnow().isoformat(),
                'total_viewers': total_viewers,
                'platforms': latest_metrics
            }
            
        except Exception as e:
            logger.error(f"Error getting real-time metrics for stream {stream_id}: {e}")
            return {}
    
    def get_comparison_report(self, stream_id1: str, stream_id2: str) -> Dict:
        """Compare metrics between two streams"""
        try:
            metrics1 = self.get_aggregated_metrics(stream_id1)
            metrics2 = self.get_aggregated_metrics(stream_id2)
            
            if not metrics1 or not metrics2:
                return {}
            
            comparison = {
                'stream1': {'id': stream_id1, **metrics1},
                'stream2': {'id': stream_id2, **metrics2},
                'differences': {}
            }
            
            # Calculate differences
            for metric in ['total_viewers', 'total_likes', 'total_comments', 'total_shares']:
                val1 = metrics1.get(metric, 0)
                val2 = metrics2.get(metric, 0)
                
                if val1 > 0:
                    percentage_change = ((val2 - val1) / val1) * 100
                    comparison['differences'][metric] = {
                        'stream1': val1,
                        'stream2': val2,
                        'absolute_change': val2 - val1,
                        'percentage_change': round(percentage_change, 2)
                    }
            
            return comparison
            
        except Exception as e:
            logger.error(f"Error comparing streams {stream_id1} and {stream_id2}: {e}")
            return {}
    
    def export_metrics(self, stream_id: str, format: str = 'json') -> Any:
        """Export stream metrics in specified format"""
        try:
            if stream_id not in self.metrics_storage:
                return None
            
            metrics = self.metrics_storage[stream_id]
            
            if format == 'json':
                return {
                    'stream_id': stream_id,
                    'exported_at': datetime.utcnow().isoformat(),
                    'metrics': metrics
                }
            elif format == 'csv':
                # Convert to CSV format
                import csv
                from io import StringIO
                
                output = StringIO()
                writer = csv.writer(output)
                
                # Write header
                writer.writerow([
                    'timestamp', 'platform', 'viewer_count', 'peak_viewers',
                    'likes', 'comments', 'shares', 'revenue'
                ])
                
                # Write data
                for metric in metrics:
                    writer.writerow([
                        metric['timestamp'],
                        metric['platform'],
                        metric['viewer_count'],
                        metric['peak_viewers'],
                        metric['likes'],
                        metric['comments'],
                        metric['shares'],
                        metric['revenue']
                    ])
                
                return output.getvalue()
            
            return None
            
        except Exception as e:
            logger.error(f"Error exporting metrics for stream {stream_id}: {e}")
            return None
    
    def get_dashboard_data(self, user_id: str = None) -> Dict:
        """Get dashboard data for analytics display"""
        try:
            dashboard_data = {
                'total_streams': len(self.active_streams),
                'active_streams': len(self.active_streams),
                'total_viewers': 0,
                'peak_viewers': 0,
                'platforms': {},
                'recent_activity': []
            }
            
            # Aggregate data from all active streams
            for stream_id, stream_data in self.active_streams.items():
                realtime_metrics = self.get_realtime_metrics(stream_id)
                
                if realtime_metrics:
                    dashboard_data['total_viewers'] += realtime_metrics['total_viewers']
                    dashboard_data['peak_viewers'] = max(
                        dashboard_data['peak_viewers'],
                        realtime_metrics['total_viewers']
                    )
                    
                    # Count platforms
                    for platform in stream_data['platforms']:
                        if platform not in dashboard_data['platforms']:
                            dashboard_data['platforms'][platform] = 0
                        dashboard_data['platforms'][platform] += 1
            
            # Get recent activity
            recent_activity = []
            
            for stream_id, metrics_list in self.metrics_storage.items():
                if metrics_list:
                    latest_metric = metrics_list[-1]
                    recent_activity.append({
                        'stream_id': stream_id,
                        'platform': latest_metric['platform'],
                        'timestamp': latest_metric['timestamp'],
                        'viewer_count': latest_metric['viewer_count']
                    })
            
            # Sort by timestamp and get last 10
            recent_activity.sort(key=lambda x: x['timestamp'], reverse=True)
            dashboard_data['recent_activity'] = recent_activity[:10]
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Error getting dashboard data: {e}")
            return {}
    
    def cleanup_old_metrics(self, days: int = 30):
        """Clean up metrics older than specified days"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(days=days)
            
            for stream_id in list(self.metrics_storage.keys()):
                metrics = self.metrics_storage[stream_id]
                filtered_metrics = []
                
                for metric in metrics:
                    metric_time = datetime.fromisoformat(metric['timestamp'].replace('Z', '+00:00'))
                    if metric_time >= cutoff_time:
                        filtered_metrics.append(metric)
                
                if filtered_metrics:
                    self.metrics_storage[stream_id] = filtered_metrics
                else:
                    del self.metrics_storage[stream_id]
            
            logger.info(f"Cleaned up metrics older than {days} days")
            
        except Exception as e:
            logger.error(f"Error cleaning up old metrics: {e}")