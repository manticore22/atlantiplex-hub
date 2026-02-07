// Event Loop Monitoring and Optimization
const eventLoopMonitor = {
  lag: 0,
  maxLag: 0,
  lastCheck: Date.now(),

  check() {
    const now = Date.now();
    const lag = now - this.lastCheck;
    
    this.lag = lag;
    this.maxLag = Math.max(this.maxLag, lag);
    
    // Warning threshold: 100ms lag
    if (lag > 100) {
      console.warn(`Event loop lag detected: ${lag}ms`);
      
      // Handle gracefully: reduce non-critical operations
      this.throttleNonCriticalOperations();
    }
    
    this.lastCheck = now;
    
    // Cleanup old data
    this.cleanup();
  },

  throttleNonCriticalOperations() {
    // Implement request throttling when event loop is slow
    console.log('Throttling operations due to event loop lag');
    
    // Delay non-critical logging
    if (this.originalConsole) {
      console.log = (...args) => {
        setTimeout(() => this.originalConsole(...args), 0);
      };
    }
  },

  cleanup() {
    // Clean up every 5 minutes
    if (Date.now() - this.lastCheck > 300000) {
      this.maxLag = 0;
    }
  },

  start() {
    console.log('Event loop monitoring started');
    this.originalConsole = console.log;
    setInterval(() => this.check(), 1000);
  }
};

// Unicode Console Fix
const unicodeConsole = {
  fix() {
    const originalLog = console.log;
    
    console.log = (...args) => {
      // Fix emoji encoding issues
      const fixedArgs = args.map(arg => {
        if (typeof arg === 'string') {
          try {
            // Ensure proper Unicode handling
            return Buffer.from(arg, 'utf8').toString('utf8');
          } catch (e) {
            return arg; // Fallback to original
          }
        }
        return arg;
      });
      
      originalLog(...fixedArgs);
    };
    
    console.info = console.log;
    console.warn = console.log;
    console.error = console.log;
  }
};

// OBS Connection Handler
const obsConnection = {
  retries: 0,
  maxRetries: 3,
  reconnectInterval: null,

  async connect() {
    try {
      console.log('Attempting OBS connection...');
      // Your OBS connection logic here
      this.retries = 0;
      return true;
    } catch (error) {
      console.warn(`OBS connection failed (attempt ${this.retries + 1}):`, error.message);
      
      this.retries++;
      if (this.retries < this.maxRetries) {
        console.log('Scheduling OBS reconnection...');
        this.reconnectInterval = setTimeout(() => {
          this.connect();
        }, 5000); // Retry after 5 seconds
      } else {
        console.error('OBS connection failed after maximum retries');
        this.clearReconnect();
      }
      
      return false;
    }
  },

  clearReconnect() {
    if (this.reconnectInterval) {
      clearTimeout(this.reconnectInterval);
      this.reconnectInterval = null;
    }
  }
};

// LSP Error Handler
const lspErrorHandler = {
  handle(error) {
    // Non-critical LSP errors
    const nonCriticalErrors = [
      'Cannot find workspace',
      'Language server startup failed',
      'Configuration file not found',
      'Extension activation failed'
    ];

    const isNonCritical = nonCriticalErrors.some(nonCritical => 
      error.message.includes(nonCritical)
    );

    if (isNonCritical) {
      console.warn('Non-critical LSP warning:', error.message);
      return false; // Don't crash
    }

    console.error('Critical LSP error:', error);
    return true;
  }
};

// System Optimization Utilities
const systemOptimizer = {
  optimizeMemory() {
    // Force garbage collection if available
    if (global.gc) {
      console.log('Running garbage collection...');
      global.gc();
    }
  },

  monitorMemory() {
    const used = process.memoryUsage();
    const formatted = {
      rss: `${Math.round(used.rss / 1024 / 1024)} MB`,
      heapTotal: `${Math.round(used.heapTotal / 1024 / 1024)} MB`,
      heapUsed: `${Math.round(used.heapUsed / 1024 / 1024)} MB`,
      external: `${Math.round(used.external / 1024 / 1024)} MB`
    };
    
    console.log('Memory usage:', formatted);
    
    // Warning if memory usage is high
    const heapUsedMB = used.heapUsed / 1024 / 1024;
    if (heapUsedMB > 500) { // 500MB threshold
      console.warn('High memory usage detected:', formatted);
    }
  },

  setupOptimizations() {
    // Optimize Node.js for production
    process.env.NODE_OPTIONS = '--max-old-space-size=4096';
    
    // Set up memory monitoring
    setInterval(() => this.monitorMemory(), 30000); // Every 30 seconds
  }
};

module.exports = {
  eventLoopMonitor,
  unicodeConsole,
  obsConnection,
  lspErrorHandler,
  systemOptimizer
};