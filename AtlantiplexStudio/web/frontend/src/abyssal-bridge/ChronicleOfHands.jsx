import React, { useState } from 'react';
import { 
  Shield, 
  UserPlus, 
  UserMinus, 
  MessageSquare, 
  Trash2,
  Video,
  AlertTriangle,
  AlertCircle,
  Settings,
  Ban,
  CheckCircle
} from 'lucide-react';

/**
 * Chronicle of Hands - Bottom Activity Strip
 * Real-time log of all actions, human and system
 */
const ChronicleOfHands = ({ entries, onFilterChange }) => {
  const [activeFilter, setActiveFilter] = useState('all');
  
  const filters = [
    { id: 'all', label: 'All Events' },
    { id: 'system', label: 'System' },
    { id: 'moderator', label: 'Moderators' },
    { id: 'guest', label: 'Guests' },
    { id: 'warning', label: 'Warnings' }
  ];
  
  const handleFilterClick = (filterId) => {
    setActiveFilter(filterId);
    onFilterChange?.(filterId);
  };
  
  const getIconForEntry = (entry) => {
    const iconMap = {
      'mute': Ban,
      'kick': UserMinus,
      'approve': CheckCircle,
      'deny': Ban,
      'spotlight': Video,
      'join': UserPlus,
      'leave': UserMinus,
      'purge': Trash2,
      'strike': AlertTriangle,
      'scene': Video,
      'overlay': Settings,
      'warning': AlertCircle,
      'error': AlertTriangle
    };
    
    const Icon = iconMap[entry.action] || 
                 (entry.type === 'system' ? Settings :
                  entry.type === 'moderator' ? Shield :
                  entry.type === 'guest' ? UserPlus :
                  entry.type === 'warning' ? AlertCircle :
                  entry.type === 'danger' ? AlertTriangle : Settings);
    
    return <Icon size={16} />;
  };
  
  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { 
      hour12: false, 
      hour: '2-digit', 
      minute: '2-digit', 
      second: '2-digit' 
    });
  };
  
  const getEntryTitle = (entry) => {
    if (entry.title) return entry.title;
    
    switch (entry.action) {
      case 'mute': return `${entry.target || 'User'} muted`;
      case 'kick': return `${entry.target || 'User'} kicked`;
      case 'approve': return `${entry.target || 'User'} approved`;
      case 'deny': return `${entry.target || 'User'} denied`;
      case 'spotlight': return `${entry.target || 'Guest'} spotlighted`;
      case 'join': return `${entry.actor || 'Guest'} joined`;
      case 'leave': return `${entry.actor || 'Guest'} left`;
      case 'purge': return 'Chat purged';
      case 'strike': return `Strike issued to ${entry.target || 'user'}`;
      case 'scene': return `Scene changed to ${entry.target || 'unknown'}`;
      case 'overlay': return `Overlay triggered: ${entry.target || 'unknown'}`;
      default: return entry.message || 'Unknown event';
    }
  };
  
  const getEntryMeta = (entry) => {
    const parts = [];
    
    if (entry.actor && entry.actor !== 'System') {
      parts.push(`by ${entry.actor}`);
    }
    
    if (entry.target && entry.action !== 'join' && entry.action !== 'leave') {
      parts.push(`target: ${entry.target}`);
    }
    
    if (entry.details) {
      parts.push(entry.details);
    }
    
    return parts.join(' • ');
  };
  
  // Filter entries based on active filter
  const filteredEntries = activeFilter === 'all' 
    ? entries 
    : entries.filter(e => e.type === activeFilter || e.category === activeFilter);
  
  return (
    <div className="chronicle-strip">
      {/* Filter Runes */}
      <div className="chronicle-filters">
        {filters.map(filter => (
          <button
            key={filter.id}
            className={`chronicle-filter-rune ${activeFilter === filter.id ? 'active' : ''}`}
            onClick={() => handleFilterClick(filter.id)}
          >
            {filter.label}
          </button>
        ))}
      </div>
      
      {/* Activity Stream */}
      <div className="chronicle-stream">
        {filteredEntries.length === 0 ? (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: '100%',
            color: 'rgba(255, 255, 255, 0.3)',
            fontSize: '12px'
          }}>
            Awaiting chronicle entries...
          </div>
        ) : (
          filteredEntries.map((entry) => (
            <div
              key={entry.id}
              className={`chronicle-tile ${entry.type}`}
            >
              <div className="chronicle-tile-icon">
                {getIconForEntry(entry)}
              </div>
              
              <div className="chronicle-tile-content">
                <div className="chronicle-tile-title">
                  {getEntryTitle(entry)}
                </div>
                <div className="chronicle-tile-meta">
                  {getEntryMeta(entry)}
                </div>
              </div>
              
              <div className="chronicle-tile-time">
                {formatTimestamp(entry.timestamp)}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default ChronicleOfHands;