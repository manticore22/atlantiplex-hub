const express = require('express');
const speakeasy = require('speakeasy');
const qrcode = require('qrcode');
const twilio = require('twilio');
const router = express.Router();

// Initialize Twilio client
const twilioClient = twilio(
  process.env.TWILIO_ACCOUNT_SID,
  process.env.TWILIO_AUTH_TOKEN
);

// Setup 2FA with Authenticator App
router.post('/setup', async (req, res) => {
  try {
    const { userId } = req.body;
    
    // Generate secret key for user
    const secret = speakeasy.generateSecret({
      name: `Atlantiplex Studio (${userId})`,
      issuer: 'Atlantiplex Studio'
    });

    // Generate QR Code URL
    const qrCodeUrl = await qrcode.toDataURL(secret.otpauth_url);

    // Generate backup codes
    const backupCodes = Array.from({ length: 10 }, () => 
      speakeasy.generateSecret({ length: 32 }).base32.substring(0, 8)
    );

    // Store secret and backup codes in database (encrypted)
    await storeUser2FASecret(userId, {
      secret: secret.base32,
      backupCodes: backupCodes,
      method: 'authenticator',
      enabled: false
    });

    res.json({
      secret: secret.base32,
      qrCodeUrl: qrCodeUrl,
      backupCodes: backupCodes,
      manualEntryKey: secret.base32
    });
  } catch (error) {
    console.error('2FA setup error:', error);
    res.status(500).json({ 
      error: 'Failed to setup 2FA',
      details: error.message 
    });
  }
});

// Verify Authenticator Code
router.post('/verify', async (req, res) => {
  try {
    const { userId, token } = req.body;
    
    // Get user's 2FA secret from database
    const user2FA = await getUser2FASettings(userId);
    
    if (!user2FA || !user2FA.secret) {
      return res.status(400).json({ 
        error: '2FA not set up for this user' 
      });
    }

    // Verify the token
    const verified = speakeasy.totp.verify({
      secret: user2FA.secret,
      encoding: 'base32',
      token: token,
      window: 2, // Allow 2 time steps (30 seconds each) for clock drift
      time: Math.floor(Date.now() / 1000)
    });

    if (verified) {
      // Enable 2FA for user
      await enableUser2FA(userId, 'authenticator');
      
      res.json({ 
        verified: true,
        message: '2FA enabled successfully'
      });
    } else {
      res.json({ 
        verified: false,
        message: 'Invalid verification code'
      });
    }
  } catch (error) {
    console.error('2FA verification error:', error);
    res.status(500).json({ 
      error: 'Verification failed',
      details: error.message 
    });
  }
});

// Send SMS OTP
router.post('/send-otp', async (req, res) => {
  try {
    const { userId, phoneNumber } = req.body;
    
    // Validate phone number
    if (!isValidPhoneNumber(phoneNumber)) {
      return res.status(400).json({ 
        error: 'Invalid phone number format' 
      });
    }

    // Generate OTP
    const otp = generateOTP();
    const otpExpiry = new Date(Date.now() + 10 * 60 * 1000); // 10 minutes

    // Store OTP in database with expiry
    await storeOTP(userId, {
      code: otp,
      phoneNumber: phoneNumber,
      expiresAt: otpExpiry,
      attempts: 0
    });

    // Send SMS via Twilio
    await twilioClient.messages.create({
      body: `Your Atlantiplex Studio verification code is: ${otp}. This code will expire in 10 minutes.`,
      from: process.env.TWILIO_PHONE_NUMBER,
      to: phoneNumber
    });

    res.json({ 
      success: true,
      message: 'OTP sent successfully'
    });
  } catch (error) {
    console.error('OTP send error:', error);
    res.status(500).json({ 
      error: 'Failed to send OTP',
      details: error.message 
    });
  }
});

// Verify SMS OTP
router.post('/verify-otp', async (req, res) => {
  try {
    const { userId, code } = req.body;
    
    // Get stored OTP
    const storedOTP = await getStoredOTP(userId);
    
    if (!storedOTP) {
      return res.status(400).json({ 
        error: 'No OTP found. Please request a new one.' 
      });
    }

    // Check if OTP is expired
    if (new Date() > storedOTP.expiresAt) {
      await clearStoredOTP(userId);
      return res.status(400).json({ 
        error: 'OTP has expired. Please request a new one.' 
      });
    }

    // Check attempts limit
    if (storedOTP.attempts >= 3) {
      await clearStoredOTP(userId);
      return res.status(400).json({ 
        error: 'Too many attempts. Please request a new OTP.' 
      });
    }

    // Increment attempts
    await incrementOTPAttempts(userId);

    // Verify OTP
    if (storedOTP.code === code) {
      // Enable SMS 2FA for user
      await enableUser2FA(userId, 'sms', {
        phoneNumber: storedOTP.phoneNumber
      });
      
      // Clear used OTP
      await clearStoredOTP(userId);

      res.json({ 
        verified: true,
        message: 'Phone number verified successfully'
      });
    } else {
      res.json({ 
        verified: false,
        message: 'Invalid OTP code'
      });
    }
  } catch (error) {
    console.error('OTP verification error:', error);
    res.status(500).json({ 
      error: 'OTP verification failed',
      details: error.message 
    });
  }
});

