import React, { useState, useEffect, useRef } from 'react';
import { getPalette, getFontFamily } from './branding.ts';

export default function VerticalContentOptimizer() {
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [originalContent, setOriginalContent] = useState(null);
  const [optimizedClips, setOptimizedClips] = useState([]);
  const [targetPlatform, setTargetPlatform] = useState('tiktok');
  const [optimizationLevel, setOptimizationLevel] = useState('balanced');
  const [progress, setProgress] = useState(0);

  const platforms = {
    tiktok: { 
      name: 'TikTok', 
      aspectRatio: '9:16', 
      maxDuration: 60, 
      optimalLength: 15,
      description: 'Short-form, trend-focused content',
      icon: '🎵'
    },
    instagram: { 
      name: 'Instagram Reels', 
      aspectRatio: '9:16', 
      maxDuration: 60, 
      optimalLength: 15,
      description: 'Visually stunning, short-form video',
      icon: '📷'
    },
    youtubeShorts: { 
      name: 'YouTube Shorts', 
      aspectRatio: '9:16', 
      maxDuration: 60, 
      optimalLength: 15,
      description: 'YouTube\'s short video platform',
      icon: '📺'
    },
    linkedin: { 
      name: 'LinkedIn Video', 
      aspectRatio: '1:1', 
      maxDuration: 90, 
      optimalLength: 30,
      description: 'Professional vertical video content',
      icon: '💼'
    },
    snapchat: { 
      name: 'Snapchat Spotlight', 
      aspectRatio: '3:4', 
      maxDuration: 60, 
      optimalLength: 10,
      description: 'Ephemeral, engaging short-form video',
      icon: '👻'
    }
  };

  const optimizationLevels = {
    quality: { 
      name: 'Highest Quality', 
      description: 'Best visual quality, larger files',
      settings: { resolution: '1080p', bitrate: 'high', compression: 'low' }
    },
    balanced: { 
      name: 'Balanced', 
      description: 'Good quality with reasonable file size',
      settings: { resolution: '1080p', bitrate: 'medium', compression: 'medium' }
    },
    performance: { 
      name: 'Performance', 
      description: 'Smaller files, good quality',
      settings: { resolution: '720p', bitrate: 'low', compression: 'high' }
    },
    minimal: { 
      name: 'Minimal', 
      description: 'Smallest files for faster uploads',
      settings: { resolution: '720p', bitrate: 'low', compression: 'maximum' }
    }
  };

  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  useEffect(() => {
    // Check for video processing capabilities
    checkVideoProcessingSupport();
  }, []);

  const checkVideoProcessingSupport = () => {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    
    if (!ctx.createImageData) {
      console.warn('Advanced video processing not supported');
    }
  };

  const uploadOriginalContent = (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      const video = document.createElement('video');
      video.src = e.target.result;
      video.onloadedmetadata = () => {
        setOriginalContent({
          file: file,
          duration: video.duration,
          width: video.videoWidth,
          height: video.videoHeight,
          aspectRatio: video.videoWidth / video.videoHeight
        });
        video.remove();
      };
    };
    reader.readAsDataURL(file);
  };

  const optimizeForVertical = useCallback(async () => {
    if (!originalContent) return;
    
    setIsOptimizing(true);
    setProgress(0);
    setOptimizedClips([]);
    
    try {
      const clips = await generateOptimizedClips(originalContent);
      setOptimizedClips(clips);
      setIsOptimizing(false);
      setProgress(100);
      
      console.log(`Generated ${clips.length} optimized clips for ${targetPlatform}`);
    } catch (error) {
      console.error('Optimization failed:', error);
      setIsOptimizing(false);
    }
  }, [originalContent, targetPlatform, optimizationLevel]);

  const generateOptimizedClips = async (content) => {
    // Simulate AI-powered content optimization
    const platform = platforms[targetPlatform];
    const clips = [];
    
    // Generate optimal clips based on platform requirements
    const numClips = Math.floor(content.duration / platform.optimalLength);
    
    for (let i = 0; i < numClips; i++) {
      const startTime = (i * platform.optimalLength) + 5; // Add 5 second buffer
      const endTime = Math.min(startTime + platform.optimalLength, content.duration);
      
      const clip = await generateClip(content, startTime, endTime, platform);
      clips.push(clip);
    }
    
    return clips;
  };

  const generateClip = async (content, startTime, endTime, platform) => {
    const clip = {
      id: Date.now() + Math.random(),
      startTime: startTime,
      endTime: endTime,
      duration: endTime - startTime,
      platform: targetPlatform,
      thumbnail: await generateThumbnail(content, startTime, platform),
      title: generateClipTitle(content, startTime, platform),
      score: calculateEngagementScore(startTime, endTime, platform),
      optimizations: await applyOptimizations(content, startTime, endTime, platform)
    };
    
    // Update progress
    setProgress(prev => Math.min(100, prev + (100 / numClips)));
    
    return clip;
  };

  const generateThumbnail = async (content, startTime, platform) => {
    // Simulate thumbnail generation with platform-specific styling
    const canvas = document.createElement('canvas');
    canvas.width = 480;
    canvas.height = platform.aspectRatio === '9:16' ? 854 : 480;
    const ctx = canvas.getContext('2d');
    
    // Create thumbnail with platform-specific styling
    await createPlatformStyledThumbnail(ctx, platform, startTime);
    
    return canvas.toDataURL();
  };

  const createPlatformStyledThumbnail = async (ctx, platform, startTime) => {
    const gradient = ctx.createLinearGradient(0, 0, canvas.width, canvas.height);
    
    if (platform.name === 'tiktok') {
      // TikTok styling - neon colors, bold text
      gradient.addColorStop(0, '#FF0050');
      gradient.addColorStop(0.5, '#FF0050');
      gradient.addColorStop(1, '#FF0A50');
      
      ctx.fillStyle = gradient;
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      
      // Add platform logo
      ctx.fillStyle = '#FFFFFF';
      ctx.font = 'bold 24px Arial';
      ctx.textAlign = 'center';
      ctx.fillText('🎵', canvas.width / 2, canvas.height / 2 - 12);
      
      // Add TikTok branding
      ctx.strokeStyle = '#FF0050';
      ctx.lineWidth = 3;
      ctx.strokeRect(10, canvas.height - 50, canvas.width - 20, 40);
      
    } else if (platform.name === 'instagram') {
      // Instagram styling - softer colors, elegant feel
      gradient.addColorStop(0, '#F58529');
      gradient.addColorStop(1, '#F58529');
      gradient.addColorStop(0.5, '#E1306C');
      
      ctx.fillStyle = gradient;
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      
      ctx.fillStyle = '#FFFFFF';
      ctx.font = 'bold 24px Georgia';
      ctx.textAlign = 'center';
      ctx.fillText('📷', canvas.width / 2, canvas.height / 2 - 12);
      
      // Instagram border
      ctx.strokeStyle = '#E1306C';
      ctx.lineWidth = 3;
      ctx.strokeRect(10, canvas.height - 50, canvas.width - 20, 40);
    } else if (platform.name === 'youtube') {
      // YouTube styling - brand colors
      gradient.addColorStop(0, '#FF0000');
      gradient.addColorStop(1, '#FF0000');
      
      ctx.fillStyle = gradient;
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      
      ctx.fillStyle = '#FFFFFF';
      ctx.font = 'bold 24px Roboto';
      ctx.textAlign = 'center';
      ctx.fillText('▶️', canvas.width / 2, canvas.height / 2 - 12);
      
      // YouTube border
      ctx.strokeStyle = '#FF0000';
      ctx.lineWidth = 3;
      ctx.strokeRect(10, canvas.height - 50, canvas.width - 20, 40);
    } else if (platform.name === 'linkedin') {
      // LinkedIn styling - professional blues
      gradient.addColorStop(0, '#0077B5');
      gradient.addColorStop(1, '#0077B5');
      
      ctx.fillStyle = gradient;
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      
      ctx.fillStyle = '#FFFFFF';
      ctx.font = 'bold 20px Arial';
      ctx.textAlign = 'center';
      ctx.fillText('💼', canvas.width / 2, canvas.height / 2 - 12);
      
      // Professional border
      ctx.strokeStyle = '#0077B5';
      ctx.lineWidth = 4;
      ctx.strokeRect(5, canvas.height - 50, canvas.width - 10, 40);
    } else {
      // Default styling
      gradient.addColorStop(0, '#00ff41');
      gradient.addColorStop(1, '#00ff41');
      
      ctx.fillStyle = gradient;
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      
      ctx.fillStyle = '#FFFFFF';
      ctx.font = 'bold 24px Arial';
      ctx.textAlign = 'center';
      ctx.fillText('📱', canvas.width / 2, canvas.height / 2 - 12);
    }
  };

  const generateClipTitle = (content, startTime, platform) => {
    const timeMarker = `${Math.floor(startTime / 60)}:${(startTime % 60).toString().padStart(2, '0')}`;
    
    const titles = {
      tiktok: [
        'Trending Moment!',
        'Epic Challenge',
        'Viral Dance',
        'Comedy Gold',
        'Recipe Success',
        'Workout Inspo',
        'Gaming Highlight',
        'Pet Fail 😂'
      ],
      instagram: [
        'Aesthetic Vibe',
        'Fashion Moment',
        'Travel Goals',
        'Food Photography',
        'Wellness Journey',
        'Home Tour',
        'Art Creation',
        'Skincare Tips'
      ],
      youtube: [
        'Tech Review',
        'Gaming Moment',
        'Tutorial Highlight',
        'Knowledge Share',
        'Life Hack',
        'DIY Project',
        'Music Performance'
      ],
      linkedin: [
        'Professional Insight',
        'Career Achievement',
        'Industry Analysis',
        'Leadership Tips',
        'Network Growth',
        'Business Strategy',
        'Expert Advice',
        'Success Story'
      ]
    };
    
    const platformTitles = titles[platform.name] || titles['tiktok'];
    const randomTitle = platformTitles[Math.floor(Math.random() * platformTitles.length)];
    
    return randomTitle;
  };

  const calculateEngagementScore = (startTime, endTime, platform) => {
    // Simulate AI engagement prediction
    const clipDuration = endTime - startTime;
    const optimalLength = platform.optimalLength;
    
    let score = 50; // Base score
    
    // Bonus for optimal length
    if (clipDuration >= optimalLength - 5 && clipDuration <= optimalLength + 5) {
      score += 30;
    }
    
    // Time-based adjustments
    if (startTime < 10 || startTime > content.duration - 10) {
      score += 20; // Beginning of video
    } else if (startTime > content.duration - 30) {
      score += 15; // End of video
    }
    
    return Math.min(100, score);
  };

  const applyOptimizations = async (content, startTime, endTime, platform) => {
    const optimizations = [];
    
    // Color grading
    optimizations.push({
      type: 'color_grading',
      description: 'Enhanced color correction'
    });
    
    // Contrast enhancement
    optimizations.push({
      type: 'contrast_enhancement',
      description: 'Improved clarity'
    });
    
    // Stabilization simulation
    optimizations.push({
      aspectRatio: platform.aspectRatio,
      description: 'Vertical aspect ratio optimization'
    });
    
    // Audio optimization
    optimizations.push({
      type: 'audio_normalization',
      description: 'Volume level balancing'
    });
    
    // Frame rate adjustment
    optimizations.push({
      targetFrameRate: platform.maxDuration <= 30 ? 60 : 30,
      description: 'Optimized frame rate'
    });
    
    return optimizations;
  };

  const downloadClip = (clip) => {
    const link = document.createElement('a');
    link.download = `${targetPlatform}-${clip.id}.mp4`;
    link.href = clip.blob;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const downloadAllClips = () => {
    optimizedClips.forEach((clip, index) => {
      setTimeout(() => downloadClip(clip), index * 500); // Delay to avoid browser issues
    });
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
          📱 Vertical Content Optimizer
          <span style={{ fontSize: '16px', opacity: 0.7, marginLeft: '20px' }}>
            AI-powered vertical clips for social media
          </span>
        </h1>

        {/* Upload Section */}
        <div style={{
          background: getPalette().surface,
          padding: '24px',
          borderRadius: '12px',
          marginBottom: '30px',
          border: '1px solid #00ff41'
        }}>
          <h2 style={{ marginBottom: '20px' }}>📤 Upload Original Content</h2>
          
          <div style={{ marginBottom: '20px' }}>
            <input
              type="file"
              accept="video/*"
              onChange={uploadOriginalContent}
              style={{
                width: '100%',
                padding: '16px',
                background: getPalette().bg,
                border: '2px dashed #00ff41',
                borderRadius: '8px',
                color: getPalette().text
              }}
            />
          </div>

          {originalContent && (
            <div style={{ 
              padding: '16px',
              background: 'rgba(0, 255, 65, 0.1)',
              borderRadius: '8px',
              marginTop: '16px'
            }}>
              <div style={{ marginBottom: '12px' }}>
                <strong>Original Video:</strong> {originalContent.file.name}
              </div>
              <div>
                <strong>Duration:</strong> {originalContent.duration.toFixed(1)}s
              </div>
              <div>
                <strong>Resolution:</strong> {originalContent.width}x{originalContent.height}
              </div>
              <div>
                <strong>Aspect Ratio:</strong> {(originalContent.aspectRatio).toFixed(2)}
              </div>
              </div>
            </div>
          )}
        </div>
        </div>

        {/* Platform Selection */}
        <div style={{
          background: getPalette().surface,
          padding: '24px',
          borderRadius: '12px',
          marginBottom: '30px',
          border: '1px solid #00ff41'
        }}>
          <h2 style={{ marginBottom: '20px' }}>🎯 Target Platform</h2>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '16px' }}>
            {Object.entries(platforms).map(([key, platform]) => (
              <button
                key={key}
                onClick={() => setTargetPlatform(key)}
                style={{
                  background: targetPlatform === key ? '#00ff41' : getPalette().bg,
                  color: targetPlatform === key ? getPalette().bg : getPalette().text,
                  border: '2px solid #00ff41',
                  padding: '16px',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  gap: '8px',
                  transition: 'all 0.3s ease'
                }}
              >
                <div style={{ fontSize: '24px' }}>{platform.icon}</div>
                <span>{platform.name}</span>
              </button>
            ))}
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
            <div>
              <label>Optimization Level</label>
              <select
                value={optimizationLevel}
                onChange={(e) => setOptimizationLevel(e.target.value)}
                style={{ 
                  width: '100%', 
                  padding: '8px', 
                  marginTop: '8px',
                  background: getPalette().bg,
                  border: '1px solid #00ff41',
                  color: getPalette().text
                }}
              >
                {Object.entries(optimizationLevels).map(([key, level]) => (
                  <option key={key} value={key}>
                    {level.name} - {level.description}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label>Clip Length (seconds)</label>
              <input
                type="number"
                value={platforms[targetPlatform].optimalLength}
                min="5"
                max={60}
                onChange={(e) => setTargetPlatform(prev => ({ ...prev, optimalLength: parseInt(e.target.value) }))}
                style={{ 
                  width: '100%', 
                  padding: '8px', 
                  marginTop: '8px',
                  background: getPalette().bg,
                  border: '1px solid #00ff41',
                  color: getPalette().text
                }}
              />
            </div>
          </div>
        </div>

        {/* Optimization Controls */}
        <div style={{ textAlign: 'center', marginTop: '30px' }}>
          <button
            onClick={optimizeForVertical}
            disabled={!originalContent || isOptimizing}
            style={{
              background: (!originalContent || isOptimizing) ? '#6b7280' : '#00ff41',
              color: (!originalContent || isOptimizing) ? getPalette().text : 'white',
              border: 'none',
              padding: '16px 32px',
              borderRadius: '8px',
              fontSize: '18px',
              fontWeight: 'bold',
              cursor: (!originalContent || isOptimizing) ? 'not-allowed' : 'pointer',
              boxShadow: (!originalContent || isOptimizing) ? 'none' : '0 4px 12px rgba(0, 255, 65, 0.3)'
            }}
          >
            {isOptimizing ? (
              <>
                <span className="theme-loading">🤖</span>
                <span style={{ marginLeft: '8px' }}>
                  Optimizing for {platforms[targetPlatform]?.name}...
                </span>
              </>
            ) : (
              <>
                <span>🚀</span>
                <span style={{ marginLeft: '8px' }}>
                  Optimize for {platforms[targetPlatform]?.name}
                </span>
              </>
            )}
          </button>
        </div>

        {/* Progress Bar */}
        {isOptimizing && (
          <div style={{
            marginTop: '20px',
            padding: '16px',
            background: getPalette().surface,
            borderRadius: '8px',
            border: '1px solid #00ff41'
          }}>
            <h3 style={{ marginBottom: '12px', textAlign: 'center' }}>🔄 Optimization Progress</h3>
            <div style={{ 
              width: '100%', 
              height: '20px', 
              background: '#f0f9ff',
              borderRadius: '10px',
              overflow: 'hidden'
            }}>
              <div
                style={{
                  width: `${progress}%`,
                  height: '100%',
                  background: '#00ff41',
                  transition: 'width 0.3s ease',
                  borderRadius: '10px'
                }}
              />
            </div>
            </div>
            <div style={{ textAlign: 'center', marginTop: '8px', fontSize: '14px' }}>
              {progress}% Complete
            </div>
          </div>
        </div>

        {/* Generated Clips */}
        {optimizedClips.length > 0 && (
          <div style={{
            background: getPalette().surface,
            padding: '24px',
            borderRadius: '12px',
            marginBottom: '30px',
            border: '1px solid #00ff41'
          }}>
            <h2 style={{ marginBottom: '20px' }}>
              📱 Generated Clips ({optimizedClips.length})
            </h2>
            
            <div style={{ 
              maxHeight: '400px', 
              overflowY: 'auto',
              display: 'grid', 
              gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
              gap: '16px'
            }}>
              {optimizedClips.map((clip, index) => (
                <div
                  key={clip.id}
                  style={{
                    background: getPalette().bg,
                    border: '2px solid #00ff41',
                    borderRadius: '8px',
                    padding: '12px',
                    cursor: 'pointer',
                    transition: 'all 0.3s ease'
                  }}
                  onClick={() => console.log('Clip details:', clip)}
                >
                  <div style={{ width: '100%', height: '90px', marginBottom: '8px' }}>
                    <img 
                      src={clip.thumbnail} 
                      alt={clip.title}
                      style={{ 
                        width: '100%', 
                        height: '100%', 
                        objectFit: 'cover',
                        borderRadius: '4px'
                      }}
                    />
                  </div>
                  
                  <div style={{ fontSize: '14px', lineHeight: '1.2' }}>
                    <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>{clip.title}</div>
                    <div>Duration: {clip.duration.toFixed(1)}s</div>
                    <div>Score: {clip.score}/100</div>
                    <div>Platform: {platforms[clip.platform]?.icon}</div>
                    <div style={{ fontSize: '12px', opacity: 0.7 }}>
                      {clip.optimizations?.map(opt => opt.description).join(', ')}
                    </div>
                  </div>
                  
                  <div style={{ 
                    marginTop: '8px', 
                    display: 'flex', 
                    gap: '8px' 
                  }}>
                    <button
                      onClick={() => downloadClip(clip)}
                      style={{
                        background: '#00ff41',
                        color: getPalette().bg,
                        border: 'none',
                        padding: '6px 12px',
                        borderRadius: '4px',
                        fontSize: '12px',
                        cursor: 'pointer'
                      }}
                    >
                      📥
                    </button>
                    <button
                      onClick={() => console.log('Add to queue:', clip)}
                      style={{
                        background: getPalette().bg,
                        border: '1px solid #00ff41',
                        color: getPalette().text,
                        padding: '6px 12px',
                        borderRadius: '4px',
                        fontSize: '12px',
                        cursor: 'pointer'
                      }}
                    >
                      ➕
                    </button>
                    <button
                      onClick={() => console.log('Share to story:', clip)}
                      style={{
                        background: 'linear-gradient(45deg, #00ff41, #00a0f0)',
                        color: getPalette().bg,
                        border: 'none',
                        padding: '6px 12px',
                        borderRadius: '4px',
                        fontSize: '12px',
                        cursor: 'pointer'
                      }}
                    >
                      📤
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div style={{ textAlign: 'center', marginTop: '20px' }}>
            <button
              onClick={downloadAllClips}
              style={{
                background: '#00ff41',
                color: getPalette().bg,
                border: 'none',
                padding: '16px 32px',
                borderRadius: '8px',
                fontSize: '16px',
                fontWeight: 'bold',
                cursor: 'pointer',
                boxShadow: '0 4px 12px rgba(0, 255, 65, 0.3)'
              }}
            >
              📥 Download All Clips
            </button>
          </div>
        </div>

        {/* Platform Tips */}
        <div style={{
          background: getPalette().surface,
          padding: '24px',
          borderRadius: '12px',
          border: '1px solid #00ff41'
        }}>
          <h2 style={{ marginBottom: '20px' }}>💡 {platforms[targetPlatform]?.name} Tips</h2>
          
          <div style={{ fontSize: '14px', lineHeight: '1.5' }}>
            {targetPlatform.name === 'tiktok' && (
              <>
                <li>• Use trending hashtags and challenges</li>
                <li>• Keep clips under 15 seconds for maximum reach</li>
                <li>• Add text overlays with bold, readable fonts</li>
                <li>• Use popular music and sound effects</li>
                <li>• Record in vertical orientation</li>
              </>
            )}
            
            {targetPlatform.name === 'instagram' && (
              <>
                <li>• Focus on aesthetic visuals and storytelling</li>
                <li>• Use consistent color grading and filters</li>
                <li>• Include trending music and transitions</li>
                <li>• Professional thumbnail design matters</li>
              </>
            )}
            
            <div style={{ gridColumn: 'span 2', marginTop: '20px' }}>
              <div style={{ marginBottom: '16px' }}>
                <h4 style={{ color: '#00ff41', marginBottom: '8px' }}>🎯 Best Practices</h4>
              </div>
              <ul style={{ fontSize: '14px', opacity: 0.8, lineHeight: '1.5' }}>
                <li>• Start with a hook (first 3-5 seconds)</li>
                <li>• Use high-energy, engaging content</li>
                <li>• Optimize for silent viewing</li>
                <li>• End with a strong call-to-action</li>
                <li>• Use trending audio when available</li>
              </ul>
              
              <div style={{ marginBottom: '16px' }}>
                <h4 style={{ color: '#00ff41', marginBottom: '8px' }}>⚡ Technical Specifications</h4>
              </div>
              <ul style={{ fontSize: '14px', opacity: 0.8, lineHeight: '1.5' }}>
                <li>• Platform aspect ratio: {platform.aspectRatio}</li>
                <li>• Max duration: {platform.maxDuration}s</li>
                <li>• Optimal length: {platform.optimalLength}s</li>
                <li>• Target resolution: 1080x1920</li>
                <li>• Frame rate: 30fps for smooth motion</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}