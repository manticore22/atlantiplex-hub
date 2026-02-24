import React, { useState, useEffect } from 'react';
import { QRCodeSVG } from 'qrcode.react';

const MobileAuthenticator = ({ user, onVerificationComplete, onCancel }) => {
  const [step, setStep] = useState('setup'); // setup, verify, complete
  const [secretKey, setSecretKey] = useState('');
  const [qrCodeUrl, setQrCodeUrl] = useState('');
  const [verificationCode, setVerificationCode] = useState('');
  const [backupCodes, setBackupCodes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [timeRemaining, setTimeRemaining] = useState(30);
  const [phoneNumber, setPhoneNumber] = useState('');
  const [otpSent, setOtpSent] = useState(false);

  useEffect(() => {
    if (step === 'setup') {
      generateSecretKey();
    }
  }, [step]);

  useEffect(() => {
    const timer = setInterval(() => {
      setTimeRemaining((prev) => {
        if (prev <= 1) return 30;
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  const generateSecretKey = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/auth/2fa/setup', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ userId: user.id })
      });

      const data = await response.json();
      
      if (response.ok) {
        setSecretKey(data.secret);
        setQrCodeUrl(data.qrCodeUrl);
        setBackupCodes(data.backupCodes);
      } else {
        setError(data.error || 'Failed to setup 2FA');
      }
    } catch (error) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const verifyAuthenticatorCode = async () => {
    if (!verificationCode) {
      setError('Please enter the verification code');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await fetch('/api/auth/2fa/verify', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          userId: user.id,
          token: verificationCode
        })
      });

      const data = await response.json();
      
      if (response.ok && data.verified) {
        setStep('complete');
        onVerificationComplete({
          method: 'authenticator',
          secret: secretKey,
          backupCodes: backupCodes
        });
      } else {
        setError('Invalid verification code');
      }
    } catch (error) {
      setError('Verification failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const sendOTP = async () => {
    if (!phoneNumber) {
      setError('Please enter your phone number');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await fetch('/api/auth/2fa/send-otp', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          userId: user.id,
          phoneNumber: phoneNumber
        })
      });

      const data = await response.json();
      
      if (response.ok) {
        setOtpSent(true);
        setTimeout(() => setOtpSent(false), 60000); // Reset after 1 minute
      } else {
        setError(data.error || 'Failed to send OTP');
      }
    } catch (error) {
      setError('Failed to send OTP. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const verifyOTP = async () => {
    if (!verificationCode) {
      setError('Please enter the OTP code');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await fetch('/api/auth/2fa/verify-otp', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          userId: user.id,
          code: verificationCode
        })
      });

      const data = await response.json();
      
      if (response.ok && data.verified) {
        setStep('complete');
        onVerificationComplete({
          method: 'sms',
          phoneNumber: phoneNumber
        });
      } else {
        setError('Invalid OTP code');
      }
    } catch (error) {
      setError('OTP verification failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const downloadBackupCodes = () => {
    const element = document.createElement('a');
    const file = new Blob([backupCodes.join('\n')], { type: 'text/plain' });
    element.href = URL.createObjectURL(file);
    element.download = 'backup-codes.txt';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  const renderSetupStep = () => (
    <div className="authenticator-setup">
      <h2>Setup Two-Factor Authentication</h2>
      
      <div className="method-selector">
        <button
          className={`method-btn ${step === 'setup' ? 'active' : ''}`}
          onClick={() => setStep('setup')}
        >
          📱 Authenticator App
        </button>
        <button
          className={`method-btn ${step === 'sms' ? 'active' : ''}`}
          onClick={() => setStep('sms')}
        >
          💬 SMS/Phone
        </button>
      </div>

      {step === 'setup' ? (
        <div className="authenticator-method">
          <div className="step">
            <h3>1. Download an authenticator app</h3>
            <div className="app-options">
              <a href="https://authy.com/download/" target="_blank" rel="noopener noreferrer">
                <img src="/images/authy-logo.png" alt="Authy" />
                Authy
              </a>
              <a href="https://support.google.com/accounts/answer/1066447" target="_blank" rel="noopener noreferrer">
                <img src="/images/google-authenticator.png" alt="Google Authenticator" />
                Google Authenticator
              </a>
              <a href="https://microsoft.com/en-us/account/authenticator/" target="_blank" rel="noopener noreferrer">
                <img src="/images/microsoft-authenticator.png" alt="Microsoft Authenticator" />
                Microsoft Authenticator
              </a>
            </div>
          </div>

          <div className="step">
            <h3>2. Scan the QR Code</h3>
            <div className="qr-code-container">
              {qrCodeUrl && <QRCodeSVG value={qrCodeUrl} size={200} />}
              <p>Or manually enter this code: <code>{secretKey}</code></p>
            </div>
          </div>

          <div className="step">
            <h3>3. Enter the verification code</h3>
            <div className="verification-input">
              <input
                type="text"
                maxLength={6}
                placeholder="000000"
                value={verificationCode}
                onChange={(e) => setVerificationCode(e.target.value.replace(/\D/g, ''))}
                className="otp-input"
              />
              <div className="timer">
                ⏰ Code refreshes in {timeRemaining}s
              </div>
            </div>
          </div>

          <div className="backup-codes">
            <h3>4. Save your backup codes</h3>
            <div className="codes-grid">
              {backupCodes.slice(0, 4).map((code, index) => (
                <div key={index} className="backup-code">{code}</div>
              ))}
            </div>
            <button onClick={downloadBackupCodes} className="download-codes-btn">
              📥 Download All Backup Codes
            </button>
          </div>

          <div className="setup-actions">
            <button
              onClick={verifyAuthenticatorCode}
              disabled={loading || verificationCode.length !== 6}
              className="verify-btn"
            >
              {loading ? 'Verifying...' : 'Enable 2FA'}
            </button>
            <button onClick={onCancel} className="cancel-btn">
              Cancel
            </button>
          </div>
        </div>
      ) : (
        <div className="sms-method">
          <div className="step">
            <h3>Enter your phone number</h3>
            <div className="phone-input">
              <input
                type="tel"
                placeholder="+1 (555) 123-4567"
                value={phoneNumber}
                onChange={(e) => setPhoneNumber(e.target.value)}
                className="phone-number-input"
              />
            </div>
          </div>

          <div className="step">
            <button
              onClick={sendOTP}
              disabled={loading || !phoneNumber || otpSent}
              className="send-otp-btn"
            >
              {loading ? 'Sending...' : otpSent ? 'OTP Sent' : 'Send Verification Code'}
            </button>
            {otpSent && <p className="otp-sent-message">OTP sent to your phone. Check your messages.</p>}
          </div>

          <div className="step">
            <h3>Enter the verification code</h3>
            <input
              type="text"
              maxLength={6}
              placeholder="000000"
              value={verificationCode}
              onChange={(e) => setVerificationCode(e.target.value.replace(/\D/g, ''))}
              className="otp-input"
              disabled={!otpSent}
            />
          </div>

          <div className="setup-actions">
            <button
              onClick={verifyOTP}
              disabled={loading || verificationCode.length !== 6 || !otpSent}
              className="verify-btn"
            >
              {loading ? 'Verifying...' : 'Verify Phone Number'}
            </button>
            <button onClick={onCancel} className="cancel-btn">
              Cancel
            </button>
          </div>
        </div>
      )}

      {error && <div className="error-message">{error}</div>}
    </div>
  );

  const renderCompleteStep = () => (
    <div className="authenticator-complete">
      <div className="success-icon">✅</div>
      <h2>Two-Factor Authentication Enabled!</h2>
      <p>Your account is now more secure with 2FA protection.</p>
      
      <div className="security-tips">
        <h3>Important Security Tips:</h3>
        <ul>
          <li>Save your backup codes in a safe place</li>
          <li>Don't share your authenticator app access</li>
          <li>Keep your recovery options updated</li>
          <li>Test your 2FA setup before logging out</li>
        </ul>
      </div>

      <button onClick={() => window.location.reload()} className="done-btn">
        Done
      </button>
    </div>
  );

  return (
    <div className="mobile-authenticator-modal">
      <div className="modal-overlay" onClick={onCancel}></div>
      <div className="modal-content">
        {step === 'complete' ? renderCompleteStep() : renderSetupStep()}
      </div>
    </div>
  );
};

export default MobileAuthenticator;