// Verify 2FA during login
router.post('/login-verify', async (req, res) => {
  try {
    const { userId, token, backupCode } = req.body;
    
    // Get user's 2FA settings
    const user2FA = await getUser2FASettings(userId);
    
    if (!user2FA || !user2FA.enabled) {
      return res.status(400).json({ 
        error: '2FA not enabled for this user' 
      });
    }

    let verified = false;
    let method = 'unknown';

    // Check backup code first
    if (backupCode) {
      verified = user2FA.backupCodes.includes(backupCode);
      if (verified) {
        method = 'backup';
        // Remove used backup code
        await removeBackupCode(userId, backupCode);
      }
    }
    // Check authenticator token
    else if (user2FA.method === 'authenticator' && token) {
      verified = speakeasy.totp.verify({
        secret: user2FA.secret,
        encoding: 'base32',
        token: token,
        window: 2,
        time: Math.floor(Date.now() / 1000)
      });
      method = 'authenticator';
    }
    // Check SMS method
    else if (user2FA.method === 'sms' && token) {
      // For SMS, you might want to resend OTP if needed
      const storedOTP = await getStoredOTP(userId);
      verified = storedOTP && storedOTP.code === token && new Date() <= storedOTP.expiresAt;
      method = 'sms';
    }

    if (verified) {
      // Log successful 2FA verification
      await log2FAAttempt(userId, method, true);
      
      res.json({ 
        verified: true,
        method: method,
        message: '2FA verification successful'
      });
    } else {
      // Log failed attempt
      await log2FAAttempt(userId, method || 'unknown', false);
      
      res.json({ 
        verified: false,
        message: 'Invalid verification code'
      });
    }
  } catch (error) {
    console.error('Login 2FA verification error:', error);
    res.status(500).json({ 
      error: '2FA verification failed',
      details: error.message 
    });
  }
});

// Disable 2FA
router.post('/disable', async (req, res) => {
  try {
    const { userId, password } = req.body;
    
    // Verify user's password before disabling 2FA
    const user = await getUserById(userId);
    const passwordValid = await verifyPassword(password, user.password);
    
    if (!passwordValid) {
      return res.status(400).json({ 
        error: 'Invalid password' 
      });
    }

    // Disable 2FA
    await disableUser2FA(userId);

    res.json({ 
      success: true,
      message: '2FA disabled successfully'
    });
  } catch (error) {
    console.error('2FA disable error:', error);
    res.status(500).json({ 
      error: 'Failed to disable 2FA',
      details: error.message 
    });
  }
});

// Regenerate backup codes
router.post('/regenerate-backup-codes', async (req, res) => {
  try {
    const { userId } = req.body;
    
    // Generate new backup codes
    const newBackupCodes = Array.from({ length: 10 }, () => 
      speakeasy.generateSecret({ length: 32 }).base32.substring(0, 8)
    );

    // Update backup codes in database
    await updateBackupCodes(userId, newBackupCodes);

    res.json({ 
      backupCodes: newBackupCodes,
      message: 'Backup codes regenerated successfully'
    });
  } catch (error) {
    console.error('Backup codes regeneration error:', error);
    res.status(500).json({ 
      error: 'Failed to regenerate backup codes',
      details: error.message 
    });
  }
});

// Helper functions
function generateOTP() {
  return Math.floor(100000 + Math.random() * 900000).toString();
}

function isValidPhoneNumber(phone) {
  // Basic phone number validation
  const phoneRegex = /^\+?[1-9]\d{1,14}$/;
  return phoneRegex.test(phone.replace(/[\s\-\(\)]/g, ''));
}

// Database helper functions (implement these based on your database)
async function storeUser2FASecret(userId, data) {
  // Store 2FA settings in database
  console.log('Storing 2FA for user:', userId, data);
}

async function getUser2FASettings(userId) {
  // Get user's 2FA settings from database
  console.log('Getting 2FA settings for user:', userId);
  return null; // Return actual data
}

async function enableUser2FA(userId, method, additionalData = {}) {
  // Enable 2FA for user
  console.log('Enabling 2FA for user:', userId, method, additionalData);
}

async function storeOTP(userId, otpData) {
  // Store OTP in database
  console.log('Storing OTP for user:', userId, otpData);
}

async function getStoredOTP(userId) {
  // Get stored OTP from database
  console.log('Getting OTP for user:', userId);
  return null; // Return actual data
}

async function clearStoredOTP(userId) {
  // Clear OTP from database
  console.log('Clearing OTP for user:', userId);
}

async function incrementOTPAttempts(userId) {
  // Increment OTP attempts
  console.log('Incrementing OTP attempts for user:', userId);
}

async function removeBackupCode(userId, backupCode) {
  // Remove used backup code
  console.log('Removing backup code for user:', userId, backupCode);
}

async function log2FAAttempt(userId, method, success) {
  // Log 2FA attempt for security monitoring
  console.log('Logging 2FA attempt:', { userId, method, success, timestamp: new Date() });
}

async function getUserById(userId) {
  // Get user from database
  console.log('Getting user by ID:', userId);
  return null; // Return actual user data
}

async function verifyPassword(password, hashedPassword) {
  // Verify password against hash
  console.log('Verifying password for user');
  return true; // Return actual verification result
}

async function disableUser2FA(userId) {
  // Disable 2FA for user
  console.log('Disabling 2FA for user:', userId);
}

async function updateBackupCodes(userId, backupCodes) {
  // Update backup codes in database
  console.log('Updating backup codes for user:', userId, backupCodes);
}

module.exports = router;