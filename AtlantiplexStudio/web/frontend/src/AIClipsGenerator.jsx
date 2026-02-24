import React, { useState, useEffect, useRef, useCallback } from 'react';
import { getPalette, getFontFamily } from './branding.ts';

export default function AIClipsGenerator() {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [clips, setClips] = useState([]);
  const [streamData, setStreamData] = useState(null);
  const [selectedClip, setSelectedClip] = useState(null);
  const [exportProgress, setExportProgress] = useState(0);
  const [aiSettings, setAISettings] = useState({
    sensitivity: 'medium',
    minLength: 15,
    maxLength: 60,
    platforms: ['tiktok', 'instagram', 'youtube-shorts']
  });

  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  // AI-powered stream analysis
  const analyzeStreamForHighlights = useCallback(async () => {
    if (!streamData) return;
    
    setIsAnalyzing(true);
    
    try {
      // Simulate AI analysis of engagement spikes
      const highlights = await detectEngagementSpikes();
      const chatHighlights = await extractChatHighlights();
      const visualMoments = await detectVisualMoments();
      
      // Generate clips based on AI analysis
      const generatedClips = await generateClipsFromHighlights(highlights, chatHighlights, visualMoments);
      
      setClips(generatedClips);
      setIsAnalyzing(false);
    } catch (error) {
      console.error('AI analysis failed:', error);
      setIsAnalyzing(false);
    }
  }, [streamData]);

  const detectEngagementSpikes = async () => {
    return new Promise(resolve => {
      setTimeout(() => {
        // Simulate engagement spike detection
        const spikes = [
          { timestamp: Date.now() - 300000, type: 'laughter', intensity: 0.8 },
          { timestamp: Date.now() - 240000, type: 'cheer', intensity: 0.7 },
          { timestamp: Date.now() - 180000, type: 'excitement', intensity: 0.9 },
          { timestamp: Date.now() - 120000, type: 'reaction', intensity: 0.6 },
          { timestamp: Date.now() - 60000, type: 'question', intensity: 0.5 },
        ];
        resolve(spikes);
      }, 2000);
    });
  };

  const extractChatHighlights = async () => {
    return new Promise(resolve => {
      setTimeout(() => {
        // Simulate chat highlights extraction
        const highlights = [
          { message: 'INSANE CLUTCH!', timestamp: Date.now() - 300000, author: 'User123' },
          { message: 'OMG this is amazing', timestamp: Date.now() - 240000, author: 'User456' },
          { message: 'POGGERS!', timestamp: Date.now() - 180000, author: 'User789' },
          { message: 'W RATIO', timestamp: Date.now() - 120000, author: 'User101' },
        ];
        resolve(highlights);
      }, 1500);
    });
  };

  const detectVisualMoments = async () => {
    return new Promise(resolve => {
      setTimeout(() => {
        // Simulate visual moment detection
        const moments = [
          { type: 'jump', timestamp: Date.now() - 300000, confidence: 0.9 },
          { type: 'dance', timestamp: Date.now() - 200000, confidence: 0.8 },
          { type: 'celebration', timestamp: Date.now() - 100000, confidence: 0.95 },
          { type: 'funny_moment', timestamp: Date.now() - 50000, confidence: 0.7 },
        ];
        resolve(moments);
      }, 1800);
    });
  };

  const generateClipsFromHighlights = async (engagementSpikes, chatHighlights, visualMoments) => {
    return new Promise(resolve => {
      setTimeout(() => {
        const generatedClips = [];
        
        // Combine all AI-detected highlights
        const allHighlights = [
          ...engagementSpikes,
          ...chatHighlights.map(chat => ({ ...chat, type: 'chat_highlight' })),
          ...visualMoments
        ].sort((a, b) => a.timestamp - b.timestamp);

        // Generate 15-60 second clips for vertical content
        allHighlights.forEach((highlight, index) => {
          const clip = {
            id: Date.now() + Math.random(),
            title: generateClipTitle(highlight),
            startTime: Math.max(0, highlight.timestamp - 30000),
            endTime: Math.min(highlight.timestamp + 30000, highlight.timestamp + aiSettings.maxLength * 1000),
            type: highlight.type,
            intensity: highlight.intensity || 0.5,
            score: calculateAIScore(highlight),
            thumbnail: generateThumbnail(highlight),
            status: 'ready'
          };
          generatedClips.push(clip);
        });

        // Limit to top 15 clips
        resolve(generatedClips.slice(0, 15));
      }, 2500);
    });
  };

  const generateClipTitle = (highlight) => {
    const titles = {
      laughter: 'Epic Laughter Moment',
      cheer: 'Crowd Goes Wild',
      excitement: 'Insane Reaction',
      reaction: 'Community Response',
      chat_highlight: `Chat Explosion: ${highlight.message.substring(0, 20)}...`,
      jump: 'E Jump Moment',
      dance: 'Dance Party',
      celebration: 'Victory Celebration',
      funny_moment: 'Hilarious Moment'
    };
    return titles[highlight.type] || 'Epic Stream Moment';
  };

  const calculateAIScore = (highlight) => {
    let score = (highlight.intensity || 0.5) * 100;
    score += highlight.confidence ? highlight.confidence * 20 : 0;
    score += highlight.type === 'celebration' ? 30 : 0;
    score += highlight.type === 'laughter' ? 25 : 0;
    return Math.min(100, Math.round(score));
  };

  const generateThumbnail = (highlight) => {
    // Simulate thumbnail generation
    return `data:image/svg+xml,${encodeURIComponent(`
      <svg width="480" height="854" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#00ff41;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#764ba2;stop-opacity:1" />
          </linearGradient>
        </defs>
        <rect width="480" height="854" fill="url(#grad)" />
        <text x="50%" y="50%" text-anchor="middle" dominant-baseline="middle" fill="white" font-size="48" font-weight="bold">
          ${highlight.type.toUpperCase()}
        </text>
      </svg>
    `)}`;
  };

  const exportToSocialPlatforms = async (clip) => {
    setExportProgress(0);
    
    for (const platform of aiSettings.platforms) {
      try {
        // Simulate export to each platform
        await new Promise(resolve => {
          setExportProgress(prev => {
            const progress = prev + (100 / aiSettings.platforms.length);
            return Math.min(100, progress);
          });
          setTimeout(resolve, 2000);
        });
        
        console.log(`Exported clip to ${platform}:`, clip.title);
      } catch (error) {
        console.error(`Failed to export to ${platform}:`, error);
      }
    }
    
    setExportProgress(100);
    setTimeout(() => setExportProgress(0), 2000);
  };

  const formatDuration = (startTime, endTime) => {
    const duration = (endTime - startTime) / 1000;
    const minutes = Math.floor(duration / 60);
    const seconds = Math.floor(duration % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
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
          🤖 AI Clips Generator
          <span style={{ fontSize: '16px', opacity: 0.7, marginLeft: '20px' }}>
            Auto-create vertical clips for social media
          </span>
        </h1>

        {/* Control Panel */}
        <div style={{
          background: getPalette().surface,
          padding: '24px',
          borderRadius: '12px',
          marginBottom: '30px',
          border: '1px solid #00ff41'
        }}>
          <h2 style={{ marginBottom: '20px' }}>🧠 AI Analysis Settings</h2>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px' }}>
            <div>
              <label>Sensitivity Level</label>
              <select 
                value={aiSettings.sensitivity}
                onChange={(e) => setAISettings({...aiSettings, sensitivity: e.target.value})}
                style={{ 
                  width: '100%', 
                  padding: '8px', 
                  marginTop: '8px',
                  background: getPalette().bg,
                  border: '1px solid #00ff41',
                  color: getPalette().text
                }}
              >
                <option value="low">Low - Fewer clips</option>
                <option value="medium">Medium - Balanced</option>
                <option value="high">High - More clips</option>
              </select>
            </div>
            
            <div>
              <label>Clip Duration</label>
              <select 
                value={aiSettings.maxLength}
                onChange={(e) => setAISettings({...aiSettings, maxLength: parseInt(e.target.value)})}
                style={{ 
                  width: '100%', 
                  padding: '8px', 
                  marginTop: '8px',
                  background: getPalette().bg,
                  border: '1px solid #00ff41',
                  color: getPalette().text
                }}
              >
                <option value={15}>15 seconds</option>
                <option value={30}>30 seconds</option>
                <option value={45}>45 seconds</option>
                <option value={60}>60 seconds</option>
              </select>
            </div>
            
            <div>
              <label>Min Clip Length</label>
              <select 
                value={aiSettings.minLength}
                onChange={(e) => setAISettings({...aiSettings, minLength: parseInt(e.target.value)})}
                style={{ 
                  width: '100%', 
                  padding: '8px', 
                  marginTop: '8px',
                  background: getPalette().bg,
                  border: '1px solid #00ff41',
                  color: getPalette().text
                }}
              >
                <option value={10}>10 seconds</option>
                <option value={15}>15 seconds</option>
                <option value={20}>20 seconds</option>
                <option value={30}>30 seconds</option>
              </select>
            </div>
          </div>

          <div style={{ marginTop: '20px' }}>
            <h3 style={{ marginBottom: '15px' }}>Export Platforms</h3>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px' }}>
              {aiSettings.platforms.map(platform => (
                <label key={platform} style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
                  <input
                    type="checkbox"
                    checked={aiSettings.platforms.includes(platform)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setAISettings({...aiSettings, platforms: [...aiSettings.platforms, platform]});
                      } else {
                        setAISettings({...aiSettings, platforms: aiSettings.platforms.filter(p => p !== platform)});
                      }
                    }}
                    style={{ marginRight: '8px' }}
                  />
                  <span style={{ 
                    textTransform: 'capitalize',
                    fontSize: '14px',
                    padding: '4px 12px',
                    borderRadius: '8px',
                    background: '#00ff41',
                    color: getPalette().bg
                  }}>
                    {platform === 'tiktok' ? '🎵 TikTok' : 
                     platform === 'instagram' ? '📷 Instagram Reels' : 
                     platform === 'youtube-shorts' ? '📺 YouTube Shorts' : platform}
                  </span>
                </label>
              ))}
            </div>
          </div>

          <div style={{ marginTop: '20px', textAlign: 'center' }}>
            <button
              onClick={analyzeStreamForHighlights}
              disabled={isAnalyzing}
              style={{
                background: isAnalyzing ? '#6b7280' : '#00ff41',
                color: 'white',
                border: 'none',
                padding: '16px 32px',
                borderRadius: '8px',
                fontSize: '18px',
                fontWeight: 'bold',
                cursor: isAnalyzing ? 'not-allowed' : 'pointer',
                transition: 'all 0.3s ease',
                boxShadow: isAnalyzing ? 'none' : '0 4px 12px rgba(0, 255, 65, 0.3)'
              }}
            >
              {isAnalyzing ? '🤖 Analyzing Stream...' : '🚀 Start AI Analysis'}
            </button>
          </div>
        </div>

        {/* Generated Clips */}
        {clips.length > 0 && (
          <div style={{
            background: getPalette().surface,
            padding: '24px',
            borderRadius: '12px',
            marginBottom: '30px',
            border: '1px solid #00ff41'
          }}>
            <h2 style={{ marginBottom: '20px' }}>📱 Generated Clips ({clips.length})</h2>
            
            <div style={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', 
              gap: '20px',
              maxHeight: '400px',
              overflowY: 'auto'
            }}>
              {clips.map(clip => (
                <div
                  key={clip.id}
                  onClick={() => setSelectedClip(clip)}
                  style={{
                    background: getPalette().bg,
                    border: '2px solid #00ff41',
                    borderRadius: '8px',
                    padding: '16px',
                    cursor: 'pointer',
                    transition: 'all 0.3s ease',
                    position: 'relative'
                  }}
                >
                  <div style={{ marginBottom: '12px' }}>
                    <div style={{ 
                      width: '240px', 
                      height: '135px', 
                      backgroundImage: clip.thumbnail,
                      backgroundSize: 'cover',
                      backgroundPosition: 'center',
                      borderRadius: '4px',
                      border: '1px solid #00ff41'
                    }} />
                  </div>
                  
                  <div>
                    <h4 style={{ marginBottom: '8px', color: '#00ff41' }}>{clip.title}</h4>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                      <span style={{ fontSize: '14px', opacity: 0.8 }}>
                        {formatDuration(clip.startTime, clip.endTime)}
                      </span>
                      <span style={{ 
                        background: '#00ff41', 
                        color: getPalette().bg,
                        padding: '4px 8px',
                        borderRadius: '12px',
                        fontSize: '12px',
                        fontWeight: 'bold'
                      }}>
                        Score: {clip.score}
                      </span>
                    </div>
                    </div>
                    
                    <div style={{ 
                      display: 'flex', 
                      gap: '8px', 
                      marginTop: '12px',
                      fontSize: '12px',
                      opacity: 0.7
                    }}>
                      <span>🔥 {clip.intensity >= 0.8 ? 'High Energy' : clip.intensity >= 0.5 ? 'Medium' : 'Low'}</span>
                      <span>📊 {clip.score >= 80 ? 'Top 10%' : clip.score >= 60 ? 'Top 25%' : 'Trending'}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <div style={{ textAlign: 'center', marginTop: '20px' }}>
              <button
                onClick={() => clips.forEach(exportToSocialPlatforms)}
                style={{
                  background: '#00ff41',
                  color: getPalette().bg,
                  border: 'none',
                  padding: '16px 32px',
                  borderRadius: '8px',
                  fontSize: '18px',
                  fontWeight: 'bold',
                  cursor: 'pointer',
                  transition: 'all 0.3s ease',
                  boxShadow: '0 4px 12px rgba(0, 255, 65, 0.3)'
                }}
              >
                📤 Export All Clips to Social Media
              </button>
            </div>
          </div>
        )}

        {/* Export Progress */}
        {exportProgress > 0 && exportProgress < 100 && (
          <div style={{
            position: 'fixed',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            background: 'rgba(0, 0, 0, 0.9)',
            color: 'white',
            padding: '40px',
            borderRadius: '12px',
            textAlign: 'center',
            zIndex: 1000
          }}>
            <h3 style={{ marginBottom: '20px' }}>📤 Exporting to Social Media</h3>
            <div style={{ 
              width: '300px', 
              height: '20px', 
              background: '#333', 
              borderRadius: '10px',
              marginBottom: '20px'
            }}>
              <div style={{ 
                width: `${exportProgress}%`, 
                height: '100%', 
                background: '#00ff41', 
                borderRadius: '10px',
                transition: 'width 0.3s ease'
              }} />
            </div>
            <p>{exportProgress}% Complete</p>
          </div>
        )}

        {/* Export Success */}
        {exportProgress === 100 && (
          <div style={{
            position: 'fixed',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            background: '#00ff41',
            color: getPalette().bg,
            padding: '40px',
            borderRadius: '12px',
            textAlign: 'center',
            zIndex: 1000,
            boxShadow: '0 4px 12px rgba(0, 255, 65, 0.3)'
          }}>
            <h2 style={{ marginBottom: '20px' }}>✅ Export Complete!</h2>
            <p>All clips exported to your selected social platforms</p>
            <button
              onClick={() => setExportProgress(0)}
              style={{
                background: getPalette().bg,
                color: '#00ff41',
                border: '2px solid #00ff41',
                padding: '12px 24px',
                borderRadius: '8px',
                fontSize: '16px',
                fontWeight: 'bold',
                cursor: 'pointer'
              }}
            >
              Close
            </button>
          </div>
        )}

        {/* Selected Clip Modal */}
        {selectedClip && (
          <div style={{
            position: 'fixed',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            background: getPalette().surface,
            border: '2px solid #00ff41',
            borderRadius: '12px',
            padding: '24px',
            zIndex: 1000,
            minWidth: '400px',
            maxWidth: '500px',
            boxShadow: '0 8px 32px rgba(0, 255, 65, 0.3)'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <h3>Clip Details</h3>
              <button
                onClick={() => setSelectedClip(null)}
                style={{
                  background: 'none',
                  border: 'none',
                  color: getPalette().text,
                  fontSize: '24px',
                  cursor: 'pointer'
                }}
              >
                ×
              </button>
            </div>
            
            <div style={{ width: '200px', height: '135px', backgroundImage: selectedClip.thumbnail, backgroundSize: 'cover', backgroundPosition: 'center', borderRadius: '4px', marginBottom: '16px' }} />
            
            <div>
              <h4 style={{ color: '#00ff41', marginBottom: '12px' }}>{selectedClip.title}</h4>
              <p><strong>Duration:</strong> {formatDuration(selectedClip.startTime, selectedClip.endTime)}</p>
              <p><strong>Type:</strong> {selectedClip.type}</p>
              <p><strong>AI Score:</strong> {selectedClip.score}/100</p>
              <p><strong>Intensity:</strong> {selectedClip.intensity}/1.0</p>
            </div>
            
            <div style={{ display: 'flex', gap: '12px' }}>
              <button
                onClick={() => exportToSocialPlatforms(selectedClip)}
                style={{
                  flex: 1,
                  background: '#00ff41',
                  color: getPalette().bg,
                  border: 'none',
                  padding: '12px',
                  borderRadius: '8px',
                  fontSize: '14px',
                  fontWeight: 'bold',
                  cursor: 'pointer'
                }}
              >
                📤 Export
              </button>
              <button
                onClick={() => console.log('Add to queue')}
                style={{
                  flex: 1,
                  background: getPalette().bg,
                  border: '2px solid #00ff41',
                  color: getPalette().text,
                  padding: '12px',
                  borderRadius: '8px',
                  fontSize: '14px',
                  fontWeight: 'bold',
                  cursor: 'pointer'
                }}
              >
                Add to Queue
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}