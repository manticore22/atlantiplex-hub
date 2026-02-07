import React, { useState, useEffect, useCallback } from 'react';
import { getPalette, getFontFamily } from './branding.ts';

export default function DarkModeSystem() {
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [themeSettings, setThemeSettings] = useState({
    primaryColor: '#00ff41',
    backgroundColor: '#0a0a0a',
    textColor: '#ffffff',
    accentColor: '#764ba2',
    customTheme: false
  });

  const presetThemes = {
    matrix: {
      name: 'Matrix',
      primary: '#00ff41',
      background: '#0a0a0a',
      text: '#ffffff',
      accent: '#764ba2'
    },
    neon: {
      name: 'Neon Lights',
      primary: '#00ffff',
      background: '#000000',
      text: '#ffffff',
      accent: '#ff00ff'
    },
    ocean: {
      name: 'Ocean Blue',
      primary: '#00b4d8',
      background: '#001f3f',
      text: '#ffffff',
      accent: '#0080ff'
    },
    forest: {
      name: 'Forest Night',
      primary: '#4ade80',
      background: '#1a1a1a',
      text: '#ffffff',
      accent: '#22c55e'
    },
    custom: {
      name: 'Custom Theme',
      primary: themeSettings.primaryColor,
      background: themeSettings.backgroundColor,
      text: themeSettings.textColor,
      accent: themeSettings.accentColor
    }
  };

  useEffect(() => {
    // Load theme from localStorage
    const savedTheme = localStorage.getItem('atlantiplex-theme');
    if (savedTheme) {
      const parsed = JSON.parse(savedTheme);
      if (parsed.name === 'custom') {
        setThemeSettings(parsed);
      } else {
        setIsDarkMode(parsed.isDarkMode || true);
      }
    }

    // Apply theme to document
    applyThemeToDocument();
  }, []);

  const applyThemeToDocument = useCallback(() => {
    const root = document.documentElement;
    const currentTheme = themeSettings.customTheme ? themeSettings : presetThemes[isDarkMode ? 'matrix' : 'light'];
    
    // Apply CSS custom properties
    root.style.setProperty('--primary-color', currentTheme.primary);
    root.style.setProperty('--background-color', currentTheme.background);
    root.style.setProperty('--text-color', currentTheme.text);
    root.style.setProperty('--accent-color', currentTheme.accent);
    
    // Apply data attributes
    root.setAttribute('data-theme', isDarkMode ? 'dark' : 'light');
    root.setAttribute('data-theme-name', currentTheme.name);
    
    // Add theme transition
    root.style.setProperty('--theme-transition', 'background-color 0.3s ease');
  }, [isDarkMode, themeSettings]);

  const toggleDarkMode = useCallback(() => {
    const newMode = !isDarkMode;
    setIsDarkMode(newMode);
    
    // Save to localStorage
    const themeToSave = themeSettings.customTheme ? themeSettings : presetThemes[newMode ? 'matrix' : 'light'];
    localStorage.setItem('atlantiplex-theme', JSON.stringify(themeToSave));
    
    // Apply immediately
    applyThemeToDocument();
  }, [isDarkMode, themeSettings]);

  const setPresetTheme = useCallback((themeName) => {
    const theme = presetThemes[themeName];
    setThemeSettings({ ...theme, customTheme: false });
    setIsDarkMode(themeName !== 'light');
    
    // Save to localStorage
    localStorage.setItem('atlantiplex-theme', JSON.stringify({ ...theme, isDarkMode: themeName !== 'light' }));
    
    applyThemeToDocument();
  }, []);

  const updateCustomTheme = useCallback((property, value) => {
    setThemeSettings(prev => {
      const updated = { ...prev, [property]: value };
      
      if (!prev.customTheme) {
        // If switching from preset to custom, copy current colors
        const currentTheme = isDarkMode ? presetThemes.matrix : presetThemes.light;
        updated.primaryColor = currentTheme.primary;
        updated.backgroundColor = currentTheme.background;
        updated.textColor = currentTheme.text;
        updated.accentColor = currentTheme.accent;
        updated.customTheme = true;
      }
      
      return updated;
    });
    
    setIsDarkMode(true);
    
    // Save custom theme
    localStorage.setItem('atlantiplex-theme', JSON.stringify({ ...themeSettings, [property]: value, customTheme: true }));
  }, [isDarkMode, themeSettings]);

  const resetToDefault = useCallback(() => {
    setThemeSettings(presetThemes.matrix);
    setIsDarkMode(true);
    
    localStorage.setItem('atlantiplex-theme', JSON.stringify({ ...presetThemes.matrix, isDarkMode: true }));
    applyThemeToDocument();
  }, []);

  return (
    <div style={{
      minHeight: '100vh',
      background: `var(--background-color)`,
      color: `var(--text-color)`,
      fontFamily: getFontFamily(),
      padding: '20px',
      transition: 'var(--theme-transition) 0.3s ease'
    }}>
      <style jsx>{`
        body {
          background: var(--background-color);
          color: var(--text-color);
          transition: var(--theme-transition) 0.3s ease;
        }
        
        .dark-mode-container {
          background: var(--background-color);
          color: var(--text-color);
          border: 1px solid var(--primary-color);
        }
        
        .theme-card {
          background: rgba(var(--primary-color), 0.1);
          border: 2px solid var(--accent-color);
          border-radius: 8px;
          transition: all 0.3s ease;
        }
        
        .theme-card:hover {
          background: rgba(var(--primary-color), 0.2);
          transform: translateY(-2px);
          box-shadow: 0 8px 25px rgba(var(--primary-color), 0.3);
        }
        
        .theme-card.active {
          background: var(--primary-color);
          color: var(--background-color);
          transform: scale(1.05);
        }
        
        .color-input {
          width: 50px;
          height: 50px;
          border: 2px solid var(--accent-color);
          border-radius: 4px;
          background: var(--background-color);
          cursor: pointer;
        }
        
        .toggle-switch {
          width: 60px;
          height: 30px;
          background: var(--accent-color);
          border-radius: 15px;
          position: relative;
          cursor: pointer;
          transition: all 0.3s ease;
        }
        
        .toggle-switch::before {
          content: '';
          position: absolute;
          width: 26px;
          height: 26px;
          border-radius: 50%;
          background: var(--background-color);
          top: 2px;
          left: 2px;
          transition: all 0.3s ease;
        }
        
        .toggle-switch.active::before {
          left: 32px;
          background: var(--primary-color);
        }
        
        .preview-box {
          width: 100%;
          height: 80px;
          border: 2px solid var(--accent-color);
          border-radius: 4px;
          background: var(--background-color);
          margin-top: 12px;
        }
        
        /* Dark mode specific styles */
        [data-theme="dark"] .theme-card {
          background: rgba(var(--primary-color), 0.05);
          border: 2px solid var(--accent-color);
        }
        
        [data-theme="dark"] .theme-card:hover {
          background: rgba(var(--primary-color), 0.1);
        }
        
        /* Animation for theme switching */
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.7; }
        }
        
        .theme-loading {
          animation: pulse 1s ease-in-out;
        }
      `}</style>

      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <h1 style={{ textAlign: 'center', marginBottom: '30px' }}>
          🌙 Dark Mode System
          <span style={{ fontSize: '16px', opacity: 0.7, marginLeft: '20px' }}>
            Professional theming with dark/light modes
          </span>
        </h1>

        {/* Theme Toggle */}
        <div style={{
          background: 'rgba(var(--primary-color), 0.1)',
          padding: '30px',
          borderRadius: '12px',
          marginBottom: '30px',
          textAlign: 'center',
          border: '1px solid var(--accent-color)'
        }}>
          <h2 style={{ marginBottom: '20px' }}>🎨 Theme Mode</h2>
          
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '20px' }}>
            <div>
              <div style={{ marginBottom: '10px' }}>
                <div style={{ fontSize: '24px', marginBottom: '10px' }}>
                  {isDarkMode ? '🌙' : '☀️'}
                </div>
                <strong>{isDarkMode ? 'Dark Mode' : 'Light Mode'}</strong>
              </div>
              
              <div
                onClick={toggleDarkMode}
                className={`toggle-switch ${isDarkMode ? 'active' : ''}`}
                style={{
                  position: 'relative',
                  marginBottom: '10px'
                }}
              />
            </div>
          </div>

          <div style={{ fontSize: '14px', opacity: 0.7 }}>
            Toggle between light and dark themes
          </div>
        </div>

        {/* Preset Themes */}
        <div style={{
          background: getPalette().surface,
          padding: '24px',
          borderRadius: '12px',
          marginBottom: '30px',
          border: '1px solid #00ff41'
        }}>
          <h2 style={{ marginBottom: '20px' }}>🎭 Preset Themes</h2>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginBottom: '20px' }}>
            {Object.entries(presetThemes).map(([key, theme]) => {
              const isActive = themeSettings.customTheme ? false : (
                (isDarkMode && key !== 'light') || (!isDarkMode && key === 'light')
              );
              
              return (
                <div
                  key={key}
                  onClick={() => setPresetTheme(key)}
                  className={`theme-card ${isActive ? 'active' : ''}`}
                  style={{ padding: '16px', textAlign: 'center' }}
                >
                  <div style={{ 
                    fontSize: '48px', 
                    marginBottom: '12px',
                    filter: theme.name === 'neon' ? 'drop-shadow(0 0 10px var(--primary-color))' : 'none'
                  }}>
                    {theme.name === 'neon' && (
                      <style jsx>{`
                        @keyframes neon {
                          0%, 100% { 
                            text-shadow: 0 0 5px var(--primary-color), 
                            0 0 10px var(--accent-color);
                          }
                        }
                      `}</style>
                    )}
                    {theme.name === 'ocean' && '🌊'}
                    {theme.name === 'forest' && '🌲'}
                    {theme.name === 'matrix' && '💚'}
                  </div>
                  
                  <div style={{ fontSize: '16px', fontWeight: 'bold' }}>
                    {theme.name}
                  </div>
                  
                  <div style={{ 
                    fontSize: '12px', 
                    opacity: 0.7, 
                    marginTop: '4px' 
                  }}>
                    {theme.name === 'matrix' && 'Digital rain, green code' }
                    {theme.name === 'neon' && 'Cyberpunk blue, glowing effects' }
                    {theme.name === 'ocean' && 'Deep ocean blues, calm focus' }
                    {theme.name === 'forest' && 'Natural greens, earth tones' }
                  </div>
                </div>
              </div>
              );
            })}
          </div>

          <div style={{ textAlign: 'center', marginTop: '16px', fontSize: '14px', opacity: 0.7 }}>
            Click any preset to apply instantly
          </div>
        </div>

        {/* Custom Theme Editor */}
        <div style={{
          background: getPalette().surface,
          padding: '24px',
          borderRadius: '12px',
          marginBottom: '30px',
          border: '1px solid #00ff41'
        }}>
          <h2 style={{ marginBottom: '20px' }}>🎨 Custom Theme Editor</h2>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px' }}>
            <div>
              <label>Primary Color</label>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginTop: '8px' }}>
                <input
                  type="color"
                  value={themeSettings.primaryColor}
                  onChange={(e) => updateCustomTheme('primaryColor', e.target.value)}
                  className="color-input"
                />
                <input
                  type="text"
                  value={themeSettings.primaryColor}
                  onChange={(e) => updateCustomTheme('primaryColor', e.target.value)}
                  style={{ 
                    background: getPalette().bg,
                    border: '1px solid #00ff41',
                    padding: '8px',
                    borderRadius: '4px',
                    color: getPalette().text,
                    fontFamily: 'monospace'
                  }}
                />
              </div>
            </div>

            <div>
              <label>Background Color</label>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginTop: '8px' }}>
                <input
                  type="color"
                  value={themeSettings.backgroundColor}
                  onChange={(e) => updateCustomTheme('backgroundColor', e.target.value)}
                  className="color-input"
                />
                <input
                  type="text"
                  value={themeSettings.backgroundColor}
                  onChange={(e) => updateCustomTheme('backgroundColor', e.target.value)}
                  style={{ 
                    background: getPalette().bg,
                    border: '1px solid #00ff41',
                    padding: '8px',
                    borderRadius: '4px',
                    color: getPalette().text,
                    fontFamily: 'monospace'
                  }}
                />
              </div>
            </div>

            <div>
              <label>Text Color</label>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginTop: '8px' }}>
                <input
                  type="color"
                  value={themeSettings.textColor}
                  onChange={(e) => updateCustomTheme('textColor', e.target.value)}
                  className="color-input"
                />
                <input
                  type="text"
                  value={themeSettings.textColor}
                  onChange={(e) => updateCustomTheme('textColor', e.target.value)}
                  style={{ 
                    background: getPalette().bg,
                    border: '1px solid #00ff41',
                    padding: '8px',
                    borderRadius: '4px',
                    color: getPalette().text,
                    fontFamily: 'monospace'
                  }}
                />
              </div>
            </div>

            <div>
              <label>Accent Color</label>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginTop: '8px' }}>
                <input
                  type="color"
                  value={themeSettings.accentColor}
                  onChange={(e) => updateCustomTheme('accentColor', e.target.value)}
                  className="color-input"
                />
                <input
                  type="text"
                  value={themeSettings.accentColor}
                  onChange={(e) => updateCustomTheme('accentColor', e.target.value)}
                  style={{ 
                    background: getPalette().bg,
                    border: '1px solid #00ff41',
                    padding: '8px',
                    borderRadius: '4px',
                    color: getPalette().text,
                    fontFamily: 'monospace'
                  }}
                />
              </div>
            </div>
          </div>

          <div style={{ marginTop: '20px' }}>
            <div className="preview-box">
              <div style={{ textAlign: 'center', paddingTop: '20px' }}>
                <strong>Theme Preview</strong>
              </div>
              <div style={{ fontSize: '24px', marginBottom: '8px' }}>
                Aa
              </div>
              <div style={{ fontSize: '14px', opacity: 0.7 }}>
                Your text appears in this color
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '12px', justifyContent: 'center', marginTop: '20px' }}>
            <button
              onClick={() => {
                updateCustomTheme('customTheme', true);
                setIsDarkMode(true);
              }}
              style={{
                background: themeSettings.customTheme ? 'var(--primary-color)' : getPalette().bg,
                color: themeSettings.customTheme ? 'var(--background-color)' : getPalette().text,
                border: '2px solid var(--accent-color)',
                padding: '16px 32px',
                borderRadius: '8px',
                fontSize: '16px',
                fontWeight: 'bold',
                cursor: 'pointer',
                boxShadow: '0 4px 12px rgba(var(--primary-color), 0.3)'
              }}
            >
              Apply Custom Theme
            </button>
            
            <button
              onClick={resetToDefault}
              style={{
                background: getPalette().bg,
                border: '2px solid #00ff41',
                color: getPalette().text,
                padding: '16px 24px',
                borderRadius: '8px',
                fontSize: '14px',
                cursor: 'pointer'
              }}
            >
              Reset to Matrix
            </button>
          </div>
        </div>

        {/* Theme Info */}
        <div style={{
          background: getPalette().surface,
          padding: '20px',
          borderRadius: '12px',
          marginTop: '20px',
          border: '1px solid #00ff41'
        }}>
          <h2 style={{ marginBottom: '20px' }}>📊 Theme Information</h2>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr))', gap: '16px' }}>
            <div>
              <strong>Current Mode:</strong> {isDarkMode ? 'Dark' : 'Light'}
            </div>
            <div>
              <strong>Custom Theme:</strong> {themeSettings.customTheme ? 'Enabled' : 'Disabled'}
            </div>
            
            <div>
              <strong>Primary:</strong> 
              <span style={{ 
                background: themeSettings.primaryColor, 
                padding: '2px 8px', 
                borderRadius: '4px',
                fontFamily: 'monospace'
              }}>
                {themeSettings.primaryColor}
              </span>
            </div>
            <div>
              <strong>Background:</strong> 
              <span style={{ 
                background: themeSettings.backgroundColor, 
                padding: '2px 8px', 
                borderRadius: '4px',
                fontFamily: 'monospace'
              }}>
                {themeSettings.backgroundColor}
              </span>
            </div>
          </div>

          <div style={{ 
            gridColumn: 'span 2', 
            marginTop: '16px', 
            paddingTop: '16px',
            borderTop: '1px solid var(--accent-color)'
          }}>
            <h4 style={{ marginBottom: '12px' }}>💡 Pro Tips</h4>
            <ul style={{ fontSize: '14px', opacity: 0.8, lineHeight: '1.5' }}>
              <li>Custom themes automatically save to your browser</li>
              <li>Use hex codes for precise color control</li>
              <li>Dark mode reduces eye strain during long sessions</li>
              <li>Matrix theme optimized for coding and streaming</li>
              <li>Neon theme adds cyberpunk aesthetic to streams</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}