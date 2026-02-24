import React, { useState, useEffect, useRef, useCallback } from 'react';
import { 
  Settings, 
  Save, 
  Upload, 
  Download, 
  RotateCcw, 
  Zap, 
  Eye, 
  EyeOff, 
  Monitor, 
  Palette, 
  Code, 
  Sliders, 
  Layers, 
  Grid3X3, 
  Sparkles,
  ChevronDown,
  ChevronUp,
  X,
  Check,
  AlertCircle,
  Info,
  Lock,
  Unlock
} from 'lucide-react';

const AdvancedCurtainSettings = ({ 
  isOpen, 
  onClose, 
  config, 
  onConfigChange, 
  onApplyPreset,
  onExportConfig,
  onImportConfig 
}) => {
  const [activeSection, setActiveSection] = useState('physics');
  const [isPresetMenuOpen, setIsPresetMenuOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [unsavedChanges, setUnsavedChanges] = useState(false);
  const [previewMode, setPreviewMode] = useState(false);
  const fileInputRef = useRef(null);

  const settingsSections = {
    physics: {
      title: 'Physics Engine',
      icon: Sliders,
      description: 'Control movement and behavior of glyphs'
    },
    visual: {
      title: 'Visual Effects',
      icon: Palette,
      description: 'Customize appearance and styling'
    },
    performance: {
      title: 'Performance',
      icon: Zap,
      description: 'Optimize rendering and resource usage'
    },
    advanced: {
      title: 'Advanced',
      icon: Code,
      description: 'Developer-level configurations'
    },
    presets: {
      title: 'Presets',
      icon: Sparkles,
      description: 'Quickly apply predefined configurations'
    }
  };

  const enhancedPresets = {
    cinematic: {
      name: 'Cinematic',
      description: 'Movie-quality matrix effect',
      icon: '🎬',
      config: {
        density: 70,
        speed: 0.8,
        gravity: 0.7,
        wind: 0.2,
        fadeSpeed: 0.015,
        glowIntensity: 1.2,
        colorScheme: 'matrix',
        trailEffect: true,
        pulseEffect: false,
        particleCount: 100,
        motionBlur: true
      }
    },
    minimalist: {
      name: 'Minimalist',
      description: 'Clean and simple design',
      icon: '⚪',
      config: {
        density: 30,
        speed: 1.2,
        gravity: 0.3,
        wind: 0,
        fadeSpeed: 0.03,
        glowIntensity: 0.3,
        colorScheme: 'ice',
        trailEffect: false,
        pulseEffect: false,
        particleCount: 25,
        motionBlur: false
      }
    },
    intense: {
      name: 'Intense',
      description: 'Maximum visual impact',
      icon: '🔥',
      config: {
        density: 90,
        speed: 1.5,
        gravity: 1.2,
        wind: 0.5,
        fadeSpeed: 0.01,
        glowIntensity: 2.0,
        colorScheme: 'fire',
        trailEffect: true,
        pulseEffect: true,
        particleCount: 200,
        motionBlur: true
      }
    },
    neon: {
      name: 'Neon Nights',
      description: 'Cyberpunk aesthetic',
      icon: '🌃',
      config: {
        density: 60,
        speed: 1.0,
        gravity: 0.5,
        wind: 0.3,
        fadeSpeed: 0.018,
        glowIntensity: 1.8,
        colorScheme: 'neon',
        trailEffect: true,
        pulseEffect: true,
        particleCount: 75,
        motionBlur: true
      }
    },
    retro: {
      name: 'Retro Terminal',
      description: 'Classic computer terminal',
      icon: '💻',
      config: {
        density: 45,
        speed: 0.6,
        gravity: 0.4,
        wind: 0,
        fadeSpeed: 0.025,
        glowIntensity: 0.6,
        colorScheme: 'matrix',
        trailEffect: false,
        pulseEffect: false,
        particleCount: 40,
        motionBlur: false,
        monospaceFont: true,
        scanLines: true
      }
    },
    quantum: {
      name: 'Quantum',
      description: 'Futuristic quantum effect',
      icon: '⚛️',
      config: {
        density: 80,
        speed: 2.0,
        gravity: 0,
        wind: 0.1,
        fadeSpeed: 0.008,
        glowIntensity: 1.5,
        colorScheme: 'neon',
        trailEffect: true,
        pulseEffect: true,
        particleCount: 150,
        motionBlur: true,
        quantumEffect: true
      }
    }
  };

  const [customPresets, setCustomPresets] = useState(() => {
    const saved = localStorage.getItem('curtain-custom-presets');
    return saved ? JSON.parse(saved) : [];
  });

  const handleConfigChange = useCallback((key, value) => {
    setUnsavedChanges(true);
    onConfigChange?.(key, value);
  }, [onConfigChange]);

  const handlePresetApply = useCallback((preset) => {
    Object.entries(preset.config).forEach(([key, value]) => {
      handleConfigChange(key, value);
    });
    setUnsavedChanges(false);
    onApplyPreset?.(preset.name);
  }, [handleConfigChange, onApplyPreset]);

  const saveCustomPreset = useCallback(() => {
    const presetName = prompt('Enter preset name:');
    if (!presetName) return;

    const newPreset = {
      id: Date.now(),
      name: presetName,
      description: 'Custom preset',
      icon: '⚡',
      config: { ...config },
      createdAt: new Date().toISOString()
    };

    const updatedPresets = [...customPresets, newPreset];
    setCustomPresets(updatedPresets);
    localStorage.setItem('curtain-custom-presets', JSON.stringify(updatedPresets));
    setUnsavedChanges(false);
  }, [config, customPresets]);

  const deleteCustomPreset = useCallback((presetId) => {
    const updatedPresets = customPresets.filter(p => p.id !== presetId);
    setCustomPresets(updatedPresets);
    localStorage.setItem('curtain-custom-presets', JSON.stringify(updatedPresets));
  }, [customPresets]);

  const resetToDefaults = useCallback(() => {
    const defaultConfig = {
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
    };

    Object.entries(defaultConfig).forEach(([key, value]) => {
      handleConfigChange(key, value);
    });
    setUnsavedChanges(false);
  }, [handleConfigChange]);

  const renderPhysicsSection = () => (
    <div className="settings-section-content">
      <div className="setting-group advanced">
        <label className="setting-label">
          <span>Gravity System</span>
          <div className="setting-info">
            <Info size={14} />
            <div className="tooltip">Controls how fast glyphs fall. Higher values create faster falling.</div>
          </div>
        </label>
        <div className="setting-controls">
          <input
            type="range"
            min="0"
            max="2"
            step="0.01"
            value={config.gravity || 0.5}
            onChange={(e) => handleConfigChange('gravity', parseFloat(e.target.value))}
            className="setting-slider"
          />
          <div className="setting-value">
            <input
              type="number"
              min="0"
              max="2"
              step="0.01"
              value={config.gravity || 0.5}
              onChange={(e) => handleConfigChange('gravity', parseFloat(e.target.value))}
              className="setting-number"
            />
          </div>
        </div>
      </div>

      <div className="setting-group advanced">
        <label className="setting-label">
          <span>Wind Force</span>
          <div className="setting-info">
            <Info size={14} />
            <div className="tooltip">Horizontal wind effect. Negative values blow left, positive blow right.</div>
          </div>
        </label>
        <div className="setting-controls">
          <input
            type="range"
            min="-2"
            max="2"
            step="0.01"
            value={config.wind || 0}
            onChange={(e) => handleConfigChange('wind', parseFloat(e.target.value))}
            className="setting-slider"
          />
          <div className="setting-value">
            <input
              type="number"
              min="-2"
              max="2"
              step="0.01"
              value={config.wind || 0}
              onChange={(e) => handleConfigChange('wind', parseFloat(e.target.value))}
              className="setting-number"
            />
          </div>
        </div>
      </div>

      <div className="setting-group advanced">
        <label className="setting-label">
          <span>Turbulence</span>
          <div className="setting-info">
            <Info size={14} />
            <div className="tooltip">Adds random variations to glyph movement for more natural motion.</div>
          </div>
        </label>
        <div className="setting-controls">
          <input
            type="range"
            min="0"
            max="1"
            step="0.01"
            value={config.turbulence || 0.1}
            onChange={(e) => handleConfigChange('turbulence', parseFloat(e.target.value))}
            className="setting-slider"
          />
          <div className="setting-value">
            <input
              type="number"
              min="0"
              max="1"
              step="0.01"
              value={config.turbulence || 0.1}
              onChange={(e) => handleConfigChange('turbulence', parseFloat(e.target.value))}
              className="setting-number"
            />
          </div>
        </div>
      </div>

      <div className="setting-group toggle">
        <label className="setting-label">
          <span>Collision Detection</span>
          <div className="setting-info">
            <Info size={14} />
            <div className="tooltip">Enable glyph interactions. May impact performance with many glyphs.</div>
          </div>
        </label>
        <div className="toggle-switch">
          <input
            type="checkbox"
            checked={config.collisionDetection || false}
            onChange={(e) => handleConfigChange('collisionDetection', e.target.checked)}
          />
          <span className="toggle-slider"></span>
        </div>
      </div>

      <div className="setting-group toggle">
        <label className="setting-label">
          <span>Quantum Effect</span>
          <div className="setting-info">
            <Info size={14} />
            <div className="tooltip">Adds quantum uncertainty to glyph positions for futuristic effect.</div>
          </div>
        </label>
        <div className="toggle-switch">
          <input
            type="checkbox"
            checked={config.quantumEffect || false}
            onChange={(e) => handleConfigChange('quantumEffect', e.target.checked)}
          />
          <span className="toggle-slider"></span>
        </div>
      </div>
    </div>
  );

  const renderVisualSection = () => (
    <div className="settings-section-content">
      <div className="setting-group advanced">
        <label className="setting-label">
          <span>Glyph Density</span>
          <div className="setting-info">
            <Info size={14} />
            <div className="tooltip">Number of glyphs displayed. Higher values create denser effects.</div>
          </div>
        </label>
        <div className="setting-controls">
          <input
            type="range"
            min="10"
            max="150"
            step="1"
            value={config.density || 50}
            onChange={(e) => handleConfigChange('density', parseInt(e.target.value))}
            className="setting-slider"
          />
          <div className="setting-value">
            <input
              type="number"
              min="10"
              max="150"
              value={config.density || 50}
              onChange={(e) => handleConfigChange('density', parseInt(e.target.value))}
              className="setting-number"
            />
          </div>
        </div>
      </div>

      <div className="setting-group advanced">
        <label className="setting-label">
          <span>Animation Speed</span>
          <div className="setting-info">
            <Info size={14} />
            <div className="tooltip">Overall animation speed multiplier. Higher values create faster movement.</div>
          </div>
        </label>
        <div className="setting-controls">
          <input
            type="range"
            min="0.1"
            max="5"
            step="0.1"
            value={config.speed || 1.0}
            onChange={(e) => handleConfigChange('speed', parseFloat(e.target.value))}
            className="setting-slider"
          />
          <div className="setting-value">
            <input
              type="number"
              min="0.1"
              max="5"
              step="0.1"
              value={config.speed || 1.0}
              onChange={(e) => handleConfigChange('speed', parseFloat(e.target.value))}
              className="setting-number"
            />
          </div>
        </div>
      </div>

      <div className="setting-group advanced">
        <label className="setting-label">
          <span>Glow Intensity</span>
          <div className="setting-info">
            <Info size={14} />
            <div className="tooltip">Brightness of glow effect. Set to 0 to disable.</div>
          </div>
        </label>
        <div className="setting-controls">
          <input
            type="range"
            min="0"
            max="3"
            step="0.1"
            value={config.glowIntensity || 0.8}
            onChange={(e) => handleConfigChange('glowIntensity', parseFloat(e.target.value))}
            className="setting-slider"
          />
          <div className="setting-value">
            <input
              type="number"
              min="0"
              max="3"
              step="0.1"
              value={config.glowIntensity || 0.8}
              onChange={(e) => handleConfigChange('glowIntensity', parseFloat(e.target.value))}
              className="setting-number"
            />
          </div>
        </div>
      </div>

      <div className="setting-group advanced">
        <label className="setting-label">
          <span>Motion Blur</span>
          <div className="setting-info">
            <Info size={14} />
            <div className="tooltip">Adds motion blur for smoother appearance. May impact performance.</div>
          </div>
        </label>
        <div className="toggle-switch">
          <input
            type="checkbox"
            checked={config.motionBlur || false}
            onChange={(e) => handleConfigChange('motionBlur', e.target.checked)}
          />
          <span className="toggle-slider"></span>
        </div>
      </div>

      <div className="setting-group advanced">
        <label className="setting-label">
          <span>Font Family</span>
          <div className="setting-info">
            <Info size={14} />
            <div className="tooltip">Choose font style for glyphs. Monospace creates terminal look.</div>
          </div>
        </label>
        <select
          value={config.fontFamily || 'monospace'}
          onChange={(e) => handleConfigChange('fontFamily', e.target.value)}
          className="setting-select"
        >
          <option value="monospace">Monospace (Terminal)</option>
          <option value="system-ui">System UI</option>
          <option value="cursive">Cursive</option>
          <option value="fantasy">Fantasy</option>
        </select>
      </div>

      <div className="setting-group toggle">
        <label className="setting-label">
          <span>Scan Lines</span>
          <div className="setting-info">
            <Info size={14} />
            <div className="tooltip">Adds retro CRT scan line effect to the curtain.</div>
          </div>
        </label>
        <div className="toggle-switch">
          <input
            type="checkbox"
            checked={config.scanLines || false}
            onChange={(e) => handleConfigChange('scanLines', e.target.checked)}
          />
          <span className="toggle-slider"></span>
        </div>
      </div>
    </div>
  );

  const renderPerformanceSection = () => (
    <div className="settings-section-content">
      <div className="performance-metrics">
        <div className="metric-card">
          <div className="metric-header">
            <Monitor size={16} />
            <span>Performance</span>
          </div>
          <div className="metric-value">
            <span className="performance-score">{config.performanceScore || 85}</span>
            <span className="performance-label">Score</span>
          </div>
        </div>
        
        <div className="metric-card">
          <div className="metric-header">
            <Grid3X3 size={16} />
            <span>Glyphs</span>
          </div>
          <div className="metric-value">
            <span>{config.density || 50}</span>
            <span className="metric-label">Active</span>
          </div>
        </div>
        
        <div className="metric-card">
          <div className="metric-header">
            <Zap size={16} />
            <span>FPS</span>
          </div>
          <div className="metric-value">
            <span className="fps-value">60</span>
            <span className="metric-label">Target</span>
          </div>
        </div>
      </div>

      <div className="setting-group advanced">
        <label className="setting-label">
          <span>Quality Mode</span>
          <div className="setting-info">
            <Info size={14} />
            <div className="tooltip">Balance between visual quality and performance.</div>
          </div>
        </label>
        <div className="quality-modes">
          {['low', 'medium', 'high', 'ultra'].map(quality => (
            <button
              key={quality}
              className={`quality-mode ${config.qualityMode === quality ? 'active' : ''}`}
              onClick={() => handleConfigChange('qualityMode', quality)}
            >
              <span className="quality-name">{quality.charAt(0).toUpperCase() + quality.slice(1)}</span>
              <span className="quality-desc">
                {quality === 'low' && 'Best Performance'}
                {quality === 'medium' && 'Balanced'}
                {quality === 'high' && 'Enhanced Visuals'}
                {quality === 'ultra' && 'Maximum Quality'}
              </span>
            </button>
          ))}
        </div>
      </div>

      <div className="setting-group advanced">
        <label className="setting-label">
          <span>Particle Limit</span>
          <div className="setting-info">
            <Info size={14} />
            <div className="tooltip">Maximum number of particles for effects. Lower values improve performance.</div>
          </div>
        </label>
        <div className="setting-controls">
          <input
            type="range"
            min="50"
            max="500"
            step="10"
            value={config.particleCount || 100}
            onChange={(e) => handleConfigChange('particleCount', parseInt(e.target.value))}
            className="setting-slider"
          />
          <div className="setting-value">
            <input
              type="number"
              min="50"
              max="500"
              value={config.particleCount || 100}
              onChange={(e) => handleConfigChange('particleCount', parseInt(e.target.value))}
              className="setting-number"
            />
          </div>
        </div>
      </div>

      <div className="setting-group toggle">
        <label className="setting-label">
          <span>GPU Acceleration</span>
          <div className="setting-info">
            <Info size={14} />
            <div className="tooltip">Use hardware acceleration for better performance.</div>
          </div>
        </label>
        <div className="toggle-switch">
          <input
            type="checkbox"
            checked={config.gpuAcceleration !== false}
            onChange={(e) => handleConfigChange('gpuAcceleration', e.target.checked)}
          />
          <span className="toggle-slider"></span>
        </div>
      </div>

      <div className="setting-group toggle">
        <label className="setting-label">
          <span>Adaptive Quality</span>
          <div className="setting-info">
            <Info size={14} />
            <div className="tooltip">Automatically adjust quality based on performance.</div>
          </div>
        </label>
        <div className="toggle-switch">
          <input
            type="checkbox"
            checked={config.adaptiveQuality || false}
            onChange={(e) => handleConfigChange('adaptiveQuality', e.target.checked)}
          />
          <span className="toggle-slider"></span>
        </div>
      </div>
    </div>
  );

  const renderAdvancedSection = () => (
    <div className="settings-section-content">
      <div className="advanced-sections">
        <div className="advanced-section">
          <h4>Developer Options</h4>
          
          <div className="setting-group">
            <label className="setting-label">
              <span>Custom Shader</span>
              <div className="setting-info">
                <Info size={14} />
                <div className="tooltip">Apply custom WebGL shaders for advanced effects.</div>
              </div>
            </label>
            <textarea
              value={config.customShader || ''}
              onChange={(e) => handleConfigChange('customShader', e.target.value)}
              placeholder="Enter custom GLSL shader code..."
              className="setting-textarea"
              rows={4}
            />
          </div>

          <div className="setting-group">
            <label className="setting-label">
              <span>Custom Glyph Set</span>
              <div className="setting-info">
                <Info size={14} />
                <div className="tooltip">Define custom characters for the matrix effect.</div>
              </div>
            </label>
            <input
              type="text"
              value={config.customGlyphs || ''}
              onChange={(e) => handleConfigChange('customGlyphs', e.target.value)}
              placeholder="Enter custom characters..."
              className="setting-input"
            />
          </div>
        </div>

        <div className="advanced-section">
          <h4>Debug Information</h4>
          
          <div className="debug-info">
            <div className="debug-item">
              <span className="debug-label">Canvas Size:</span>
              <span className="debug-value">{config.canvasWidth || 1920} × {config.canvasHeight || 1080}</span>
            </div>
            <div className="debug-item">
              <span className="debug-label">Render Time:</span>
              <span className="debug-value">{config.renderTime || 16.7}ms</span>
            </div>
            <div className="debug-item">
              <span className="debug-label">Memory Usage:</span>
              <span className="debug-value">{config.memoryUsage || 45}MB</span>
            </div>
            <div className="debug-item">
              <span className="debug-label">Active Shaders:</span>
              <span className="debug-value">{config.activeShaders || 3}</span>
            </div>
          </div>

          <div className="setting-group toggle">
            <label className="setting-label">
              <span>Show Debug Overlay</span>
            </label>
            <div className="toggle-switch">
              <input
                type="checkbox"
                checked={config.showDebugOverlay || false}
                onChange={(e) => handleConfigChange('showDebugOverlay', e.target.checked)}
              />
              <span className="toggle-slider"></span>
            </div>
          </div>

          <div className="setting-group toggle">
            <label className="setting-label">
              <span>Enable Profiling</span>
            </label>
            <div className="toggle-switch">
              <input
                type="checkbox"
                checked={config.enableProfiling || false}
                onChange={(e) => handleConfigChange('enableProfiling', e.target.checked)}
              />
              <span className="toggle-slider"></span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderPresetsSection = () => (
    <div className="settings-section-content">
      <div className="preset-categories">
        <div className="preset-category">
          <h4>Built-in Presets</h4>
          <div className="preset-grid">
            {Object.entries(enhancedPresets).map(([key, preset]) => (
              <div
                key={key}
                className="preset-card"
                onClick={() => handlePresetApply(preset)}
              >
                <div className="preset-header">
                  <span className="preset-icon">{preset.icon}</span>
                  <span className="preset-name">{preset.name}</span>
                </div>
                <p className="preset-description">{preset.description}</p>
                <div className="preset-preview">
                  <div className="preview-colors">
                    <div 
                      className="preview-color" 
                      style={{ backgroundColor: getColorScheme(preset.config.colorScheme).primary }}
                    ></div>
                    <div 
                      className="preview-color" 
                      style={{ backgroundColor: getColorScheme(preset.config.colorScheme).secondary }}
                    ></div>
                    <div 
                      className="preview-color" 
                      style={{ backgroundColor: getColorScheme(preset.config.colorScheme).tertiary }}
                    ></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="preset-category">
          <div className="category-header">
            <h4>Custom Presets</h4>
            <button
              onClick={saveCustomPreset}
              className="save-preset-btn"
            >
              <Save size={14} />
              Save Current
            </button>
          </div>
          
          {customPresets.length === 0 ? (
            <div className="no-presets">
              <AlertCircle size={24} />
              <p>No custom presets saved yet</p>
              <p>Adjust settings and click "Save Current" to create your first preset</p>
            </div>
          ) : (
            <div className="preset-grid">
              {customPresets.map(preset => (
                <div key={preset.id} className="preset-card custom">
                  <div className="preset-header">
                    <span className="preset-icon">{preset.icon}</span>
                    <span className="preset-name">{preset.name}</span>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        deleteCustomPreset(preset.id);
                      }}
                      className="delete-preset-btn"
                    >
                      <X size={14} />
                    </button>
                  </div>
                  <p className="preset-description">{preset.description}</p>
                  <div className="preset-meta">
                    <span className="preset-date">
                      {new Date(preset.createdAt).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="preset-actions">
        <div className="import-export">
          <button
            onClick={() => fileInputRef.current?.click()}
            className="action-btn import"
          >
            <Upload size={16} />
            Import Preset
          </button>
          <input
            ref={fileInputRef}
            type="file"
            accept=".json"
            onChange={(e) => {
              const file = e.target.files[0];
              if (file) {
                const reader = new FileReader();
                reader.onload = (event) => {
                  try {
                    const preset = JSON.parse(event.target.result);
                    handlePresetApply(preset);
                  } catch (error) {
                    console.error('Invalid preset file:', error);
                  }
                };
                reader.readAsText(file);
              }
            }}
            style={{ display: 'none' }}
          />
          
          <button
            onClick={() => {
              const preset = {
                name: 'Current Configuration',
                description: 'Exported from curtain settings',
                icon: '⚙️',
                config: config
              };
              onExportConfig?.(preset);
            }}
            className="action-btn export"
          >
            <Download size={16} />
            Export Settings
          </button>
        </div>
      </div>
    </div>
  );

  const getColorScheme = (schemeName) => {
    const schemes = {
      matrix: { primary: '#00ff41', secondary: '#008f11', tertiary: '#004d0a' },
      cyberpunk: { primary: '#00ffff', secondary: '#ff00ff', tertiary: '#ffff00' },
      fire: { primary: '#ff6b35', secondary: '#f77825', tertiary: '#f4b942' },
      ice: { primary: '#00bfff', secondary: '#87ceeb', tertiary: '#b0e0e6' },
      neon: { primary: '#ff00ff', secondary: '#00ff00', tertiary: '#0000ff' },
      solar: { primary: '#ffeb3b', secondary: '#ff9800', tertiary: '#ff5722' }
    };
    return schemes[schemeName] || schemes.matrix;
  };

  const renderSectionContent = () => {
    switch (activeSection) {
      case 'physics': return renderPhysicsSection();
      case 'visual': return renderVisualSection();
      case 'performance': return renderPerformanceSection();
      case 'advanced': return renderAdvancedSection();
      case 'presets': return renderPresetsSection();
      default: return null;
    }
  };

  if (!isOpen) return null;

  return (
    <div className="advanced-curtain-settings-overlay">
      <div className="advanced-curtain-settings">
        <div className="settings-header">
          <div className="header-left">
            <h2>Curtain Settings</h2>
            <div className="header-actions">
              <button
                onClick={() => setPreviewMode(!previewMode)}
                className={`preview-btn ${previewMode ? 'active' : ''}`}
                title="Toggle preview mode"
              >
                <Eye size={16} />
              </button>
              {unsavedChanges && (
                <div className="unsaved-indicator">
                  <AlertCircle size={14} />
                  <span>Unsaved changes</span>
                </div>
              )}
            </div>
          </div>
          
          <div className="header-right">
            <button
              onClick={resetToDefaults}
              className="reset-btn"
              title="Reset to default settings"
            >
              <RotateCcw size={16} />
            </button>
            
            <button
              onClick={onClose}
              className="close-btn"
            >
              <X size={20} />
            </button>
          </div>
        </div>

        <div className="settings-body">
          <div className="settings-sidebar">
            <div className="section-list">
              {Object.entries(settingsSections).map(([key, section]) => (
                <button
                  key={key}
                  className={`section-btn ${activeSection === key ? 'active' : ''}`}
                  onClick={() => setActiveSection(key)}
                >
                  <section.icon size={18} />
                  <div className="section-info">
                    <span className="section-title">{section.title}</span>
                    <span className="section-description">{section.description}</span>
                  </div>
                </button>
              ))}
            </div>

            <div className="search-section">
              <input
                type="text"
                placeholder="Search settings..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="search-input"
              />
            </div>
          </div>

          <div className="settings-main">
            {renderSectionContent()}
          </div>
        </div>

        <div className="settings-footer">
          <div className="footer-info">
            <span>Atlantiplex Studio v2.5.0</span>
            <span>•</span>
            <span>Curtain Settings</span>
          </div>
          
          <div className="footer-actions">
            <button
              onClick={() => {
                // Apply settings and close
                setUnsavedChanges(false);
                onClose?.();
              }}
              className="apply-btn"
              disabled={!unsavedChanges}
            >
              <Check size={16} />
              Apply Changes
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdvancedCurtainSettings;