import React, { useState, useEffect, useRef } from 'react';
import { getPalette, getFontFamily } from './branding.ts';

export default function EnhancedScreenSharing() {
  const [isSharing, setIsSharing] = useState(false);
  const [shareQuality, setShareQuality] = useState('1080p');
  const [shareMode, setShareMode] = useState('window');
  const [audioEnabled, setAudioEnabled] = useState(true);
  const [mouseEnabled, setMouseEnabled] = useState(false);
  const [performanceMode, setPerformanceMode] = useState('balanced');
  const [screenCount, setScreenCount] = useState(1);

  const canvasRef = useRef(null);
  const streamRef = useRef(null);

  const shareQualities = {
    '720p': { label: '720p HD', width: 1280, height: 720, maxBitrate: 2500000 },
    '1080p': { label: '1080p FHD', width: 1920, height: 1080, maxBitrate: 5000000 },
    '1440p': { label: '1440p 2K', width: 2560, height: 1440, maxBitrate: 10000000 },
    '4K': { label: '2160p UHD', width: 3840, height: 2160, maxBitrate: 25000000 }
  };

  const shareModes = {
    'window': { label: 'Window', captureMethod: 'getScreen' },
    'application': { label: 'Application', captureMethod: 'browser' },
    'tab': { label: 'Current Tab', captureMethod: 'getScreen' },
    'display': { label: 'Display', captureMethod: 'fullScreen' }
  };

  const performancePresets = {
    'quality': { label: 'Highest Quality', bitrate: 1.2, frameRate: 60 },
    'balanced': { label: 'Balanced', bitrate: 1.0, frameRate: 30 },
    'performance': { label: 'Performance', bitrate: 0.8, frameRate: 30 },
    'adaptive': { label: 'Adaptive', description: 'Dynamically adjusts based on bandwidth' }
  };

  useEffect(() => {
    // Check for Display Capture API support
    if (!navigator.getDisplayMedia) {
      console.warn('Display Capture API not supported');
      setShareMode('window');
    }
  }, []);

  const startScreenShare = async () => {
    try {
      const constraints = {
        video: {
          width: { ideal: shareQualities[shareQuality].width },
          height: { ideal: shareQualities[shareQuality].height },
          frameRate: { ideal: 30 },
          cursor: 'never'
        },
        audio: audioEnabled
      };

      let stream;
      
      if (shareMode === 'display') {
        // Use Display Capture API for better quality
        stream = await navigator.getDisplayMedia({
          video: constraints.video,
          audio: constraints.audio,
          preferCurrentTab: true,
          controller: true
        });
      } else if (shareMode === 'window') {
        // Fall back to getScreen for windows
        stream = await navigator.mediaDevices.getDisplayMedia({
          video: constraints.video,
          audio: constraints.audio
        });
      } else if (shareMode === 'application') {
        // Browser-based screen capture
        stream = await navigator.mediaDevices.getUserMedia(constraints);
      } else if (shareMode === 'tab') {
        // Tab-based capture
        stream = await navigator.mediaDevices.getUserMedia({
          video: {
            mediaSource: 'screen',
            width: { ideal: shareQualities[shareQuality].width },
            height: { ideal: shareQualities[shareQuality].height }
          },
          audio: constraints.audio
        });
      }

      streamRef.current = stream;
      
      if (canvasRef.current) {
        const video = document.createElement('video');
        video.srcObject = stream;
        video.autoplay = true;
        video.muted = true;
        
        video.onloadedmetadata = () => {
          canvasRef.current.width = video.videoWidth;
          canvasRef.current.height = video.videoHeight;
        };

        video.onplay = () => {
          renderVideoToCanvas(video, canvasRef.current);
        };

        video.play();
      }
      
      setIsSharing(true);
      console.log(`Started ${shareQuality} screen sharing in ${shareMode} mode`);
      
    } catch (error) {
      console.error('Failed to start screen sharing:', error);
      alert(`Screen sharing failed: ${error.message}`);
    }
  };

  const stopScreenShare = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    
    if (canvasRef.current) {
      const ctx = canvasRef.current.getContext('2d');
      ctx.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height);
    }
    
    setIsSharing(false);
    console.log('Screen sharing stopped');
  };

  const renderVideoToCanvas = (video, canvas) => {
    const ctx = canvas.getContext('2d');
    let requestId;

    const render = () => {
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      requestId = requestAnimationFrame(render);
    };

    render();
  };

  const takeScreenshot = () => {
    if (!canvasRef.current) return;
    
    const link = document.createElement('a');
    link.download = `screen-capture-${shareQuality}-${Date.now()}.png`;
    link.href = canvasRef.current.toDataURL();
    link.click();
    
    console.log('Screenshot captured');
  };

  const addMouseOverlay = () => {
    // This would be implemented with WebRTC data channel
    console.log('Mouse overlay would be added');
  };

  const adjustQuality = async (quality) => {
    if (!isSharing) return;
    
    const oldStream = streamRef.current;
    setShareQuality(quality);
    
    // Stop current stream and restart with new quality
    stopScreenShare();
    await new Promise(resolve => setTimeout(resolve, 1000));
    await startScreenShare();
  };

  const getPerformanceMetrics = () => {
    if (!streamRef.current) return null;
    
    const videoTrack = streamRef.current.getVideoTracks()[0];
    const audioTrack = streamRef.current.getAudioTracks()[0];
    
    return {
      resolution: `${shareQualities[shareQuality].width}x${shareQualities[shareQuality].height}`,
      frameRate: videoTrack?.getSettings().frameRate || 30,
      bandwidth: videoTrack?.getSettings().width * videoTrack?.getSettings().height * 30 || 0,
      audioEnabled: audioTrack?.enabled || false,
      screenCount: screenCount,
      quality: shareQualities[shareQuality].maxBitrate
    };
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: getPalette().bg,
      fontFamily: getFontFamily(),
      padding: '20px',
      color: getPalette().text
    }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <h1 style={{ textAlign: 'center', marginBottom: '30px' }}>
          🖥️ Enhanced Screen Sharing
          <span style={{ fontSize: '16px', opacity: 0.7, marginLeft: '20px' }}>
            Professional screen capture with quality optimization
          </span>
        </h1>

        {/* Preview Area */}
        <div style={{
          background: getPalette().surface,
          padding: '20px',
          borderRadius: '12px',
          marginBottom: '30px',
          border: '1px solid #00ff41'
        }}>
          <h2 style={{ marginBottom: '20px' }}>📺 Screen Preview</h2>
          
          <canvas
            ref={canvasRef}
            style={{
              width: '100%',
              maxWidth: '800px',
              height: 'auto',
              background: '#000',
              borderRadius: '8px',
              border: '2px solid #00ff41'
            }}
          />
          
          {isSharing && (
            <div style={{ 
              position: 'absolute', 
              top: '10px', 
              right: '10px', 
              background: 'rgba(0, 255, 65, 0.8)',
              color: 'white',
              padding: '8px 16px',
              borderRadius: '8px',
              fontSize: '12px',
              fontWeight: 'bold',
              zIndex: 10
            }}>
              🔴 LIVE
            </div>
          )}
          
          <div style={{ textAlign: 'center', marginTop: '16px' }}>
            <button
              onClick={takeScreenshot}
              disabled={!isSharing}
              style={{
                background: isSharing ? '#00ff41' : '#6b7280',
                color: 'white',
                border: 'none',
                padding: '12px 24px',
                borderRadius: '8px',
                fontSize: '16px',
                fontWeight: 'bold',
                cursor: isSharing ? 'pointer' : 'not-allowed'
              }}
            >
              📸 Take Screenshot
            </button>
          </div>
        </div>

        {/* Share Controls */}
        <div style={{
          background: getPalette().surface,
          padding: '24px',
          borderRadius: '12px',
          marginBottom: '30px',
          border: '1px solid #00ff41'
        }}>
          <h2 style={{ marginBottom: '20px' }}>🎮 Share Controls</h2>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px', marginBottom: '20px' }}>
            <div>
              <label>Sharing Mode</label>
              <select
                value={shareMode}
                onChange={(e) => setShareMode(e.target.value)}
                style={{ 
                  width: '100%', 
                  padding: '8px', 
                  marginTop: '8px',
                  background: getPalette().bg,
                  border: '1px solid #00ff41',
                  color: getPalette().text
                }}
                disabled={isSharing}
              >
                {Object.entries(shareModes).map(([key, mode]) => (
                  <option key={key} value={key}>
                    {mode.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label>Quality</label>
              <select
                value={shareQuality}
                onChange={(e) => setShareQuality(e.target.value)}
                style={{ 
                  width: '100%', 
                  padding: '8px', 
                  marginTop: '8px',
                  background: getPalette().bg,
                  border: '1px solid #00ff41',
                  color: getPalette().text
                }}
                disabled={isSharing}
              >
                {Object.entries(shareQualities).map(([key, quality]) => (
                  <option key={key} value={key}>
                    {quality.label} - {Math.round(quality.maxBitrate / 1000000)} Mbps
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label>Performance</label>
              <select
                value={performanceMode}
                onChange={(e) => setPerformanceMode(e.target.value)}
                style={{ 
                  width: '100%', 
                  padding: '8px', 
                  marginTop: '8px',
                  background: getPalette().bg,
                  border: '1px solid #00ff41',
                  color: getPalette().text
                }}
                disabled={isSharing}
              >
                {Object.entries(performancePresets).map(([key, preset]) => (
                  <option key={key} value={key}>
                    {preset.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr))', gap: '16px' }}>
            <div>
              <label>
                <input
                  type="checkbox"
                  checked={audioEnabled}
                  onChange={(e) => setAudioEnabled(e.target.checked)}
                  disabled={isSharing}
                  style={{ marginRight: '8px' }}
                />
                Audio Enabled
              </label>
            </div>

            <div>
              <label>
                <input
                  type="checkbox"
                  checked={mouseEnabled}
                  onChange={(e) => setMouseEnabled(e.target.checked)}
                  disabled={isSharing}
                  style={{ marginRight: '8px' }}
                />
                Mouse Overlay
              </label>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr))', gap: '16px' }}>
            <div>
              <label>Screen Count</label>
              <input
                type="range"
                min="1"
                max="4"
                value={screenCount}
                onChange={(e) => setScreenCount(parseInt(e.target.value))}
                disabled={isSharing}
                style={{ width: '100%', marginTop: '8px' }}
              />
            </div>
            <div style={{ textAlign: 'center', fontSize: '14px' }}>
              {screenCount} Screen{screenCount !== 1 ? 's' : ''}
            </div>
          </div>

          {/* Share/Stop Buttons */}
          <div style={{ display: 'flex', gap: '12px', justifyContent: 'center', marginTop: '20px' }}>
            {!isSharing ? (
              <button
                onClick={startScreenShare}
                style={{
                  background: '#00ff41',
                  color: 'white',
                  border: 'none',
                  padding: '16px 32px',
                  borderRadius: '8px',
                  fontSize: '16px',
                  fontWeight: 'bold',
                  cursor: 'pointer',
                  boxShadow: '0 4px 12px rgba(0, 255, 65, 0.3)'
                }}
              >
                🚀 Start Sharing
              </button>
            ) : (
              <button
                onClick={stopScreenShare}
                style={{
                  background: '#f44336',
                  color: 'white',
                  border: 'none',
                  padding: '16px 32px',
                  borderRadius: '8px',
                  fontSize: '16px',
                  fontWeight: 'bold',
                  cursor: 'pointer',
                  boxShadow: '0 4px 12px rgba(244, 67, 54, 0.3)'
                }}
              >
                ⏹️ Stop Sharing
              </button>
            )}
          </div>
        </div>

        {/* Performance Metrics */}
        {isSharing && (
          <div style={{
            background: getPalette().surface,
            padding: '20px',
            borderRadius: '12px',
            border: '1px solid #00ff41'
          }}>
            <h2 style={{ marginBottom: '20px' }}>📊 Performance Metrics</h2>
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr))', gap: '16px', fontSize: '14px' }}>
              <div>
                <strong>Resolution:</strong> {getPerformanceMetrics()?.resolution || 'N/A'}
              </div>
              <div>
                <strong>Frame Rate:</strong> {getPerformanceMetrics()?.frameRate || 'N/A'} fps
              </div>
              <div>
                <strong>Bandwidth:</strong> {getPerformanceMetrics()?.bandwidth ? `${Math.round(getPerformanceMetrics().bandwidth / 1000000)} Mbps` : 'N/A'}
              </div>
              <div>
                <strong>Quality:</strong> {shareQualities[shareQuality].label}
              </div>
            </div>

            <div style={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(2, 1fr)', 
              gap: '16px', 
              fontSize: '14px',
              marginTop: '16px',
              paddingTop: '16px',
              borderTop: '1px solid var(--accent-color)'
            }}>
              <div>
                <strong>Audio:</strong> {getPerformanceMetrics()?.audioEnabled ? 'Enabled' : 'Disabled'}
              </div>
              <div>
                <strong>Mouse:</strong> {mouseEnabled ? 'Enabled' : 'Disabled'}
              </div>
              <div>
                <strong>Screens:</strong> {screenCount}
              </div>
              <div>
                <strong>Mode:</strong> {shareModes[shareMode]?.label || 'N/A'}
              </div>
            </div>
          </div>

          <div style={{ 
            marginTop: '20px',
            padding: '16px',
            background: 'rgba(0, 255, 65, 0.1)',
            borderRadius: '8px',
            fontSize: '14px'
          }}>
            <h4 style={{ marginBottom: '12px', color: '#00ff41' }}>💡 Tips</h4>
            <ul style={{ margin: 0, paddingLeft: '20px', lineHeight: '1.5' }}>
              <li>Use Display mode for highest quality and system-level access</li>
              <li>1080p provides good balance between quality and performance</li>
              <li>4K requires strong hardware and fast internet</li>
              <li>Performance mode helps reduce bandwidth usage</li>
              <li>Audio sharing adds professional touch to presentations</li>
              <li>Multi-screen support for complex presentations</li>
            </ul>
          </div>
        </div>
        )}

        {/* Status Information */}
        <div style={{
          background: getPalette().surface,
          padding: '20px',
          borderRadius: '12px',
          border: '1px solid #00ff41',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '24px', marginBottom: '16px' }}>
            {isSharing ? '📹' : '⚪'}
          </div>
          <div>
            <strong style={{ fontSize: '18px', marginBottom: '8px' }}>
              {isSharing ? 'Screen Sharing Active' : 'Ready to Share'}
            </strong>
          </div>
          {isSharing && (
            <div style={{ fontSize: '14px', opacity: 0.8, marginTop: '8px' }}>
              Sharing your {shareQualities[shareQuality]?.label} screen
              {shareCount > 1 ? ` and ${screenCount - 1} other screen${screenCount - 1 ? 's' : ''}` : ''}
            </div>
          )}
        </div>
        </div>
      </div>
    </div>
  );
}