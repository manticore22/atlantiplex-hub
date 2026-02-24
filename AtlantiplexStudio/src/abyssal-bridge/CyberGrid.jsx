import React, { useEffect, useRef } from 'react';

/**
 * CyberGrid - Perspective grid and hex patterns
 * Creates futuristic grid floor and ceiling effect
 */
const CyberGrid = () => {
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
      
      const centerX = canvas.width / 2;
      const centerY = canvas.height / 2;
      
      // Perspective floor grid
      ctx.strokeStyle = 'rgba(0, 246, 255, 0.08)';
      ctx.lineWidth = 1;
      
      // Horizontal lines (perspective)
      for (let i = 0; i < 20; i++) {
        const y = centerY + (i * i * 2);
        if (y > canvas.height) break;
        
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(canvas.width, y);
        ctx.stroke();
      }
      
      // Vertical lines radiating from center
      for (let i = -10; i <= 10; i++) {
        const x = centerX + (i * 100);
        ctx.beginPath();
        ctx.moveTo(centerX, centerY);
        ctx.lineTo(x + (i * 200), canvas.height);
        ctx.stroke();
      }
      
      // Floating hexagons
      const drawHexagon = (x, y, size, alpha) => {
        ctx.beginPath();
        for (let i = 0; i < 6; i++) {
          const angle = (Math.PI / 3) * i - Math.PI / 2;
          const hx = x + size * Math.cos(angle);
          const hy = y + size * Math.sin(angle);
          if (i === 0) ctx.moveTo(hx, hy);
          else ctx.lineTo(hx, hy);
        }
        ctx.closePath();
        ctx.strokeStyle = `rgba(106, 0, 255, ${alpha})`;
        ctx.stroke();
      };
      
      // Animate floating hexes
      for (let i = 0; i < 5; i++) {
        const x = (canvas.width / 6) * (i + 1);
        const y = 100 + Math.sin(time * 0.01 + i) * 30;
        const size = 20 + Math.sin(time * 0.02 + i) * 5;
        const alpha = 0.1 + Math.sin(time * 0.03 + i) * 0.05;
        drawHexagon(x, y, size, alpha);
      }
      
      // Data stream indicators on sides
      const drawDataStream = (x, isRight) => {
        const streamHeight = 150;
        const offset = (time * 2) % streamHeight;
        
        for (let i = 0; i < 5; i++) {
          const y = 200 + (i * 80) + offset;
          if (y > canvas.height - 200) continue;
          
          ctx.fillStyle = `rgba(0, 255, 138, ${0.3 - (i * 0.05)})`;
          ctx.fillRect(x, y, isRight ? 3 : -3, 20);
        }
      };
      
      drawDataStream(20, false);
      drawDataStream(canvas.width - 20, true);
      
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
        zIndex: 1
      }}
    />
  );
};

export default CyberGrid;
