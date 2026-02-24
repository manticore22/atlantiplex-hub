import React, { useEffect, useRef } from 'react';

/**
 * HolographicOverlay - Scanlines and holographic effects
 * Adds futuristic holographic display aesthetics
 */
const HolographicOverlay = () => {
  const canvasRef = useRef(null);
  const animationRef = useRef(null);
  
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    let time = 0;
    
    const resizeCanvas = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);
    
    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      // Scanlines
      ctx.strokeStyle = 'rgba(0, 246, 255, 0.03)';
      ctx.lineWidth = 1;
      for (let y = 0; y < canvas.height; y += 4) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(canvas.width, y);
        ctx.stroke();
      }
      
      // Moving scanline
      const scanlineY = (time * 2) % canvas.height;
      const gradient = ctx.createLinearGradient(0, scanlineY - 50, 0, scanlineY + 50);
      gradient.addColorStop(0, 'rgba(0, 246, 255, 0)');
      gradient.addColorStop(0.5, 'rgba(0, 246, 255, 0.1)');
      gradient.addColorStop(1, 'rgba(0, 246, 255, 0)');
      ctx.fillStyle = gradient;
      ctx.fillRect(0, scanlineY - 50, canvas.width, 100);
      
      // Corner brackets (holographic frame)
      const cornerSize = 30;
      const lineWidth = 2;
      ctx.strokeStyle = 'rgba(0, 246, 255, 0.3)';
      ctx.lineWidth = lineWidth;
      
      // Top-left corner
      ctx.beginPath();
      ctx.moveTo(cornerSize, 0);
      ctx.lineTo(0, 0);
      ctx.lineTo(0, cornerSize);
      ctx.stroke();
      
      // Top-right corner
      ctx.beginPath();
      ctx.moveTo(canvas.width - cornerSize, 0);
      ctx.lineTo(canvas.width, 0);
      ctx.lineTo(canvas.width, cornerSize);
      ctx.stroke();
      
      // Bottom-left corner
      ctx.beginPath();
      ctx.moveTo(0, canvas.height - cornerSize);
      ctx.lineTo(0, canvas.height);
      ctx.lineTo(cornerSize, canvas.height);
      ctx.stroke();
      
      // Bottom-right corner
      ctx.beginPath();
      ctx.moveTo(canvas.width - cornerSize, canvas.height);
      ctx.lineTo(canvas.width, canvas.height);
      ctx.lineTo(canvas.width, canvas.height - cornerSize);
      ctx.stroke();
      
      // Random glitch lines
      if (Math.random() > 0.98) {
        const glitchY = Math.random() * canvas.height;
        const glitchHeight = Math.random() * 20 + 5;
        ctx.fillStyle = 'rgba(0, 246, 255, 0.1)';
        ctx.fillRect(0, glitchY, canvas.width, glitchHeight);
      }
      
      time += 1;
      animationRef.current = requestAnimationFrame(draw);
    };
    
    draw();
    
    return () => {
      window.removeEventListener('resize', resizeCanvas);
      cancelAnimationFrame(animationRef.current);
    };
  }, []);
  
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
        zIndex: 3
      }}
    />
  );
};

export default HolographicOverlay;