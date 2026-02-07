import React, { useState, useEffect, useRef, useCallback } from 'react';
import { getPalette, getFontFamily } from './branding.ts';

export default function CameraEffectsEngine() {
  const [selectedShape, setSelectedShape] = useState('circle');
  const [shapeSize, setShapeSize] = useState(80);
  const [shapeColor, setShapeColor] = useState('#00ff41');
  const [shapeBorder, setShapeBorder] = useState(true);
  const [animationStyle, setAnimationStyle] = useState('pulse');
  const [effects, setEffects] = useState([]);
  const [webcamStream, setWebcamStream] = useState(null);
  const [gpuAcceleration, setGpuAcceleration] = useState(true);

  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const animationFrameRef = useRef(null);

  const shapes = [
    { id: 'circle', icon: '○', label: 'Circle' },
    { id: 'square', icon: '□', label: 'Square' },
    { id: 'rounded-square', icon: '◇', label: 'Rounded Square' },
    { id: 'hexagon', icon: '⬡', label: 'Hexagon' },
    { id: 'triangle', icon: '△', label: 'Triangle' },
    { id: 'star', icon: '★', label: 'Star' },
    { id: 'heart', icon: '♥', label: 'Heart' }
  ];

  const animations = [
    { id: 'pulse', label: 'Pulse', effect: 'opacity 0.3 → 1' },
    { id: 'rotate', label: 'Rotate', effect: 'rotate 360deg' },
    { id: 'bounce', label: 'Bounce', effect: 'translateY(0) → translateY(-20px)' },
    { id: 'glow', label: 'Glow', effect: 'box-shadow 0 0 20px rgba(0, 255, 65, 0.8)' },
    { id: 'shimmer', label: 'Shimmer', effect: 'linear-gradient(45deg, transparent 30%, rgba(0, 255, 65, 0.8) 50%, transparent 70%)' }
  ];

  const effectPresets = [
    { name: 'Subtle', id: 'subtle', effects: ['glow'], animation: 'pulse' },
    { name: 'Party', id: 'party', effects: ['glow', 'shimmer'], animation: 'bounce' },
    { name: 'Professional', id: 'professional', effects: [''], animation: 'none' },
    { name: 'Extreme', id: 'extreme', effects: ['glow', 'shimmer'], animation: 'rotate' }
  ];

  useEffect(() => {
    // Initialize webcam stream
    initializeWebcam();
    
    // Start rendering loop
    const render = () => {
      renderCameraEffects();
      animationFrameRef.current = requestAnimationFrame(render);
    };
    render();
    
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [selectedShape, shapeSize, shapeColor, shapeBorder, animationStyle, effects]);

  const initializeWebcam = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 1920 },
          height: { ideal: 1080 },
          facingMode: 'user'
        },
        audio: true
      });
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
        setWebcamStream(stream);
      }
    } catch (error) {
      console.error('Failed to access webcam:', error);
    }
  };

  const renderCameraEffects = useCallback(() => {
    if (!videoRef.current || !canvasRef.current) return;
    
    const video = videoRef.current;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    
    if (!ctx || video.paused || video.ended) return;
    
    // Set canvas size to match video
    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;
    
    // Draw the video frame
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    // Apply camera shape overlay
    drawShapeOverlay(ctx, canvas.width, canvas.height);
    
    // Apply effects
    applyVideoEffects(ctx, canvas.width, canvas.height);
  }, [selectedShape, shapeSize, shapeColor, shapeBorder, animationStyle, effects]);

  const drawShapeOverlay = (ctx, width, height) => {
    if (!selectedShape) return;
    
    const centerX = width / 2;
    const centerY = height / 2;
    const currentTime = Date.now() / 1000;
    
    // Save current context state
    ctx.save();
    
    // Apply animation transformations
    ctx.translate(centerX, centerY);
    
    if (animationStyle === 'rotate') {
      ctx.rotate((currentTime * 360 / 5) % 360);
    } else if (animationStyle === 'bounce') {
      const bounceOffset = Math.sin(currentTime * 2) * 20;
      ctx.translate(0, bounceOffset);
    }
    
    // Draw the selected shape
    ctx.beginPath();
    
    switch (selectedShape) {
      case 'circle':
        ctx.arc(0, 0, shapeSize / 2, 0, Math.PI * 2);
        break;
        
      case 'square':
        ctx.rect(-shapeSize / 2, -shapeSize / 2, shapeSize, shapeSize);
        break;
        
      case 'rounded-square':
        drawRoundedRect(ctx, -shapeSize / 2, -shapeSize / 2, shapeSize, shapeSize, 10);
        break;
        
      case 'hexagon':
        drawHexagon(ctx, 0, 0, shapeSize / 2);
        break;
        
      case 'triangle':
        ctx.moveTo(0, -shapeSize / 2);
        ctx.lineTo(-shapeSize / 2, shapeSize / 2);
        ctx.lineTo(shapeSize / 2, -shapeSize / 2);
        ctx.closePath();
        break;
        
      case 'star':
        drawStar(ctx, 0, 0, 5, shapeSize / 2, shapeSize / 4);
        break;
        
      case 'heart':
        drawHeart(ctx, 0, 0, shapeSize);
        break;
    }
    
    ctx.closePath();
    
    // Apply styles
    if (shapeColor !== 'transparent') {
      ctx.fillStyle = shapeColor + '33'; // Add transparency
      ctx.fill();
    }
    
    if (shapeBorder) {
      ctx.strokeStyle = shapeColor;
      ctx.lineWidth = 3;
      ctx.stroke();
    }
    
    // Apply animation-specific color changes
    if (animationStyle === 'pulse') {
      const pulseOpacity = 0.3 + (Math.sin(currentTime * 3) + 1) * 0.7;
      ctx.fillStyle = shapeColor + Math.floor(pulseOpacity * 255).toString(16).padStart(2, '0');
      ctx.fill();
    }
    
    // Restore context
    ctx.restore();
  };

  const drawRoundedRect = (ctx, x, y, width, height, radius) => {
    ctx.moveTo(x + radius, y);
    ctx.lineTo(x + width - radius, y);
    ctx.lineTo(x + width - radius, y + height - radius);
    ctx.quadraticCurveTo(x + width, y + height, x + width, y + height - radius, x + width - radius, y + height);
    ctx.lineTo(x + radius, y + height - radius);
    ctx.quadraticCurveTo(x, y + height - radius, x, y + height - radius, x, y + height);
  };

  const drawHexagon = (ctx, x, y, radius) => {
    ctx.beginPath();
    for (let i = 0; i < 6; i++) {
      const angle = (Math.PI / 3) * i;
      const xPos = x + radius * Math.cos(angle);
      const yPos = y + radius * Math.sin(angle);
      if (i === 0) {
        ctx.moveTo(xPos, yPos);
      } else {
        ctx.lineTo(xPos, yPos);
      }
    }
    ctx.closePath();
  };

  const drawStar = (ctx, x, y, spikes, outerRadius, innerRadius) => {
    let rot = Math.PI / 2 * 3;
    let step = Math.PI / spikes;
    ctx.beginPath();
    ctx.moveTo(x, y - outerRadius);
    
    for (let i = 0; i < spikes; i++) {
      const outerX = x + Math.cos(rot) * outerRadius;
      const outerY = y + Math.sin(rot) * outerRadius;
      rot += step;
      
      const innerX = x + Math.cos(rot) * innerRadius;
      const innerY = y + Math.sin(rot) * innerRadius;
      rot += step;
      
      ctx.lineTo(outerX, outerY);
      ctx.lineTo(innerX, innerY);
    }
    
    ctx.lineTo(x, y - outerRadius);
    ctx.closePath();
  };

  const drawHeart = (ctx, x, y, size) => {
    ctx.beginPath();
    const topCurveHeight = size * 0.3;
    ctx.moveTo(x, y + topCurveHeight);
    
    // Left curve
    ctx.bezierCurveTo(x, y, x - size / 2, y, x - size / 2, y + size / 4);
    
    // Bottom point
    ctx.bezierCurveTo(x - size / 2, y + size, x, y + size);
    
    // Right curve
    ctx.bezierCurveTo(x, y + size, x + size / 2, y, x + size / 2, y + size / 4);
    
    ctx.closePath();
  };

  const applyVideoEffects = (ctx, width, height) => {
    effects.forEach(effect => {
      switch (effect) {
        case 'blur':
          applyBlurEffect(ctx, width, height);
          break;
        case 'grayscale':
          applyGrayscaleEffect(ctx, width, height);
          break;
        case 'sepia':
          applySepiaEffect(ctx, width, height);
          break;
        case 'brightness':
          applyBrightnessEffect(ctx, width, height, 1.2);
          break;
        case 'contrast':
          applyContrastEffect(ctx, width, height, 1.5);
          break;
        case 'pixelate':
          applyPixelateEffect(ctx, width, height);
          break;
        case 'rainbow':
          applyRainbowEffect(ctx, width, height);
          break;
      }
    });
  };

  const applyBlurEffect = (ctx, width, height) => {
    const imageData = ctx.getImageData(0, 0, width, height);
    const data = imageData.data;
    const outputData = new Uint8ClampedArray(data.length);
    
    // Simple box blur
    for (let y = 0; y < height; y++) {
      for (let x = 0; x < width; x++) {
        const idx = (y * width + x) * 4;
        let r = 0, g = 0, b = 0, a = 0;
        
        for (let dy = -1; dy <= 1; dy++) {
          for (let dx = -1; dx <= 1; dx++) {
            const pixelIdx = ((y + dy) * width + (x + dx)) * 4;
            if (pixelIdx >= 0 && pixelIdx < data.length) {
              r += data[pixelIdx];
              g += data[pixelIdx + 1];
              b += data[pixelIdx + 2];
              a += data[pixelIdx + 3];
            }
          }
        }
        
        outputData[idx] = Math.round(r / 9);
        outputData[idx + 1] = Math.round(g / 9);
        outputData[idx + 2] = Math.round(b / 9);
        outputData[idx + 3] = Math.round(b / 9);
      }
    }
    
    const outputImageData = new ImageData(outputData, width, height);
    ctx.putImageData(outputImageData, 0, 0);
  };

  const applyGrayscaleEffect = (ctx, width, height) => {
    const imageData = ctx.getImageData(0, 0, width, height);
    const data = imageData.data;
    
    for (let i = 0; i < data.length; i += 4) {
      const gray = data[i] * 0.299 + data[i + 1] * 0.587 + data[i + 2] * 0.114;
      data[i] = gray;
      data[i + 1] = gray;
      data[i + 2] = gray;
      data[i + 3] = 255; // Alpha
    }
    
    ctx.putImageData(imageData, 0, 0);
  };

  const applySepiaEffect = (ctx, width, height) => {
    const imageData = ctx.getImageData(0, 0, width, height);
    const data = imageData.data;
    
    for (let i = 0; i < data.length; i += 4) {
      const r = data[i];
      const g = data[i + 1];
      const b = data[i + 2];
      
      data[i] = Math.min(255, (r * 0.393 + g * 0.769 + b * 0.189));
      data[i + 1] = Math.min(255, (r * 0.349 + g * 0.686 + b * 0.168));
      data[i + 2] = Math.min(255, (r * 0.272 + g * 0.534 + b * 0.131));
      data[i + 3] = 255; // Alpha
    }
    
    ctx.putImageData(imageData, 0, 0);
  };

  const applyBrightnessEffect = (ctx, width, height, factor) => {
    const imageData = ctx.getImageData(0, 0, width, height);
    const data = imageData.data;
    
    for (let i = 0; i < data.length; i += 4) {
      data[i] = Math.min(255, data[i] * factor);
      data[i + 1] = Math.min(255, data[i + 1] * factor);
      data[i + 2] = Math.min(255, data[i + 2] * factor);
      // Alpha channel unchanged
    }
    
    ctx.putImageData(imageData, 0, 0);
  };

  const applyContrastEffect = (ctx, width, height, factor) => {
    const imageData = ctx.getImageData(0, 0, width, height);
    const data = imageData.data;
    
    for (let i = 0; i < data.length; i += 4) {
      data[i] = Math.min(255, ((data[i] - 128) * factor) + 128);
      data[i + 1] = Math.min(255, ((data[i + 1] - 128) * factor) + 128);
      data[i + 2] = Math.min(255, ((data[i + 2] - 128) * factor) + 128);
      // Alpha channel unchanged
    }
    
    ctx.putImageData(imageData, 0, 0);
  };

  const applyPixelateEffect = (ctx, width, height) => {
    const pixelSize = 8;
    const imageData = ctx.getImageData(0, 0, width, height);
    const data = imageData.data;
    
    for (let y = 0; y < height; y += pixelSize) {
      for (let x = 0; x < width; x += pixelSize) {
        const idx = (y * width + x) * 4;
        const r = data[idx];
        const g = data[idx + 1];
        const b = data[idx + 2];
        
        // Fill the pixel block with average color
        for (let py = 0; py < pixelSize; py++) {
          for (let px = 0; px < pixelSize; px++) {
            const pixelIdx = ((y + py) * width + (x + px)) * 4;
            data[pixelIdx] = r;
            data[pixelIdx + 1] = g;
            data[pixelIdx + 2] = b;
            data[pixelIdx + 3] = 255;
          }
        }
      }
    }
    
    ctx.putImageData(imageData, 0, 0);
  };

  const applyRainbowEffect = (ctx, width, height) => {
    const imageData = ctx.getImageData(0, 0, width, height);
    const data = imageData.data;
    const currentTime = Date.now() / 1000;
    
    for (let i = 0; i < data.length; i += 4) {
      const hue = ((currentTime * 50 + i) % 360);
      const [r, g, b] = hslToRgb(hue, 100, 100);
      
      data[i] = r;
      data[i + 1] = g;
      data[i + 2] = b;
      // Alpha channel unchanged
    }
    
    ctx.putImageData(imageData, 0, 0);
  };

  const hslToRgb = (h, s, l) => {
    s /= 100;
    l /= 100;
    
    const c = (1 - Math.abs(2 * l - 1)) * s;
    const m = l + c - Math.abs(l - c);
    const x = m * (1 - Math.abs(((h / 60) % 2) - 1)) + s - 1;
    
    if (h === 0) {
      return [l * 255, l * 255, l * 255];
    }
    
    const huePrime = h / 60 + 0.5;
    
    if (huePrime >= 1 && huePrime < 2) {
      return [x, m, c];
    } else if (huePrime >= 2 && huePrime < 3) {
      return [c, x, m];
    } else if (huePrime >= 3 && huePrime < 4) {
      return [m, c, x];
    } else {
      return [c, c, x];
    }
  };

  const takeSnapshot = useCallback(() => {
    if (!canvasRef.current) return;
    
    const link = document.createElement('a');
    link.download = `camera-snapshot-${Date.now()}.png`;
    link.href = canvasRef.current.toDataURL();
    link.click();
  }, []);

  const toggleEffect = (effect) => {
    setEffects(prev => {
      if (prev.includes(effect)) {
        return prev.filter(e => e !== effect);
      } else {
        return [...prev, effect];
      }
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
          🎥 Camera Effects Engine
          <span style={{ fontSize: '16px', opacity: 0.7, marginLeft: '20px' }}>
            Add shapes and effects to your camera feed
          </span>
        </h1>

        {/* Webcam Preview */}
        <div style={{
          background: getPalette().surface,
          padding: '20px',
          borderRadius: '12px',
          marginBottom: '30px',
          border: '1px solid #00ff41',
          textAlign: 'center'
        }}>
          <h2 style={{ marginBottom: '20px' }}>📹 Camera Preview</h2>
          
          <video
            ref={videoRef}
            autoPlay
            muted
            style={{
              width: '100%',
              maxWidth: '640px',
              height: 'auto',
              borderRadius: '8px',
              background: '#000'
            }}
          />
          
          <canvas
            ref={canvasRef}
            style={{
              width: '100%',
              maxWidth: '640px',
              height: 'auto',
              borderRadius: '8px',
              border: '2px solid #00ff41'
            }}
          />
          
          <div style={{ marginTop: '20px', textAlign: 'center' }}>
            <button
              onClick={takeSnapshot}
              style={{
                background: '#00ff41',
                color: getPalette().bg,
                border: 'none',
                padding: '12px 24px',
                borderRadius: '8px',
                fontSize: '16px',
                fontWeight: 'bold',
                cursor: 'pointer'
              }}
            >
              📸 Take Snapshot
            </button>
            
            {webcamStream && (
              <div style={{ marginTop: '12px', fontSize: '14px', opacity: 0.7 }}>
                GPU Acceleration: <strong>{gpuAcceleration ? 'Enabled' : 'Disabled'}</strong>
              </div>
            )}
          </div>
        </div>

        {/* Shape Controls */}
        <div style={{
          background: getPalette().surface,
          padding: '24px',
          borderRadius: '12px',
          marginBottom: '30px',
          border: '1px solid #00ff41'
        }}>
          <h2 style={{ marginBottom: '20px' }}>🔷 Camera Shapes</h2>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '16px', marginBottom: '20px' }}>
            {shapes.map(shape => (
              <button
                key={shape.id}
                onClick={() => setSelectedShape(shape.id)}
                style={{
                  background: selectedShape === shape.id ? '#00ff41' : getPalette().bg,
                  color: selectedShape === shape.id ? getPalette().bg : '#00ff41',
                  border: `2px solid #00ff41`,
                  padding: '16px',
                  borderRadius: '8px',
                  fontSize: '24px',
                  cursor: 'pointer',
                  transition: 'all 0.3s ease',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  gap: '8px'
                }}
              >
                <span>{shape.icon}</span>
                <span style={{ fontSize: '12px' }}>{shape.label}</span>
              </button>
            ))}
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
            <div>
              <label>Shape Size</label>
              <input
                type="range"
                min="20"
                max="200"
                value={shapeSize}
                onChange={(e) => setShapeSize(parseInt(e.target.value))}
                style={{ width: '100%', marginTop: '8px' }}
              />
              <div style={{ textAlign: 'center', fontSize: '12px', opacity: 0.7 }}>
                {shapeSize}px
              </div>
            </div>
            
            <div>
              <label>Shape Color</label>
              <input
                type="color"
                value={shapeColor}
                onChange={(e) => setShapeColor(e.target.value)}
                style={{ 
                  width: '100%', 
                  height: '40px',
                  marginTop: '8px',
                  border: '1px solid #00ff41',
                  borderRadius: '4px',
                  background: getPalette().bg
                }}
              />
            </div>
            
            <div>
              <label>
                <input
                  type="checkbox"
                  checked={shapeBorder}
                  onChange={(e) => setShapeBorder(e.target.checked)}
                  style={{ marginRight: '8px' }}
                />
                Shape Border
              </label>
            </div>
            
            <div>
              <label>GPU Acceleration</label>
              <input
                type="checkbox"
                checked={gpuAcceleration}
                onChange={(e) => setGpuAcceleration(e.target.checked)}
              />
            </div>
          </div>

          <div style={{ marginTop: '20px' }}>
            <label>Animation Style</label>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', gap: '12px' }}>
              {animations.map(animation => (
                <button
                  key={animation.id}
                  onClick={() => setAnimationStyle(animation.id)}
                  style={{
                    background: animationStyle === animation.id ? '#00ff41' : getPalette().bg,
                    color: animationStyle === animation.id ? getPalette().bg : '#00ff41',
                    border: '1px solid #00ff41',
                    padding: '12px',
                    borderRadius: '8px',
                    fontSize: '12px',
                    cursor: 'pointer'
                  }}
                >
                  {animation.label}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Video Effects */}
        <div style={{
          background: getPalette().surface,
          padding: '24px',
          borderRadius: '12px',
          marginBottom: '30px',
          border: '1px solid #00ff41'
        }}>
          <h2 style={{ marginBottom: '20px' }}>✨ Video Effects</h2>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', gap: '12px', marginBottom: '20px' }}>
            {['blur', 'grayscale', 'sepia', 'brightness', 'contrast', 'pixelate', 'rainbow'].map(effect => (
              <button
                key={effect}
                onClick={() => toggleEffect(effect)}
                style={{
                  background: effects.includes(effect) ? '#00ff41' : getPalette().bg,
                  color: effects.includes(effect) ? getPalette().bg : '#00ff41',
                  border: '1px solid #00ff41',
                  padding: '12px 16px',
                  borderRadius: '8px',
                  fontSize: '14px',
                  fontWeight: 'bold',
                  cursor: 'pointer',
                  textTransform: 'capitalize',
                  boxShadow: effects.includes(effect) ? '0 4px 12px rgba(0, 255, 65, 0.3)' : 'none'
                }}
              >
                {effect}
              </button>
            ))}
          </div>

          <div style={{ marginBottom: '20px' }}>
            <h3 style={{ marginBottom: '15px', color: '#00ff41' }}>Effect Presets</h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '12px' }}>
              {effectPresets.map(preset => (
                <button
                  key={preset.id}
                  onClick={() => {
                    setEffects(preset.effects);
                    setAnimationStyle(preset.animation);
                  }}
                  style={{
                    background: effects.length === 0 && preset.effects.length === 0 ? getPalette().bg : '#00ff41',
                    color: effects.length === 0 && preset.effects.length === 0 ? getPalette().text : '#00ff41',
                    border: '1px solid #00ff41',
                    padding: '16px',
                    borderRadius: '8px',
                    fontSize: '14px',
                    fontWeight: 'bold',
                    cursor: 'pointer'
                  }}
                >
                  {preset.name}
                </button>
              ))}
            </div>
          </div>

          {effects.length > 0 && (
            <div style={{ marginTop: '20px', textAlign: 'center' }}>
              <button
                onClick={() => setEffects([])}
                style={{
                  background: '#00ff41',
                  color: getPalette().bg,
                  border: 'none',
                  padding: '12px 24px',
                  borderRadius: '8px',
                  fontSize: '16px',
                  fontWeight: 'bold',
                  cursor: 'pointer'
                }}
              >
                🔄 Reset Effects
              </button>
            </div>
          )}
        </div>

        {/* Active Effects Display */}
        {effects.length > 0 && (
          <div style={{
            background: getPalette().surface,
            padding: '20px',
            borderRadius: '12px',
            border: '1px solid #00ff41'
          }}>
            <h3 style={{ marginBottom: '15px' }}>🎨 Active Effects</h3>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
              {effects.map(effect => (
                <span
                  key={effect}
                  style={{
                    background: '#00ff41',
                    color: getPalette().bg,
                    padding: '6px 12px',
                    borderRadius: '16px',
                    fontSize: '12px',
                    fontWeight: 'bold',
                    textTransform: 'capitalize'
                  }}
                >
                  {effect}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}