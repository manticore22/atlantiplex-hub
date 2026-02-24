import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Play, Pause, Settings, X, Maximize2, Zap, Code, Eye, EyeOff, Download, Upload, Palette, RotateCcw } from 'lucide-react';

const MatrixCurtain = ({ isOpen, onToggle, position = 'front' }) => {
  const canvasRef = useRef(null);
  const animationRef = useRef(null);
  const glyphsRef = useRef([]);
  const [isPaused, setIsPaused] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [config, setConfig] = useState({
    density: 50,
    speed: 1.0,
    gravity: 0.5,
    wind: 0,
    fadeSpeed: 0.02,
    glowIntensity: 0.8,
    colorScheme: 'matrix',
    backgroundColor: 'rgba(0, 0, 0, 0.9)',
    showControls: true,
    physicsEnabled: true,
    collisionDetection: false,
    trailEffect: true,
    pulseEffect: true
  });

  // Color schemes for the matrix effect
  const colorSchemes = {
    matrix: {
      primary: '#00ff41',
      secondary: '#008f11',
      tertiary: '#004d0a',
      glow: 'rgba(0, 255, 65, 0.8)'
    },
    cyberpunk: {
      primary: '#00ffff',
      secondary: '#ff00ff',
      tertiary: '#ffff00',
      glow: 'rgba(0, 255, 255, 0.8)'
    },
    fire: {
      primary: '#ff6b35',
      secondary: '#f77825',
      tertiary: '#f4b942',
      glow: 'rgba(255, 107, 53, 0.8)'
    },
    ice: {
      primary: '#00bfff',
      secondary: '#87ceeb',
      tertiary: '#b0e0e6',
      glow: 'rgba(0, 191, 255, 0.8)'
    },
    neon: {
      primary: '#ff00ff',
      secondary: '#00ff00',
      tertiary: '#0000ff',
      glow: 'rgba(255, 0, 255, 0.8)'
    },
    solar: {
      primary: '#ffeb3b',
      secondary: '#ff9800',
      tertiary: '#ff5722',
      glow: 'rgba(255, 235, 59, 0.8)'
    }
  };

  // Matrix character set
  const matrixGlyphs = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789@#$%^&*()_+-=[]{}|;:<>?,./~`ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ';

  const initializeGlyphs = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const glyphs = [];
    const numGlyphs = Math.floor((canvas.width / 20) * (config.density / 100));
    const colors = colorSchemes[config.colorScheme];

    for (let i = 0; i < numGlyphs; i++) {
      glyphs.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height - canvas.height,
        vx: (Math.random() - 0.5) * config.wind,
        vy: Math.random() * 2 + 1,
        glyph: matrixGlyphs[Math.floor(Math.random() * matrixGlyphs.length)],
        fontSize: Math.random() * 20 + 12,
        color: colors.primary,
        opacity: 1,
        rotation: Math.random() * Math.PI * 2,
        rotationSpeed: (Math.random() - 0.5) * 0.1,
        trail: [],
        maxTrailLength: config.trailEffect ? 15 : 0,
        danglePhase: Math.random() * Math.PI * 2,
        dangleSpeed: Math.random() * 0.05 + 0.02,
        dangleAmplitude: Math.random() * 0.5 + 0.5,
        pulsePhase: Math.random() * Math.PI * 2
      });
    }

    glyphsRef.current = glyphs;
  }, [config.density, config.wind, config.trailEffect, config.colorScheme]);

  const updateGlyphs = useCallback(() => {
    if (!config.physicsEnabled) return;

    const canvas = canvasRef.current;
    const colors = colorSchemes[config.colorScheme];
    
    glyphsRef.current = glyphsRef.current.map(glyph => {
      // Apply physics
      const newGlyph = { ...glyph };
      
      // Update position
      newGlyph.x += glyph.vx * config.speed;
      newGlyph.y += glyph.vy * config.gravity * config.speed;
      
      // Dangle physics
      newGlyph.danglePhase += glyph.dangleSpeed;
      const dangleOffset = Math.sin(newGlyph.danglePhase) * glyph.dangleAmplitude;
      newGlyph.x += dandleOffset;
      
      // Rotation
      newGlyph.rotation += glyph.rotationSpeed;
      
      // Pulse effect
      if (config.pulseEffect) {
        newGlyph.pulsePhase += 0.1;
        const pulseFactor = 1 + Math.sin(newGlyph.pulsePhase) * 0.2;
        newGlyph.fontSize = glyph.fontSize * pulseFactor;
      }
      
      // Trail effect
      if (config.trailEffect) {
        newGlyph.trail = [{ x: glyph.x, y: glyph.y }, ...glyph.trail.slice(0, glyph.maxTrailLength - 1)];
      }
      
      // Fade out as falling
      if (newGlyph.y > canvas.height * 0.3) {
        newGlyph.opacity = Math.max(0, newGlyph.opacity - config.fadeSpeed);
      }
      
      // Regenerate at top
      if (newGlyph.y > canvas.height || newGlyph.opacity <= 0) {
        newGlyph.x = Math.random() * canvas.width;
        newGlyph.y = -50;
        newGlyph.vy = Math.random() * 2 + 1;
        newGlyph.opacity = 1;
        newGlyph.trail = [];
        newGlyph.glyph = matrixGlyphs[Math.floor(Math.random() * matrixGlyphs.length)];
      }
      
      // Wrap around horizontally
      if (newGlyph.x < -50) newGlyph.x = canvas.width + 50;
      if (newGlyph.x > canvas.width + 50) newGlyph.x = -50;
      
      // Color variation based on position
      const positionRatio = newGlyph.y / canvas.height;
      if (positionRatio < 0.3) {
        newGlyph.color = colors.primary;
      } else if (positionRatio < 0.6) {
        newGlyph.color = colors.secondary;
      } else {
        newGlyph.color = colors.tertiary;
      }
      
      return newGlyph;
    });
  }, [config, config.colorScheme]);

  const renderGlyphs = useCallback(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const colors = colorSchemes[config.colorScheme];

    // Clear canvas
    ctx.fillStyle = config.backgroundColor;
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Apply glow effect
    if (config.glowIntensity > 0) {
      ctx.shadowBlur = 20 * config.glowIntensity;
      ctx.shadowColor = colors.glow;
    }

    // Draw each glyph
    glyphsRef.current.forEach(glyph => {
      // Draw trail
      if (config.trailEffect && glyph.trail.length > 0) {
        glyph.trail.forEach((point, index) => {
          const trailOpacity = (1 - index / glyph.trail.length) * glyph.opacity * 0.3;
          ctx.save();
          ctx.globalAlpha = trailOpacity;
          ctx.font = `${glyph.fontSize * 0.8}px monospace`;
          ctx.fillStyle = glyph.color;
          ctx.translate(point.x, point.y);
          ctx.rotate(glyph.rotation);
          ctx.fillText(glyph.glyph, 0, 0);
          ctx.restore();
        });
      }

      // Draw main glyph
      ctx.save();
      ctx.globalAlpha = glyph.opacity;
      ctx.font = `${glyph.fontSize}px monospace`;
      ctx.fillStyle = glyph.color;
      ctx.translate(glyph.x, glyph.y);
      ctx.rotate(glyph.rotation);
      
      // Add center line effect for main glyphs
      if (Math.random() > 0.95) {
        ctx.strokeStyle = colors.primary;
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(0, -glyph.fontSize / 2);
        ctx.lineTo(0, glyph.fontSize / 2);
        ctx.stroke();
      }
      
      ctx.fillText(glyph.glyph, 0, 0);
      ctx.restore();
    });

    // Reset shadow
    ctx.shadowBlur = 0;
    ctx.shadowColor = 'transparent';
  }, [config, config.backgroundColor, config.glowIntensity]);

  const animate = useCallback(() => {
    if (!isPaused) {
      updateGlyphs();
      renderGlyphs();
    }
    animationRef.current = requestAnimationFrame(animate);
  }, [isPaused, updateGlyphs, renderGlyphs]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const handleResize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      initializeGlyphs();
    };

    handleResize();
    window.addEventListener('resize', handleResize);

    animationRef.current = requestAnimationFrame(animate);

    return () => {
      window.removeEventListener('resize', handleResize);
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [animate, initializeGlyphs]);

  useEffect(() => {
    initializeGlyphs();
  }, [initializeGlyphs]);

  const handleConfigChange = (key, value) => {
    setConfig(prev => ({ ...prev, [key]: value }));
  };

  const exportConfig = () => {
    const dataStr = JSON.stringify(config, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    const exportFileDefaultName = 'matrix-curtain-config.json';
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  };

  const importConfig = (event) => {
    const file = event.target.files[0];
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const importedConfig = JSON.parse(e.target.result);
        setConfig(prev => ({ ...prev, ...importedConfig }));
      } catch (error) {
        console.error('Invalid config file:', error);
      }
    };
    reader.readAsText(file);
  };

  const resetConfig = () => {
    setConfig({
      density: 50,
      speed: 1.0,
      gravity: 0.5,
      wind: 0,
      fadeSpeed: 0.02,
      glowIntensity: 0.8,
      colorScheme: 'matrix',
      backgroundColor: 'rgba(0, 0, 0, 0.9)',
      showControls: true,
      physicsEnabled: true,
      collisionDetection: false,
      trailEffect: true,
      pulseEffect: true
    });
  };

  const togglePause = () => {
    setIsPaused(prev => !prev);
  };

  if (!isOpen) {
    return null;
  }

  return (
    <div className="matrix-curtain-overlay">
      <canvas
        ref={canvasRef}
        className="matrix-curtain-canvas"
      />
      
      {/* Control Panel */}
      <div className="curtain-controls">
        <div className="control-header">
          <div className="control-title">
            <Code size={20} />
            <span>Matrix Curtain Controls</span>
          </div>
          
          <div className="control-actions">
            <button
              onClick={togglePause}
              className="control-btn"
              title={isPaused ? 'Play' : 'Pause'}
            >
              {isPaused ? <Play size={16} /> : <Pause size={16} />}
            </button>
            
            <button
              onClick={() => setSettingsOpen(!settingsOpen)}
              className="control-btn"
              title="Settings"
            >
              <Settings size={16} />
            </button>
            
            <button
              onClick={onToggle}
              className="control-btn close-btn"
              title="Close Curtain"
            >
              <X size={16} />
            </button>
          </div>
        </div>
        
        {/* Quick Status */}
        <div className="quick-status">
          <div className="status-item">
            <span className="status-label">Glyphs:</span>
            <span className="status-value">{glyphsRef.current.length}</span>
          </div>
          <div className="status-item">
            <span className="status-label">FPS:</span>
            <span className="status-value">60</span>
          </div>
          <div className="status-item">
            <span className="status-label">Physics:</span>
            <span className={`status-value ${config.physicsEnabled ? 'active' : 'inactive'}`}>
              {config.physicsEnabled ? 'ON' : 'OFF'}
            </span>
          </div>
        </div>
      </div>

      {/* Settings Panel */}
      {settingsOpen && (
        <div className="settings-panel">
          <div className="settings-header">
            <h3>Curtain Configuration</h3>
            <button
              onClick={() => setSettingsOpen(false)}
              className="close-settings"
            >
              <X size={16} />
            </button>
          </div>
          
          <div className="settings-content">
            {/* Physics Settings */}
            <div className="settings-section">
              <h4>Physics</h4>
              
              <div className="setting-group">
                <label>Gravity: {config.gravity.toFixed(2)}</label>
                <input
                  type="range"
                  min="0"
                  max="2"
                  step="0.1"
                  value={config.gravity}
                  onChange={(e) => handleConfigChange('gravity', parseFloat(e.target.value))}
                />
              </div>
              
              <div className="setting-group">
                <label>Wind: {config.wind.toFixed(2)}</label>
                <input
                  type="range"
                  min="-2"
                  max="2"
                  step="0.1"
                  value={config.wind}
                  onChange={(e) => handleConfigChange('wind', parseFloat(e.target.value))}
                />
              </div>
              
              <div className="setting-group">
                <label>Speed: {config.speed.toFixed(1)}x</label>
                <input
                  type="range"
                  min="0.1"
                  max="3"
                  step="0.1"
                  value={config.speed}
                  onChange={(e) => handleConfigChange('speed', parseFloat(e.target.value))}
                />
              </div>
              
              <div className="setting-group">
                <label>
                  <input
                    type="checkbox"
                    checked={config.physicsEnabled}
                    onChange={(e) => handleConfigChange('physicsEnabled', e.target.checked)}
                  />
                  Enable Physics
                </label>
              </div>
              
              <div className="setting-group">
                <label>
                  <input
                    type="checkbox"
                    checked={config.collisionDetection}
                    onChange={(e) => handleConfigChange('collisionDetection', e.target.checked)}
                  />
                  Collision Detection
                </label>
              </div>
            </div>

            {/* Visual Settings */}
            <div className="settings-section">
              <h4>Visual</h4>
              
              <div className="setting-group">
                <label>Density: {config.density}%</label>
                <input
                  type="range"
                  min="10"
                  max="100"
                  step="5"
                  value={config.density}
                  onChange={(e) => handleConfigChange('density', parseInt(e.target.value))}
                />
              </div>
              
              <div className="setting-group">
                <label>Fade Speed: {config.fadeSpeed.toFixed(3)}</label>
                <input
                  type="range"
                  min="0.001"
                  max="0.1"
                  step="0.001"
                  value={config.fadeSpeed}
                  onChange={(e) => handleConfigChange('fadeSpeed', parseFloat(e.target.value))}
                />
              </div>
              
              <div className="setting-group">
                <label>Glow Intensity: {config.glowIntensity.toFixed(1)}</label>
                <input
                  type="range"
                  min="0"
                  max="2"
                  step="0.1"
                  value={config.glowIntensity}
                  onChange={(e) => handleConfigChange('glowIntensity', parseFloat(e.target.value))}
                />
              </div>
              
              <div className="setting-group">
                <label>
                  <input
                    type="checkbox"
                    checked={config.trailEffect}
                    onChange={(e) => handleConfigChange('trailEffect', e.target.checked)}
                  />
                  Trail Effect
                </label>
              </div>
              
              <div className="setting-group">
                <label>
                  <input
                    type="checkbox"
                    checked={config.pulseEffect}
                    onChange={(e) => handleConfigChange('pulseEffect', e.target.checked)}
                  />
                  Pulse Effect
                </label>
              </div>
            </div>

            {/* Color Scheme */}
            <div className="settings-section">
              <h4>Color Scheme</h4>
              
              <div className="color-schemes">
                {Object.keys(colorSchemes).map(scheme => (
                  <button
                    key={scheme}
                    className={`color-scheme-btn ${config.colorScheme === scheme ? 'active' : ''}`}
                    onClick={() => handleConfigChange('colorScheme', scheme)}
                    style={{
                      background: `linear-gradient(135deg, ${colorSchemes[scheme].primary}, ${colorSchemes[scheme].tertiary})`
                    }}
                  >
                    {scheme.charAt(0).toUpperCase() + scheme.slice(1)}
                  </button>
                ))}
              </div>
              
              <div className="setting-group">
                <label>Background Opacity</label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={parseFloat(config.backgroundColor.match(/[\d.]+/)?.[0] || 0.9)}
                  onChange={(e) => {
                    const opacity = parseFloat(e.target.value);
                    handleConfigChange('backgroundColor', `rgba(0, 0, 0, ${opacity})`);
                  }}
                />
              </div>
            </div>

            {/* Config Management */}
            <div className="settings-section">
              <h4>Configuration</h4>
              
              <div className="config-actions">
                <button onClick={exportConfig} className="config-btn">
                  <Download size={16} />
                  Export Config
                </button>
                
                <label className="config-btn">
                  <Upload size={16} />
                  Import Config
                  <input
                    type="file"
                    accept=".json"
                    onChange={importConfig}
                    style={{ display: 'none' }}
                  />
                </label>
                
                <button onClick={resetConfig} className="config-btn">
                  <RotateCcw size={16} />
                  Reset to Default
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Open/Close Button */}
      <button
        onClick={onToggle}
        className="curtain-toggle-btn"
        title={isOpen ? 'Close Curtain' : 'Open Curtain'}
      >
        <div className="toggle-icon">
          {isOpen ? (
            <Eye size={24} />
          ) : (
            <EyeOff size={24} />
          )}
        </div>
        <div className="toggle-text">
          {isOpen ? 'Hide' : 'Show'}
        </div>
      </button>
    </div>
  );
};

export default MatrixCurtain;