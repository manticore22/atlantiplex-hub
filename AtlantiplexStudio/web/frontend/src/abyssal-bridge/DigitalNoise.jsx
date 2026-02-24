import React, { useEffect, useRef } from 'react';

/**
 * DigitalNoise - CRT static and digital noise effects
 * Adds retro-futuristic digital distortion
 */
const DigitalNoise = ({ intensity = 0.02 }) => {
  const canvasRef = useRef(null);
  const animationRef = useRef(null);
  
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    const resizeCanvas = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);
    
    const imageData = ctx.createImageData(canvas.width, canvas.height);
    const data = imageData.data;
    
    let frameCount = 0;
    
    const drawNoise = () => {
      frameCount++;
      
      // Only update every 3rd frame for performance
      if (frameCount % 3 === 0) {
        for (let i = 0; i < data.length; i += 4) {
          if (Math.random() < intensity) {
            const noise = Math.random() * 255;
            data[i] = noise;     // Red
            data[i + 1] = noise; // Green
            data[i + 2] = noise; // Blue
            data[i + 3] = 15;    // Alpha (very transparent)
          } else {
            data[i + 3] = 0; // Transparent
          }
        }
        ctx.putImageData(imageData, 0, 0);
      }
      
      animationRef.current = requestAnimationFrame(drawNoise);
    };
    
    drawNoise();
    
    return () => {
      window.removeEventListener('resize', resizeCanvas);
      cancelAnimationFrame(animationRef.current);
    };
  }, [intensity]);
  
  return (
    <canvas
      ref={canvasRef}
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        pointerEvents: 'none',
        zIndex: 2,
        mixBlendMode: 'overlay'
      }}
    />
  );
};

export default DigitalNoise;
