import React, { useEffect, useRef } from 'react';

/**
 * Abyssal Effects - Background visual effects
 * Deep-sea bioluminescence, particle drift, and holographic refraction
 */
const AbyssalEffects = () => {
  const canvasRef = useRef(null);
  const animationRef = useRef(null);
  
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    let particles = [];
    let time = 0;
    
    // Set canvas size
    const resizeCanvas = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);
    
    // Particle class
    class Particle {
      constructor() {
        this.reset();
      }
      
      reset() {
        this.x = Math.random() * canvas.width;
        this.y = canvas.height + Math.random() * 100;
        this.size = Math.random() * 2 + 0.5;
        this.speedY = Math.random() * 0.5 + 0.1;
        this.speedX = (Math.random() - 0.5) * 0.3;
        this.opacity = Math.random() * 0.5 + 0.1;
        this.color = this.getRandomColor();
        this.pulse = Math.random() * Math.PI * 2;
        this.pulseSpeed = Math.random() * 0.02 + 0.01;
      }
      
      getRandomColor() {
        const colors = [
          'rgba(0, 246, 255, ', // Cyan
          'rgba(106, 0, 255, ', // Violet
          'rgba(255, 62, 127, ', // Coral
          'rgba(0, 255, 138, '  // Green
        ];
        return colors[Math.floor(Math.random() * colors.length)];
      }
      
      update() {
        this.y -= this.speedY;
        this.x += this.speedX;
        this.pulse += this.pulseSpeed;
        
        // Pulsing opacity
        this.currentOpacity = this.opacity * (0.7 + 0.3 * Math.sin(this.pulse));
        
        // Reset if off screen
        if (this.y < -10) {
          this.reset();
        }
      }
      
      draw() {
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fillStyle = `${this.color}${this.currentOpacity})`;
        ctx.fill();
        
        // Glow effect
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size * 3, 0, Math.PI * 2);
        ctx.fillStyle = `${this.color}${this.currentOpacity * 0.2})`;
        ctx.fill();
      }
    }
    
    // Initialize particles
    for (let i = 0; i < 50; i++) {
      const particle = new Particle();
      particle.y = Math.random() * canvas.height;
      particles.push(particle);
    }
    
    // Draw caustics (light rays)
    const drawCaustics = () => {
      ctx.save();
      ctx.globalCompositeOperation = 'overlay';
      
      for (let i = 0; i < 5; i++) {
        const gradient = ctx.createLinearGradient(
          canvas.width * (0.1 + i * 0.2),
          0,
          canvas.width * (0.2 + i * 0.2),
          canvas.height
        );
        
        const opacity = 0.02 + 0.01 * Math.sin(time * 0.001 + i);
        gradient.addColorStop(0, `rgba(0, 246, 255, 0)`);
        gradient.addColorStop(0.5, `rgba(0, 246, 255, ${opacity})`);
        gradient.addColorStop(1, `rgba(0, 246, 255, 0)`);
        
        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, canvas.width, canvas.height);
      }
      
      ctx.restore();
    };
    
    // Draw vignette
    const drawVignette = () => {
      const gradient = ctx.createRadialGradient(
        canvas.width / 2,
        canvas.height / 2,
        canvas.height * 0.3,
        canvas.width / 2,
        canvas.height / 2,
        canvas.height * 0.8
      );
      
      gradient.addColorStop(0, 'rgba(2, 4, 10, 0)');
      gradient.addColorStop(1, 'rgba(2, 4, 10, 0.8)');
      
      ctx.fillStyle = gradient;
      ctx.fillRect(0, 0, canvas.width, canvas.height);
    };
    
    // Animation loop
    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      // Draw caustics
      drawCaustics();
      
      // Update and draw particles
      particles.forEach(particle => {
        particle.update();
        particle.draw();
      });
      
      // Draw vignette
      drawVignette();
      
      time += 16;
      animationRef.current = requestAnimationFrame(animate);
    };
    
    animate();
    
    return () => {
      window.removeEventListener('resize', resizeCanvas);
      cancelAnimationFrame(animationRef.current);
    };
  }, []);
  
  return (
    <canvas
      ref={canvasRef}
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        pointerEvents: 'none',
        zIndex: 0
      }}
    />
  );
};

export default AbyssalEffects;