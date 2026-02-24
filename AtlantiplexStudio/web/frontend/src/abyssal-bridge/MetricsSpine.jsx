import React, { useEffect, useRef } from 'react';
import { 
  Activity, 
  Users, 
  MessageSquare, 
  Heart,
  Wifi,
  Cpu,
  Mic,
  Monitor
} from 'lucide-react';

/**
 * Metrics Spine - Right Column
 * Real-time telemetry: stream vitals, audience pulse, guest diagnostics
 */
const MetricsSpine = ({
  bitrate,
  fps,
  droppedFrames,
  latency,
  liveViewers,
  engagementVelocity,
  sentimentTide,
  guests
}) => {
  const waveRef = useRef(null);
  
  // Animate wave graph
  useEffect(() => {
    if (!waveRef.current) return;
    
    const canvas = waveRef.current;
    const ctx = canvas.getContext('2d');
    let animationId;
    let offset = 0;
    
    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      // Draw wave
      ctx.beginPath();
      ctx.moveTo(0, canvas.height / 2);
      
      for (let x = 0; x < canvas.width; x++) {
        const y = canvas.height / 2 + 
          Math.sin((x + offset) * 0.05) * 10 + 
          Math.sin((x + offset * 1.5) * 0.03) * 5;
        ctx.lineTo(x, y);
      }
      
      ctx.strokeStyle = '#00F6FF';
      ctx.lineWidth = 2;
      ctx.stroke();
      
      // Fill gradient
      ctx.lineTo(canvas.width, canvas.height);
      ctx.lineTo(0, canvas.height);
      ctx.closePath();
      
      const gradient = ctx.createLinearGradient(0, 0, 0, canvas.height);
      gradient.addColorStop(0, 'rgba(0, 246, 255, 0.3)');
      gradient.addColorStop(1, 'rgba(0, 246, 255, 0)');
      ctx.fillStyle = gradient;
      ctx.fill();
      
      offset += 2;
      animationId = requestAnimationFrame(animate);
    };
    
    animate();
    
    return () => cancelAnimationFrame(animationId);
  }, []);
  
  // Determine status colors
  const getBitrateStatus = (val) => {
    if (val < 2000) return 'danger';
    if (val < 3500) return 'warning';
    return '';
  };
  
  const getFpsStatus = (val) => {
    if (val < 30) return 'danger';
    if (val < 55) return 'warning';
    return '';
  };
  
  const getLatencyStatus = (val) => {
    if (val > 200) return 'danger';
    if (val > 100) return 'warning';
    return '';
  };
  
  const getDroppedFramesStatus = (val) => {
    if (val > 50) return 'danger';
    if (val > 10) return 'warning';
    return '';
  };
  
  // Get guest connection quality
  const getGuestQuality = (guest) => {
    if (guest.connectionQuality > 0.8) return 'excellent';
    if (guest.connectionQuality > 0.6) return 'good';
    if (guest.connectionQuality > 0.4) return 'fair';
    if (guest.connectionQuality > 0.2) return 'poor';
    return 'critical';
  };
  
  return (
    <div className="metrics-spine">
      {/* Stream Vital Signs */}
      <div className="spine-section">
        <div className="spine-title">
          <Activity size={12} />
          Stream Vitals
        </div>
        
        <div className="vital-signs">
          {/* Bitrate */}
          <div className="vital-sign">
            <span className="vital-sign-label">
              <Activity size={10} />
              Bitrate
            </span>
            <span className={`vital-sign-value ${getBitrateStatus(bitrate)}`}>
              {bitrate} kbps
            </span>
          </div>
          
          {/* Wave Graph */}
          <div className="wave-graph">
            <canvas 
              ref={waveRef}
              width={300}
              height={40}
              style={{ width: '100%', height: '100%' }}
            />
          </div>
          
          {/* FPS */}
          <div className="vital-sign">
            <span className="vital-sign-label">
              <Monitor size={10} />
              FPS
            </span>
            <span className={`vital-sign-value ${getFpsStatus(fps)}`}>
              {fps}
            </span>
          </div>
          
          {/* Dropped Frames */}
          <div className="vital-sign">
            <span className="vital-sign-label">
              <Activity size={10} />
              Dropped
            </span>
            <span className={`vital-sign-value ${getDroppedFramesStatus(droppedFrames)}`}>
              {droppedFrames}
            </span>
          </div>
          
          {/* Latency */}
          <div className="vital-sign">
            <span className="vital-sign-label">
              <Wifi size={10} />
              Latency
            </span>
            <span className={`vital-sign-value ${getLatencyStatus(latency)}`}>
              {latency}ms
            </span>
          </div>
        </div>
      </div>
      
      {/* Audience Pulse */}
      <div className="spine-section">
        <div className="spine-title">
          <Users size={12} />
          Audience Pulse
        </div>
        
        {/* Live Viewer Orb */}
        <div className="audience-orb">
          <div className="orb-ring" />
          <div className="orb-ring" />
          <div className="orb-ring" />
          <div className="orb-core" />
          <span className="orb-count">{liveViewers.toLocaleString()}</span>
        </div>
        
        {/* Engagement Velocity */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: '8px',
          marginBottom: '12px'
        }}>
          <div style={{
            background: 'rgba(0, 0, 0, 0.3)',
            padding: '8px',
            borderRadius: '6px',
            textAlign: 'center'
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '4px',
              fontSize: '10px',
              color: 'rgba(255, 255, 255, 0.5)',
              marginBottom: '4px'
            }}>
              <MessageSquare size={10} />
              Msg/min
            </div>
            <div style={{
              fontSize: '16px',
              fontWeight: 700,
              color: '#fff'
            }}>
              {engagementVelocity.messagesPerMinute}
            </div>
          </div>
          
          <div style={{
            background: 'rgba(0, 0, 0, 0.3)',
            padding: '8px',
            borderRadius: '6px',
            textAlign: 'center'
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '4px',
              fontSize: '10px',
              color: 'rgba(255, 255, 255, 0.5)',
              marginBottom: '4px'
            }}>
              <Heart size={10} />
              React/min
            </div>
            <div style={{
              fontSize: '16px',
              fontWeight: 700,
              color: '#fff'
            }}>
              {engagementVelocity.reactionsPerMinute}
            </div>
          </div>
        </div>
        
        {/* Sentiment Tide */}
        <div>
          <div style={{
            fontSize: '10px',
            color: 'rgba(255, 255, 255, 0.5)',
            marginBottom: '6px',
            textTransform: 'uppercase',
            letterSpacing: '0.5px'
          }}>
            Sentiment Tide
          </div>
          <div style={{
            height: '6px',
            background: 'rgba(0, 0, 0, 0.3)',
            borderRadius: '3px',
            overflow: 'hidden',
            position: 'relative'
          }}>
            <div style={{
              position: 'absolute',
              left: 0,
              top: 0,
              bottom: 0,
              width: `${sentimentTide * 100}%`,
              background: `linear-gradient(90deg, 
                #FF2D55 0%, 
                #FF9500 ${sentimentTide < 0.5 ? sentimentTide * 200 : 50}%, 
                #00FF8A 100%
              )`,
              borderRadius: '3px',
              transition: 'width 0.5s ease'
            }} />
          </div>
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            marginTop: '4px',
            fontSize: '9px',
            color: 'rgba(255, 255, 255, 0.4)'
          }}>
            <span>Negative</span>
            <span>Neutral</span>
            <span>Positive</span>
          </div>
        </div>
      </div>
      
      {/* Guest Diagnostics */}
      <div className="spine-section" style={{ flex: 1 }}>
        <div className="spine-title">
          <Users size={12} />
          Guest Shards ({guests.length})
        </div>
        
        <div className="guest-shards">
          {guests.map((guest) => (
            <div 
              key={guest.id}
              className={`guest-shard ${getGuestQuality(guest)}`}
            >
              <div className="guest-avatar">
                {guest.name.charAt(0).toUpperCase()}
              </div>
              
              <div className="guest-info">
                <div className="guest-name">{guest.name}</div>
                <div className="guest-metrics">
                  <span className="guest-metric">
                    <Wifi size={8} />
                    {Math.round(guest.connectionQuality * 100)}%
                  </span>
                  <span className="guest-metric">
                    <Cpu size={8} />
                    {guest.cpuLoad}%
                  </span>
                  <span className="guest-metric">
                    <Mic size={8} />
                    {guest.audioLevel}dB
                  </span>
                </div>
              </div>
              
              <div className="guest-status" style={{
                background: guest.connectionQuality > 0.6 ? '#00FF8A' : 
                           guest.connectionQuality > 0.3 ? '#FF9500' : '#FF2D55',
                boxShadow: `0 0 8px ${guest.connectionQuality > 0.6 ? '#00FF8A' : 
                                      guest.connectionQuality > 0.3 ? '#FF9500' : '#FF2D55'}`
              }} />
            </div>
          ))}
          
          {guests.length === 0 && (
            <div style={{
              fontSize: '11px',
              color: 'rgba(255, 255, 255, 0.3)',
              textAlign: 'center',
              padding: '20px 0'
            }}>
              No guests connected
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MetricsSpine;