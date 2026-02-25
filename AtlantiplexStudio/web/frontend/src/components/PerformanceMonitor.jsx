import React, { useState, useEffect, useRef } from 'react';
import { Monitor, Cpu, Activity, Zap, Wifi, WifiOff, AlertTriangle } from 'lucide-react';

const PerformanceMonitor = ({ config, onPerformanceUpdate }) => {
  const [metrics, setMetrics] = useState({
    fps: 60,
    renderTime: 0,
    memoryUsage: 0,
    activeGlyphs: 0,
    drawCalls: 0,
    cpuUsage: 0,
    networkLatency: 0,
    frameTime: 16.67
  });
  
  const [performanceScore, setPerformanceScore] = useState(100);
  const [isOptimal, setIsOptimal] = useState(true);
  const [alerts, setAlerts] = useState([]);
  const frameTimeHistory = useRef([]);
  const lastFrameTime = useRef(performance.now());

  useEffect(() => {
    let animationId;
    
    const measurePerformance = (timestamp) => {
      const deltaTime = timestamp - lastFrameTime.current;
      const frameTime = deltaTime;
      const fps = Math.round(1000 / frameTime);
      
      // Store frame time history for analysis
      frameTimeHistory.current.push(frameTime);
      if (frameTimeHistory.current.length > 60) {
        frameTimeHistory.current.shift();
      }
      
      // Calculate metrics
      const avgFrameTime = frameTimeHistory.current.reduce((a, b) => a + b, 0) / frameTimeHistory.current.length;
      const memoryUsage = getMemoryUsage();
      const activeGlyphs = config.density || 50;
      
      // Update metrics state
      const newMetrics = {
        fps,
        renderTime: Math.round(deltaTime * 100) / 100,
        memoryUsage,
        activeGlyphs,
        drawCalls: Math.round(activeGlyphs * 1.5), // Estimate
        cpuUsage: estimateCPUUsage(fps, avgFrameTime),
        networkLatency: measureNetworkLatency(),
        frameTime: avgFrameTime
      };
      
      setMetrics(newMetrics);
      
      // Calculate performance score
      const score = calculatePerformanceScore(newMetrics);
      setPerformanceScore(score);
      
      // Check if optimal
      const optimal = checkOptimalPerformance(newMetrics);
      setIsOptimal(optimal);
      
      // Generate alerts
      const newAlerts = generatePerformanceAlerts(newMetrics, score);
      setAlerts(newAlerts);
      
      // Notify parent component
      onPerformanceUpdate?.(newMetrics, score);
      
      lastFrameTime.current = timestamp;
      animationId = requestAnimationFrame(measurePerformance);
    };
    
    animationId = requestAnimationFrame(measurePerformance);
    
    return () => {
      if (animationId) {
        cancelAnimationFrame(animationId);
      }
    };
  }, [config, onPerformanceUpdate]);

  const getMemoryUsage = () => {
    if (performance.memory) {
      const used = performance.memory.usedJSHeapSize / 1048576; // Convert to MB
      const total = performance.memory.totalJSHeapSize / 1048576;
      return {
        used: Math.round(used * 100) / 100,
        total: Math.round(total * 100) / 100,
        percentage: Math.round((used / total) * 100 * 100) / 100
      };
    }
    return { used: 0, total: 0, percentage: 0 };
  };

  const estimateCPUUsage = (fps, frameTime) => {
    // Simple CPU estimation based on frame time and FPS
    const targetFrameTime = 16.67; // 60 FPS
    const cpuUsage = Math.min(100, Math.max(0, (frameTime / targetFrameTime - 1) * 100));
    return Math.round(cpuUsage);
  };

  const measureNetworkLatency = () => {
    // Simulate network latency measurement
    return Math.round(Math.random() * 10 + 5); // 5-15ms
  };

  const calculatePerformanceScore = (metrics) => {
    let score = 100;
    
    // FPS score (40% weight)
    const fpsScore = Math.max(0, Math.min(100, (metrics.fps / 60) * 100));
    score = score * 0.6 + fpsScore * 0.4;
    
    // Frame time score (30% weight)
    const frameTimeScore = Math.max(0, Math.min(100, 100 - ((metrics.frameTime - 16.67) / 16.67 * 100)));
    score = score * 0.7 + frameTimeScore * 0.3;
    
    // Memory usage score (20% weight)
    const memoryScore = Math.max(0, Math.min(100, 100 - metrics.memoryUsage.percentage));
    score = score * 0.8 + memoryScore * 0.2;
    
    // CPU usage score (10% weight)
    const cpuScore = Math.max(0, Math.min(100, 100 - metrics.cpuUsage));
    score = score * 0.9 + cpuScore * 0.1;
    
    return Math.round(score);
  };

  const checkOptimalPerformance = (metrics) => {
    return (
      metrics.fps >= 55 &&
      metrics.frameTime <= 20 &&
      metrics.memoryUsage.percentage <= 70 &&
      metrics.cpuUsage <= 70
    );
  };

  const generatePerformanceAlerts = (metrics, score) => {
    const alerts = [];
    
    if (metrics.fps < 30) {
      alerts.push({
        type: 'critical',
        message: 'Very low FPS detected',
        icon: AlertTriangle
      });
    } else if (metrics.fps < 45) {
      alerts.push({
        type: 'warning',
        message: 'Low FPS - Consider reducing density',
        icon: Activity
      });
    }
    
    if (metrics.memoryUsage.percentage > 80) {
      alerts.push({
        type: 'critical',
        message: 'High memory usage detected',
        icon: AlertTriangle
      });
    } else if (metrics.memoryUsage.percentage > 60) {
      alerts.push({
        type: 'warning',
        message: 'Moderate memory usage',
        icon: Cpu
      });
    }
    
    if (metrics.cpuUsage > 80) {
      alerts.push({
        type: 'critical',
        message: 'High CPU usage detected',
        icon: AlertTriangle
      });
    } else if (metrics.cpuUsage > 60) {
      alerts.push({
        type: 'warning',
        message: 'Moderate CPU usage',
        icon: Zap
      });
    }
    
    return alerts;
  };

  const getPerformanceColor = (value, optimalRange) => {
    if (value >= optimalRange.max) return '#ef4444';
    if (value >= optimalRange.warning) return '#f59e0b';
    return '#10b981';
  };

  const getPerformanceLevel = (score) => {
    if (score >= 90) return { text: 'Excellent', color: '#10b981' };
    if (score >= 70) return { text: 'Good', color: '#3b82f6' };
    if (score >= 50) return { text: 'Fair', color: '#f59e0b' };
    return { text: 'Poor', color: '#ef4444' };
  };

  const performanceLevel = getPerformanceLevel(performanceScore);

  return (
    <div className="performance-monitor">
      <div className="monitor-header">
        <div className="header-left">
          <h3>Performance Monitor</h3>
          <div className={`status-indicator ${isOptimal ? 'optimal' : 'suboptimal'}`}>
            <div className="status-dot"></div>
            <span>{isOptimal ? 'Optimal' : 'Needs Optimization'}</span>
          </div>
        </div>
        
        <div className="header-right">
          <div className="overall-score">
            <span className="score-value">{performanceScore}</span>
            <span className="score-label">Score</span>
          </div>
          <div className="performance-level" style={{ color: performanceLevel.color }}>
            {performanceLevel.text}
          </div>
        </div>
      </div>

      {alerts.length > 0 && (
        <div className="performance-alerts">
          {alerts.map((alert, index) => (
            <div key={index} className={`alert-item ${alert.type}`}>
              <alert.icon size={14} />
              <span>{alert.message}</span>
            </div>
          ))}
        </div>
      )}

      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-header">
            <Monitor size={16} />
            <span>FPS</span>
          </div>
          <div className="metric-value" style={{ color: getPerformanceColor(metrics.fps, { warning: 45, max: 30 }) }}>
            {metrics.fps}
          </div>
          <div className="metric-bar">
            <div 
              className="metric-fill" 
              style={{ 
                width: `${Math.min(100, (metrics.fps / 60) * 100)}%`,
                backgroundColor: getPerformanceColor(metrics.fps, { warning: 45, max: 30 })
              }}
            ></div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-header">
            <Activity size={16} />
            <span>Frame Time</span>
          </div>
          <div className="metric-value" style={{ color: getPerformanceColor(metrics.frameTime, { warning: 20, max: 33.33 }) }}>
            {metrics.frameTime.toFixed(1)}ms
          </div>
          <div className="metric-bar">
            <div 
              className="metric-fill" 
              style={{ 
                width: `${Math.min(100, (33.33 / metrics.frameTime) * 100)}%`,
                backgroundColor: getPerformanceColor(metrics.frameTime, { warning: 20, max: 33.33 })
              }}
            ></div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-header">
            <Cpu size={16} />
            <span>CPU Usage</span>
          </div>
          <div className="metric-value" style={{ color: getPerformanceColor(metrics.cpuUsage, { warning: 60, max: 80 }) }}>
            {metrics.cpuUsage}%
          </div>
          <div className="metric-bar">
            <div 
              className="metric-fill" 
              style={{ 
                width: `${metrics.cpuUsage}%`,
                backgroundColor: getPerformanceColor(metrics.cpuUsage, { warning: 60, max: 80 })
              }}
            ></div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-header">
            <Zap size={16} />
            <span>Memory</span>
          </div>
          <div className="metric-value" style={{ color: getPerformanceColor(metrics.memoryUsage.percentage, { warning: 60, max: 80 }) }}>
            {metrics.memoryUsage.percentage}%
          </div>
          <div className="metric-bar">
            <div 
              className="metric-fill" 
              style={{ 
                width: `${metrics.memoryUsage.percentage}%`,
                backgroundColor: getPerformanceColor(metrics.memoryUsage.percentage, { warning: 60, max: 80 })
              }}
            ></div>
          </div>
          <div className="metric-subvalue">
            {metrics.memoryUsage.used}MB / {metrics.memoryUsage.total}MB
          </div>
        </div>
      </div>

      <div className="advanced-metrics">
        <div className="metric-row">
          <span className="metric-label">Active Glyphs:</span>
          <span className="metric-value">{metrics.activeGlyphs}</span>
        </div>
        
        <div className="metric-row">
          <span className="metric-label">Draw Calls:</span>
          <span className="metric-value">{metrics.drawCalls}</span>
        </div>
        
        <div className="metric-row">
          <span className="metric-label">Render Time:</span>
          <span className="metric-value">{metrics.renderTime}ms</span>
        </div>
        
        <div className="metric-row">
          <span className="metric-label">Network Latency:</span>
          <span className="metric-value">{metrics.networkLatency}ms</span>
        </div>
      </div>

      <div className="performance-tips">
        <h4>Optimization Tips</h4>
        <ul>
          {metrics.fps < 30 && (
            <li>Reduce glyph density to improve performance</li>
          )}
          {metrics.memoryUsage.percentage > 70 && (
            <li>Disable trail effects to reduce memory usage</li>
          )}
          {metrics.cpuUsage > 70 && (
            <li>Lower animation speed to reduce CPU load</li>
          )}
          {metrics.renderTime > 20 && (
            <li>Disable motion blur and glow effects</li>
          )}
          {isOptimal && (
            <li className="tip-success">Performance is optimal!</li>
          )}
        </ul>
      </div>
    </div>
  );
};

export default PerformanceMonitor;