import React, { useState } from 'react';
import { 
  Server, 
  Activity, 
  Database, 
  Clock,
  ChevronDown,
  ChevronUp
} from 'lucide-react';

/**
 * Systems Oracle - Left Column
 * System health, backend performance, and operational integrity
 */
const SystemsOracle = ({
  serverLoad,
  webrtcConnections,
  apiLatency,
  apiErrors,
  history
}) => {
  const [expandedSection, setExpandedSection] = useState(null);
  
  const toggleSection = (section) => {
    setExpandedSection(expandedSection === section ? null : section);
  };
  
  // Calculate load intensity (affects rotation speed)
  const getLoadIntensity = (value) => {
    if (value < 30) return 3; // Low load - slow rotation
    if (value < 60) return 2; // Medium load
    if (value < 80) return 1; // High load - fast rotation
    return 0.5; // Critical - very fast
  };
  
  return (
    <div className="systems-oracle">
      {/* Server Load Runes */}
      <div className="oracle-section">
        <div className="oracle-title">
          <Server size={12} />
          Server Vitals
        </div>
        
        <div className="server-runes">
          {/* CPU Rune */}
          <div className="server-rune">
            <div className="server-rune-spinner" style={{
              animationDuration: `${getLoadIntensity(serverLoad.cpu)}s`
            }}>
              <svg viewBox="0 0 40 40">
                <circle
                  cx="20"
                  cy="20"
                  r="16"
                  fill="none"
                  stroke="rgba(106, 0, 255, 0.3)"
                  strokeWidth="3"
                />
                <circle
                  cx="20"
                  cy="20"
                  r="16"
                  fill="none"
                  stroke="#6A00FF"
                  strokeWidth="3"
                  strokeDasharray={`${serverLoad.cpu * 1.01} 100`}
                  transform="rotate(-90 20 20)"
                  style={{
                    filter: 'drop-shadow(0 0 4px rgba(106, 0, 255, 0.5))'
                  }}
                />
              </svg>
            </div>
            <div className="server-rune-value" style={{
              color: serverLoad.cpu > 80 ? '#FF2D55' : serverLoad.cpu > 60 ? '#FF9500' : '#fff'
            }}>
              {serverLoad.cpu}%
            </div>
            <div className="server-rune-label">CPU</div>
          </div>
          
          {/* GPU Rune */}
          <div className="server-rune">
            <div className="server-rune-spinner" style={{
              animationDuration: `${getLoadIntensity(serverLoad.gpu)}s`
            }}>
              <svg viewBox="0 0 40 40">
                <polygon
                  points="20,4 36,14 36,30 20,38 4,30 4,14"
                  fill="none"
                  stroke="rgba(106, 0, 255, 0.3)"
                  strokeWidth="2"
                />
                <polygon
                  points="20,4 36,14 36,30 20,38 4,30 4,14"
                  fill="none"
                  stroke="#6A00FF"
                  strokeWidth="2"
                  strokeDasharray={`${serverLoad.gpu * 1.2} 120`}
                  style={{
                    filter: 'drop-shadow(0 0 4px rgba(106, 0, 255, 0.5))'
                  }}
                />
              </svg>
            </div>
            <div className="server-rune-value" style={{
              color: serverLoad.gpu > 80 ? '#FF2D55' : serverLoad.gpu > 60 ? '#FF9500' : '#fff'
            }}>
              {serverLoad.gpu}%
            </div>
            <div className="server-rune-label">GPU</div>
          </div>
          
          {/* RAM Rune */}
          <div className="server-rune">
            <div className="server-rune-spinner" style={{
              animationDuration: `${getLoadIntensity(serverLoad.ram)}s`
            }}>
              <svg viewBox="0 0 40 40">
                <rect
                  x="8"
                  y="8"
                  width="24"
                  height="24"
                  fill="none"
                  stroke="rgba(106, 0, 255, 0.3)"
                  strokeWidth="2"
                />
                <rect
                  x="8"
                  y="8"
                  width={24 * (serverLoad.ram / 100)}
                  height="24"
                  fill="rgba(106, 0, 255, 0.3)"
                  stroke="#6A00FF"
                  strokeWidth="1"
                  style={{
                    filter: 'drop-shadow(0 0 4px rgba(106, 0, 255, 0.5))'
                  }}
                />
              </svg>
            </div>
            <div className="server-rune-value" style={{
              color: serverLoad.ram > 80 ? '#FF2D55' : serverLoad.ram > 60 ? '#FF9500' : '#fff'
            }}>
              {serverLoad.ram}%
            </div>
            <div className="server-rune-label">RAM</div>
          </div>
        </div>
      </div>
      
      {/* WebRTC Constellation */}
      <div className="oracle-section">
        <div className="oracle-title">
          <Activity size={12} />
          WebRTC Constellation
        </div>
        
        <div className="constellation-map">
          {/* Central hub */}
          <div 
            className="constellation-node"
            style={{
              left: '50%',
              top: '50%',
              transform: 'translate(-50%, -50%)',
              width: '12px',
              height: '12px',
              background: '#00F6FF',
              boxShadow: '0 0 15px #00F6FF'
            }}
          />
          
          {/* Connection nodes */}
          {webrtcConnections.map((conn, index) => {
            const angle = (index / webrtcConnections.length) * 2 * Math.PI - Math.PI / 2;
            const radius = 40;
            const x = 50 + (Math.cos(angle) * radius);
            const y = 50 + (Math.sin(angle) * radius);
            
            return (
              <React.Fragment key={conn.id}>
                {/* Connection line */}
                <div
                  className="constellation-line"
                  style={{
                    left: '50%',
                    top: '50%',
                    width: `${radius}px`,
                    transform: `rotate(${angle * 180 / Math.PI}deg)`,
                    opacity: conn.quality > 0.7 ? 0.6 : 0.3
                  }}
                />
                
                {/* Node */}
                <div
                  className="constellation-node"
                  style={{
                    left: `${x}%`,
                    top: `${y}%`,
                    transform: 'translate(-50%, -50%)',
                    background: conn.quality > 0.7 ? '#00FF8A' : conn.quality > 0.4 ? '#FF9500' : '#FF2D55',
                    boxShadow: `0 0 10px ${conn.quality > 0.7 ? '#00FF8A' : conn.quality > 0.4 ? '#FF9500' : '#FF2D55'}`,
                    width: conn.active ? '10px' : '6px',
                    height: conn.active ? '10px' : '6px'
                  }}
                />
              </React.Fragment>
            );
          })}
          
          {/* Empty state */}
          {webrtcConnections.length === 0 && (
            <div style={{
              position: 'absolute',
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
              fontSize: '11px',
              color: 'rgba(255, 255, 255, 0.3)',
              textAlign: 'center'
            }}>
              Awaiting connections...
            </div>
          )}
        </div>
        
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          marginTop: '8px',
          fontSize: '10px',
          color: 'rgba(255, 255, 255, 0.5)'
        }}>
          <span>Active: {webrtcConnections.filter(c => c.active).length}</span>
          <span>Total: {webrtcConnections.length}</span>
        </div>
      </div>
      
      {/* API Latency River */}
      <div className="oracle-section">
        <div className="oracle-title">
          <Database size={12} />
          API Currents
        </div>
        
        <div className="latency-river">
          <div className="latency-flow" />
          
          {/* Error sparks */}
          {apiErrors > 0 && Array.from({ length: Math.min(apiErrors, 5) }).map((_, i) => (
            <div
              key={i}
              className="latency-spark"
              style={{
                animationDelay: `${i * 0.8}s`,
                top: `${20 + Math.random() * 60}%`
              }}
            />
          ))}
        </div>
        
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          marginTop: '8px'
        }}>
          <span style={{
            fontSize: '11px',
            color: apiLatency < 100 ? '#00FF8A' : apiLatency < 300 ? '#FF9500' : '#FF2D55'
          }}>
            {apiLatency}ms
          </span>
          <span style={{
            fontSize: '11px',
            color: apiErrors > 0 ? '#FF2D55' : 'rgba(255, 255, 255, 0.5)'
          }}>
            {apiErrors > 0 ? `${apiErrors} errors` : 'No errors'}
          </span>
        </div>
      </div>
      
      {/* Historical Performance Scroll */}
      <div className="oracle-section" style={{ flex: 1 }}>
        <div 
          className="oracle-title"
          onClick={() => toggleSection('history')}
          style={{ cursor: 'pointer', display: 'flex', justifyContent: 'space-between' }}
        >
          <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Clock size={12} />
            Historical Runes
          </span>
          {expandedSection === 'history' ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
        </div>
        
        {expandedSection === 'history' && (
          <div className="historical-scroll">
            {/* Hourly Graph */}
            <div style={{ marginBottom: '16px' }}>
              <div style={{
                fontSize: '10px',
                color: 'rgba(255, 255, 255, 0.5)',
                marginBottom: '6px',
                textTransform: 'uppercase',
                letterSpacing: '0.5px'
              }}>
                Hourly Arc
              </div>
              <div className="historical-chart">
                <svg width="100%" height="100%" viewBox="0 0 200 60" preserveAspectRatio="none">
                  <defs>
                    <linearGradient id="hourlyGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                      <stop offset="0%" stopColor="#6A00FF" stopOpacity="0.5" />
                      <stop offset="100%" stopColor="#6A00FF" stopOpacity="0" />
                    </linearGradient>
                  </defs>
                  <path
                    d={`M0,60 ${history.hourly.map((v, i) => `L${(i / (history.hourly.length - 1)) * 200},${60 - (v / 100) * 60}`).join(' ')} L200,60 Z`}
                    fill="url(#hourlyGradient)"
                  />
                  <path
                    d={`M0,60 ${history.hourly.map((v, i) => `L${(i / (history.hourly.length - 1)) * 200},${60 - (v / 100) * 60}`).join(' ')}`}
                    fill="none"
                    stroke="#6A00FF"
                    strokeWidth="2"
                  />
                </svg>
              </div>
            </div>
            
            {/* Daily Arc */}
            <div>
              <div style={{
                fontSize: '10px',
                color: 'rgba(255, 255, 255, 0.5)',
                marginBottom: '6px',
                textTransform: 'uppercase',
                letterSpacing: '0.5px'
              }}>
                Daily Tide
              </div>
              <div className="historical-chart">
                <svg width="100%" height="100%" viewBox="0 0 200 60" preserveAspectRatio="none">
                  <defs>
                    <linearGradient id="dailyGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                      <stop offset="0%" stopColor="#00F6FF" stopOpacity="0.5" />
                      <stop offset="100%" stopColor="#00F6FF" stopOpacity="0" />
                    </linearGradient>
                  </defs>
                  <path
                    d={`M0,60 ${history.daily.map((v, i) => `L${(i / (history.daily.length - 1)) * 200},${60 - (v / 100) * 60}`).join(' ')} L200,60 Z`}
                    fill="url(#dailyGradient)"
                  />
                  <path
                    d={`M0,60 ${history.daily.map((v, i) => `L${(i / (history.daily.length - 1)) * 200},${60 - (v / 100) * 60}`).join(' ')}`}
                    fill="none"
                    stroke="#00F6FF"
                    strokeWidth="2"
                  />
                </svg>
              </div>
            </div>
          </div>
        )}
        
        {!history.hourly?.length && (
          <div style={{
            fontSize: '11px',
            color: 'rgba(255, 255, 255, 0.3)',
            textAlign: 'center',
            padding: '20px 0'
          }}>
            Gathering temporal data...
          </div>
        )}
      </div>
    </div>
  );
};

export default SystemsOracle;