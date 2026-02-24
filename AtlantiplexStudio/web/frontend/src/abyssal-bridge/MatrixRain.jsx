import React, { useEffect, useRef } from 'react';

/**
 * MatrixRain - Digital cascade effect
 * Creates falling digital characters like The Matrix
 */
const MatrixRain = ({ intensity = 'medium' }) => {
  const canvasRef = useRef(null);
  const animationRef = useRef(null);
  
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // Set canvas size
    const resizeCanvas = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);
    
    // Matrix characters - mix of katakana, numbers, and symbols
    const chars = 'アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ@#$%^&*()_+-=[]{}|;:,.<>?/~`';
    
    // Configure based on intensity
    const config = {
      low: { fontSize: 14, columns: 0.3, speed: 0.5, opacity: 0.03 },
      medium: { fontSize: 12, columns: 0.5, speed: 1, opacity: 0.05 },
      high: { fontSize: 10, columns: 1, speed: 1.5, opacity: 0.08 }
    }[intensity] || config.medium;
    
    const fontSize = config.fontSize;
    const columns = Math.floor(canvas.width / fontSize * config.columns);
    
    // Drops array - position of each column
    const drops = [];
    for (let i = 0; i < columns; i++) {
      drops[i] = Math.random() * -100; // Start above screen
    }
    
    // Colors for depth effect
    const getColor = (isHead) => {
      if (isHead) {
        return '#FFFFFF'; // White heads
      }
      // Mix of Matrix green and abyssal cyan
      const colors = ['#00FF8A', '#00F6FF', '#00FF41', '#008F11'];
      return colors[Math.floor(Math.random() * colors.length)];
    };
    
    let frameCount = 0;
    
    const draw = () => {
      // Semi-transparent black to create trail effect
      ctx.fillStyle = `rgba(2, 4, 10, ${config.opacity})`;
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      
      ctx.font = `${fontSize}px 'Courier New', monospace`;
      
      for (let i = 0; i < drops.length; i++) {
        // Random character
        const char = chars[Math.floor(Math.random() * chars.length)];
        
        // Head of the column (brightest)
        const isHead = Math.random() > 0.95;
        ctx.fillStyle = getColor(isHead);
        ctx.fillText(char, i * fontSize / config.columns, drops[i] * fontSize);
        
        // Reset drop to top randomly after it crosses screen
        if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
          drops[i] = 0;
        }
        
        // Move drop down
        drops[i] += config.speed;
      }
      
      frameCount++;
      animationRef.current = requestAnimationFrame(draw);
    };
    
    draw();
    
    return () => {
      window.removeEventListener('resize', resizeCanvas);
      cancelAnimationFrame(animationRef.current);
    };
  }, [intensity]);
  
  return (
    <canvas
      ref={canvasRef}
      className="matrix-rain"
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        pointerEvents: 'none',
        zIndex: 1,
        opacity: 0.4
      }}
    />
  );
};

export default MatrixRain;