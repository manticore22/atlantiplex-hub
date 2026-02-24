# Node.js Security Configuration Example
# Place in apps/admin-dashboard/middleware/security.js or similar

const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const { body, validationResult } = require('express-validator');
const RedisStore = require('rate-limit-redis');
const redis = require('redis');

# Initialize Redis for rate limiting
const redisClient = redis.createClient({
  host: process.env.REDIS_HOST || 'localhost',
  port: process.env.REDIS_PORT || 6379,
  password: process.env.REDIS_PASSWORD,
});

# =====================
# HELMET SECURITY
# =====================

const helmetConfig = helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'", "'unsafe-inline'"],  # Reduce this in production
      styleSrc: ["'self'", "'unsafe-inline'"],
      imgSrc: ["'self'", "data:", "https:"],
      connectSrc: ["'self'", "https://api.stripe.com"],
      fontSrc: ["'self'"],
      objectSrc: ["'none'"],
      mediaSrc: ["'self'"],
      frameSrc: ["'self'"],
      upgradeInsecureRequests: [],
    },
  },
  crossOriginEmbedderPolicy: true,
  crossOriginOpenerPolicy: true,
  crossOriginResourcePolicy: { policy: "cross-origin" },
  dnsPrefetchControl: true,
  frameguard: { action: 'deny' },
  hidePoweredBy: true,
  hsts: {
    maxAge: 31536000,  # 1 year
    includeSubDomains: true,
    preload: true,
  },
  ieNoOpen: true,
  noSniff: true,
  originAgentCluster: true,
  referrerPolicy: { policy: "strict-origin-when-cross-origin" },
  xssFilter: true,
});

# =====================
# RATE LIMITING
# =====================

# General rate limiter
const limiter = rateLimit({
  store: new RedisStore({
    client: redisClient,
    prefix: 'rl:',
  }),
  windowMs: 15 * 60 * 1000,  # 15 minutes
  max: 100,  # Limit each IP to 100 requests per windowMs
  message: 'Too many requests from this IP, please try again later.',
  standardHeaders: true,
  legacyHeaders: false,
  skip: (req) => {
    # Skip rate limiting for health checks
    return req.path === '/health';
  },
});

# Strict rate limiter for login
const loginLimiter = rateLimit({
  store: new RedisStore({
    client: redisClient,
    prefix: 'rl_login:',
  }),
  windowMs: 15 * 60 * 1000,
  max: 5,  # Only 5 login attempts
  skipSuccessfulRequests: true,  # Don't count successful logins
  message: 'Too many login attempts, please try again later.',
});

# API rate limiter (stricter)
const apiLimiter = rateLimit({
  store: new RedisStore({
    client: redisClient,
    prefix: 'rl_api:',
  }),
  windowMs: 1 * 60 * 1000,  # 1 minute
  max: 60,
  message: 'Too many API requests, please slow down.',
});

# =====================
# INPUT VALIDATION
# =====================

const validateEmail = body('email')
  .isEmail()
  .normalizeEmail()
  .withMessage('Invalid email address');

const validatePassword = body('password')
  .isLength({ min: 12 })
  .withMessage('Password must be at least 12 characters')
  .matches(/[A-Z]/)
  .withMessage('Password must contain uppercase letter')
  .matches(/[a-z]/)
  .withMessage('Password must contain lowercase letter')
  .matches(/[0-9]/)
  .withMessage('Password must contain number')
  .matches(/[!@#$%^&*]/)
  .withMessage('Password must contain special character');

const validateInputMiddleware = [
  body('*').trim().escape(),  # Trim and escape all body fields
  (req, res, next) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }
    next();
  },
];

# =====================
# CORS CONFIGURATION
# =====================

const corsConfig = {
  origin: (process.env.CORS_ORIGIN || 'https://atlantiplex.example.com')
    .split(',')
    .map(o => o.trim()),
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization'],
  exposedHeaders: ['X-Total-Count', 'X-Page-Number'],
  maxAge: 86400,  # 24 hours
  optionsSuccessStatus: 200,
};

# =====================
# SESSION CONFIGURATION
# =====================

const sessionConfig = {
  secret: process.env.SESSION_SECRET,
  resave: false,
  saveUninitialized: false,
  store: new (require('connect-redis').default)(redisClient),
  cookie: {
    secure: process.env.NODE_ENV === 'production',  # HTTPS only
    httpOnly: true,  # No JS access
    sameSite: 'strict',  # CSRF protection
    maxAge: 24 * 60 * 60 * 1000,  # 24 hours
    domain: process.env.COOKIE_DOMAIN,
    path: '/',
  },
};

# =====================
# EXPORTS
# =====================

module.exports = {
  helmetConfig,
  limiter,
  loginLimiter,
  apiLimiter,
  validateEmail,
  validatePassword,
  validateInputMiddleware,
  corsConfig,
  sessionConfig,
};
