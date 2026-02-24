import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Mic, Video, Monitor, Users, Settings, Zap, Clock, TrendingUp, Calendar, Globe, Wifi, Cpu } from 'lucide-react';

const StreamScheduler = ({ onSchedule, onEdit, onDelete, streams = [] }) => {
  const [viewMode, setViewMode] = useState('calendar'); // calendar, list, timeline
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [showScheduleForm, setShowScheduleForm] = useState(false);
  const [editingStream, setEditingStream] = useState(null);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    platforms: [],
    scheduledTime: '',
    duration: 60,
    quality: '1080p',
    isRecurring: false,
    recurringPattern: 'weekly',
    reminderTime: 15,
    privacy: 'public',
    tags: []
  });

  const calendarRef = useRef(null);

  useEffect(() => {
    // Generate calendar grid for selected month
    generateCalendarDays();
  }, [selectedDate]);

  const generateCalendarDays = () => {
    const year = selectedDate.getFullYear();
    const month = selectedDate.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDayOfWeek = firstDay.getDay();

    const days = [];
    
    // Add empty cells for days before month starts
    for (let i = 0; i < startingDayOfWeek; i++) {
      days.push(null);
    }
    
    // Add all days of the month
    for (let i = 1; i <= daysInMonth; i++) {
      days.push(new Date(year, month, i));
    }
    
    return days;
  };

  const handleScheduleStream = useCallback(() => {
    if (!formData.title || !formData.scheduledTime || formData.platforms.length === 0) {
      return;
    }

    const streamData = {
      ...formData,
      id: editingStream?.id || Date.now(),
      status: editingStream?.status || 'scheduled',
      createdAt: editingStream?.createdAt || new Date(),
      updatedAt: new Date()
    };

    if (editingStream) {
      onEdit?.(streamData);
    } else {
      onSchedule?.(streamData);
    }

    resetForm();
    setShowScheduleForm(false);
    setEditingStream(null);
  }, [formData, editingStream, onSchedule, onEdit]);

  const resetForm = () => {
    setFormData({
      title: '',
      description: '',
      platforms: [],
      scheduledTime: '',
      duration: 60,
      quality: '1080p',
      isRecurring: false,
      recurringPattern: 'weekly',
      reminderTime: 15,
      privacy: 'public',
      tags: []
    });
  };

  const formatDateTime = (date) => {
    return new Date(date).toLocaleString('en-US', {
      weekday: 'short',
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStreamStatusColor = (status) => {
    switch (status) {
      case 'live': return 'bg-red-500';
      case 'scheduled': return 'bg-blue-500';
      case 'completed': return 'bg-green-500';
      case 'cancelled': return 'bg-gray-500';
      default: return 'bg-gray-400';
    }
  };

  const getStreamStatusText = (status) => {
    switch (status) {
      case 'live': return 'LIVE';
      case 'scheduled': return 'SCHEDULED';
      case 'completed': return 'COMPLETED';
      case 'cancelled': return 'CANCELLED';
      default: return 'UNKNOWN';
    }
  };

  const CalendarView = () => {
    const calendarDays = generateCalendarDays();
    const currentMonth = selectedDate.getMonth();
    const currentYear = selectedDate.getFullYear();

    // Get streams for the current month
    const monthStreams = streams.filter(stream => {
      const streamDate = new Date(stream.scheduledTime);
      return streamDate.getMonth() === currentMonth && streamDate.getFullYear() === currentYear;
    });

    const getStreamsForDay = (day) => {
      if (!day) return [];
      return monthStreams.filter(stream => {
        const streamDate = new Date(stream.scheduledTime);
        return streamDate.getDate() === day.getDate();
      });
    };

    return (
      <div className="calendar-view">
        <div className="calendar-header">
          <div className="calendar-navigation">
            <button 
              onClick={() => setSelectedDate(new Date(currentYear, currentMonth - 1))}
              className="nav-btn"
            >
              ←
            </button>
            <h3>
              {selectedDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
            </h3>
            <button 
              onClick={() => setSelectedDate(new Date(currentYear, currentMonth + 1))}
              className="nav-btn"
            >
              →
            </button>
          </div>
          
          <div className="calendar-actions">
            <button 
              onClick={() => setSelectedDate(new Date())}
              className="today-btn"
            >
              Today
            </button>
          </div>
        </div>

        <div className="calendar-grid">
          <div className="calendar-weekdays">
            {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
              <div key={day} className="weekday">
                {day}
              </div>
            ))}
          </div>
          
          <div className="calendar-days">
            {calendarDays.map((day, index) => {
              const dayStreams = getStreamsForDay(day);
              const isToday = day && day.toDateString() === new Date().toDateString();
              
              return (
                <div 
                  key={index} 
                  className={`calendar-day ${day ? 'has-day' : 'empty'} ${isToday ? 'today' : ''}`}
                >
                  {day && (
                    <>
                      <div className="day-number">{day.getDate()}</div>
                      <div className="day-streams">
                        {dayStreams.slice(0, 3).map(stream => (
                          <div 
                            key={stream.id}
                            className="stream-indicator"
                            title={stream.title}
                          >
                            <div className={`indicator-dot ${getStreamStatusColor(stream.status)}`}></div>
                          </div>
                        ))}
                        {dayStreams.length > 3 && (
                          <div className="more-streams">
                            +{dayStreams.length - 3}
                          </div>
                        )}
                      </div>
                    </>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>
    );
  };

  const ListView = () => (
    <div className="list-view">
      <div className="list-header">
        <h3>Upcoming Streams</h3>
        <div className="filter-options">
          <select className="filter-select">
            <option>All Status</option>
            <option>Scheduled</option>
            <option>Live</option>
            <option>Completed</option>
          </select>
          <select className="filter-select">
            <option>All Platforms</option>
            <option>YouTube</option>
            <option>Facebook</option>
            <option>Twitch</option>
          </select>
        </div>
      </div>
      
      <div className="stream-list">
        {streams.map(stream => (
          <div key={stream.id} className="stream-card">
            <div className="stream-header">
              <div className="stream-title-section">
                <h4>{stream.title}</h4>
                <span className={`status-badge ${getStreamStatusColor(stream.status)}`}>
                  {getStreamStatusText(stream.status)}
                </span>
              </div>
              <div className="stream-actions">
                <button 
                  onClick={() => {
                    setEditingStream(stream);
                    setFormData(stream);
                    setShowScheduleForm(true);
                  }}
                  className="action-btn edit"
                >
                  <Settings size={16} />
                </button>
                <button 
                  onClick={() => onDelete?.(stream.id)}
                  className="action-btn delete"
                >
                  ×
                </button>
              </div>
            </div>
            
            <div className="stream-details">
              <p className="stream-description">{stream.description}</p>
              
              <div className="stream-meta">
                <div className="meta-item">
                  <Calendar size={14} />
                  {formatDateTime(stream.scheduledTime)}
                </div>
                <div className="meta-item">
                  <Clock size={14} />
                  {stream.duration} minutes
                </div>
                <div className="meta-item">
                  <Video size={14} />
                  {stream.quality}
                </div>
                <div className="meta-item">
                  <Globe size={14} />
                  {stream.privacy}
                </div>
              </div>
              
              <div className="stream-platforms">
                {stream.platforms?.map(platform => (
                  <span key={platform} className="platform-tag">
                    {platform}
                  </span>
                ))}
              </div>
              
              {stream.tags?.length > 0 && (
                <div className="stream-tags">
                  {stream.tags.map(tag => (
                    <span key={tag} className="tag">
                      #{tag}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const TimelineView = () => (
    <div className="timeline-view">
      <div className="timeline-header">
        <h3>Timeline View</h3>
        <div className="timeline-controls">
          <button className="zoom-btn">Zoom In</button>
          <button className="zoom-btn">Zoom Out</button>
          <button className="fit-btn">Fit</button>
        </div>
      </div>
      
      <div className="timeline-container">
        <div className="timeline-hours">
          {Array.from({ length: 24 }, (_, i) => (
            <div key={i} className="hour-mark">
              {i.toString().padStart(2, '0')}:00
            </div>
          ))}
        </div>
        
        <div className="timeline-tracks">
          {['YouTube', 'Facebook', 'Twitch', 'LinkedIn'].map(platform => (
            <div key={platform} className="timeline-track">
              <div className="track-label">{platform}</div>
              <div className="track-content">
                {streams
                  .filter(stream => stream.platforms.includes(platform))
                  .map(stream => {
                    const startTime = new Date(stream.scheduledTime);
                    const startHour = startTime.getHours() + startTime.getMinutes() / 60;
                    const durationHours = stream.duration / 60;
                    
                    return (
                      <div
                        key={stream.id}
                        className="timeline-event"
                        style={{
                          left: `${(startHour / 24) * 100}%`,
                          width: `${(durationHours / 24) * 100}%`,
                          backgroundColor: stream.status === 'live' ? '#ef4444' : '#3b82f6'
                        }}
                        title={stream.title}
                      >
                        <div className="event-title">{stream.title}</div>
                        <div className="event-time">
                          {startTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </div>
                      </div>
                    );
                  })}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const ScheduleForm = () => (
    <div className="schedule-form-overlay">
      <div className="schedule-form">
        <div className="form-header">
          <h3>{editingStream ? 'Edit Stream' : 'Schedule New Stream'}</h3>
          <button 
            onClick={() => {
              setShowScheduleForm(false);
              setEditingStream(null);
              resetForm();
            }}
            className="close-btn"
          >
            ×
          </button>
        </div>
        
        <div className="form-content">
          <div className="form-section">
            <h4>Basic Information</h4>
            <div className="form-group">
              <label>Stream Title *</label>
              <input
                type="text"
                value={formData.title}
                onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
                placeholder="Enter stream title"
                className="form-input"
              />
            </div>
            
            <div className="form-group">
              <label>Description</label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                placeholder="Describe your stream"
                rows={3}
                className="form-textarea"
              />
            </div>
          </div>
          
          <div className="form-section">
            <h4>Schedule</h4>
            <div className="form-row">
              <div className="form-group">
                <label>Date & Time *</label>
                <input
                  type="datetime-local"
                  value={formData.scheduledTime}
                  onChange={(e) => setFormData(prev => ({ ...prev, scheduledTime: e.target.value }))}
                  className="form-input"
                />
              </div>
              
              <div className="form-group">
                <label>Duration (minutes)</label>
                <input
                  type="number"
                  value={formData.duration}
                  onChange={(e) => setFormData(prev => ({ ...prev, duration: parseInt(e.target.value) }))}
                  min="15"
                  max="480"
                  className="form-input"
                />
              </div>
            </div>
            
            <div className="form-group">
              <label>Reminder (minutes before)</label>
              <select
                value={formData.reminderTime}
                onChange={(e) => setFormData(prev => ({ ...prev, reminderTime: parseInt(e.target.value) }))}
                className="form-select"
              >
                <option value={5}>5 minutes</option>
                <option value={15}>15 minutes</option>
                <option value={30}>30 minutes</option>
                <option value={60}>1 hour</option>
                <option value={120}>2 hours</option>
              </select>
            </div>
          </div>
          
          <div className="form-section">
            <h4>Platforms</h4>
            <div className="platform-selection">
              {['YouTube', 'Facebook', 'Twitch', 'LinkedIn', 'TikTok', 'Instagram'].map(platform => (
                <label key={platform} className="platform-checkbox">
                  <input
                    type="checkbox"
                    checked={formData.platforms.includes(platform)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setFormData(prev => ({ ...prev, platforms: [...prev.platforms, platform] }));
                      } else {
                        setFormData(prev => ({ ...prev, platforms: prev.platforms.filter(p => p !== platform) }));
                      }
                    }}
                  />
                  <span>{platform}</span>
                </label>
              ))}
            </div>
          </div>
          
          <div className="form-section">
            <h4>Technical Settings</h4>
            <div className="form-row">
              <div className="form-group">
                <label>Quality</label>
                <select
                  value={formData.quality}
                  onChange={(e) => setFormData(prev => ({ ...prev, quality: e.target.value }))}
                  className="form-select"
                >
                  <option value="720p">720p</option>
                  <option value="1080p">1080p</option>
                  <option value="1440p">1440p</option>
                  <option value="4K">4K</option>
                </select>
              </div>
              
              <div className="form-group">
                <label>Privacy</label>
                <select
                  value={formData.privacy}
                  onChange={(e) => setFormData(prev => ({ ...prev, privacy: e.target.value }))}
                  className="form-select"
                >
                  <option value="public">Public</option>
                  <option value="unlisted">Unlisted</option>
                  <option value="private">Private</option>
                </select>
              </div>
            </div>
          </div>
          
          <div className="form-section">
            <h4>Recurring Stream</h4>
            <label className="checkbox-group">
              <input
                type="checkbox"
                checked={formData.isRecurring}
                onChange={(e) => setFormData(prev => ({ ...prev, isRecurring: e.target.checked }))}
              />
              <span>Make this a recurring stream</span>
            </label>
            
            {formData.isRecurring && (
              <div className="form-group">
                <label>Repeat Pattern</label>
                <select
                  value={formData.recurringPattern}
                  onChange={(e) => setFormData(prev => ({ ...prev, recurringPattern: e.target.value }))}
                  className="form-select"
                >
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                  <option value="biweekly">Bi-weekly</option>
                  <option value="monthly">Monthly</option>
                </select>
              </div>
            )}
          </div>
        </div>
        
        <div className="form-footer">
          <button
            onClick={() => {
              setShowScheduleForm(false);
              setEditingStream(null);
              resetForm();
            }}
            className="btn-secondary"
          >
            Cancel
          </button>
          <button
            onClick={handleScheduleStream}
            disabled={!formData.title || !formData.scheduledTime || formData.platforms.length === 0}
            className="btn-primary"
          >
            {editingStream ? 'Update Stream' : 'Schedule Stream'}
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <div className="stream-scheduler">
      <div className="scheduler-header">
        <div className="header-left">
          <h2>Stream Scheduler</h2>
          <p>Plan and organize your streaming schedule</p>
        </div>
        
        <div className="header-right">
          <div className="view-switcher">
            <button
              className={`view-btn ${viewMode === 'calendar' ? 'active' : ''}`}
              onClick={() => setViewMode('calendar')}
            >
              <Calendar size={16} />
              Calendar
            </button>
            <button
              className={`view-btn ${viewMode === 'list' ? 'active' : ''}`}
              onClick={() => setViewMode('list')}
            >
              <List size={16} />
              List
            </button>
            <button
              className={`view-btn ${viewMode === 'timeline' ? 'active' : ''}`}
              onClick={() => setViewMode('timeline')}
            >
              <Clock size={16} />
              Timeline
            </button>
          </div>
          
          <button
            onClick={() => setShowScheduleForm(true)}
            className="schedule-btn"
          >
            <Zap size={16} />
            Schedule Stream
          </button>
        </div>
      </div>

      <div className="scheduler-content">
        {viewMode === 'calendar' && <CalendarView />}
        {viewMode === 'list' && <ListView />}
        {viewMode === 'timeline' && <TimelineView />}
      </div>

      {showScheduleForm && <ScheduleForm />}
    </div>
  );
};

export default StreamScheduler;