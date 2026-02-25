import React, { useState, useEffect, useCallback } from 'react';
import { Wifi, WifiOff, Download, RefreshCw, Home, Settings, Bell, X, Check, AlertCircle, Info } from 'lucide-react';

const PWAFeatures = () => {
  const [installPrompt, setInstallPrompt] = useState(null);
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [installStatus, setInstallStatus] = useState('available');
  const [updateAvailable, setUpdateAvailable] = useState(false);
  const [updateInstalling, setUpdateInstalling] = useState(false);
  const [notificationPermission, setNotificationPermission] = useState('default');
  const [storageEstimate, setStorageEstimate] = useState(null);

  useEffect(() => {
    // Check for service worker updates
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('/sw.js').then(registration => {
        registration.addEventListener('updatefound', () => {
          const newWorker = registration.installing;
          newWorker.addEventListener('statechange', () => {
            if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
              setUpdateAvailable(true);
            }
          });
        });
      });
    }

    // Listen for online/offline events
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);
    
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // Listen for beforeinstallprompt
    const handleBeforeInstallPrompt = (e) => {
      e.preventDefault();
      setInstallPrompt(e);
      setInstallStatus('prompted');
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);

    // Check storage quota
    if ('storage' in navigator && 'estimate' in navigator.storage) {
      navigator.storage.estimate().then(estimate => {
        setStorageEstimate(estimate);
      });
    }

    // Check notification permission
    if ('Notification' in window) {
      setNotificationPermission(Notification.permission);
    }

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    };
  }, []);

  const handleInstall = useCallback(async () => {
    if (!installPrompt) return;

    try {
      const result = await installPrompt.prompt();
      setInstallStatus(result.outcome === 'accepted' ? 'installing' : 'declined');
      setInstallPrompt(null);
    } catch (error) {
      console.error('Install error:', error);
      setInstallStatus('error');
    }
  }, [installPrompt]);

  const handleUpdate = useCallback(async () => {
    if (!('serviceWorker' in navigator)) return;

    setUpdateInstalling(true);
    
    try {
      const registration = await navigator.serviceWorker.ready;
      await registration.update();
      
      // Tell the new service worker to skip waiting
      registration.waiting?.postMessage({ type: 'SKIP_WAITING' });
      
      // Reload the page to get the new version
      window.location.reload();
    } catch (error) {
      console.error('Update error:', error);
      setUpdateInstalling(false);
    }
  }, []);

  const requestNotificationPermission = useCallback(async () => {
    if (!('Notification' in window)) return;

    try {
      const permission = await Notification.requestPermission();
      setNotificationPermission(permission);
      
      if (permission === 'granted') {
        new Notification('Atlantiplex Studio', {
          body: 'Notifications are now enabled!',
          icon: '/icons/icon-192x192.png',
          badge: '/icons/badge-72x72.png'
        });
      }
    } catch (error) {
      console.error('Notification permission error:', error);
    }
  }, []);

  const formatBytes = (bytes, decimals = 2) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
  };

  const NetworkStatus = () => (
    <div className={`network-status ${isOnline ? 'online' : 'offline'}`}>
      {isOnline ? (
        <>
          <Wifi size={16} />
          <span>Online</span>
        </>
      ) : (
        <>
          <WifiOff size={16} />
          <span>Offline - Limited functionality</span>
        </>
      )}
    </div>
  );

  const InstallPrompt = () => {
    if (installStatus === 'installed' || installStatus === 'not-available') return null;

    return (
      <div className="install-prompt">
        <div className="prompt-content">
          <div className="prompt-icon">
            <Download size={24} />
          </div>
          <div className="prompt-text">
            <h4>Install Atlantiplex Studio</h4>
            <p>Get the full desktop experience with offline support</p>
          </div>
          <div className="prompt-actions">
            {installPrompt && (
              <button onClick={handleInstall} className="btn-primary">
                Install
              </button>
            )}
            <button 
              onClick={() => setInstallStatus('dismissed')}
              className="btn-secondary"
            >
              Not now
            </button>
          </div>
        </div>
      </div>
    );
  };

  const UpdateBanner = () => {
    if (!updateAvailable) return null;

    return (
      <div className="update-banner">
        <div className="banner-content">
          <div className="banner-icon">
            <RefreshCw size={20} className={updateInstalling ? 'animate-spin' : ''} />
          </div>
          <div className="banner-text">
            <h4>Update Available</h4>
            <p>A new version of Atlantiplex Studio is ready</p>
          </div>
          <div className="banner-actions">
            <button 
              onClick={handleUpdate} 
              disabled={updateInstalling}
              className="btn-primary"
            >
              {updateInstalling ? 'Installing...' : 'Update Now'}
            </button>
            <button 
              onClick={() => setUpdateAvailable(false)}
              className="btn-secondary"
            >
              Later
            </button>
          </div>
        </div>
      </div>
    );
  };

  const NotificationSettings = () => (
    <div className="notification-settings">
      <div className="setting-header">
        <h4>Notifications</h4>
        <Bell size={16} />
      </div>
      
      <div className="setting-content">
        <p>Stay updated with stream alerts and important notifications</p>
        
        {notificationPermission === 'default' && (
          <button 
            onClick={requestNotificationPermission}
            className="btn-primary"
          >
            Enable Notifications
          </button>
        )}
        
        {notificationPermission === 'granted' && (
          <div className="permission-status">
            <Check size={16} />
            <span>Notifications enabled</span>
          </div>
        )}
        
        {notificationPermission === 'denied' && (
          <div className="permission-status denied">
            <AlertCircle size={16} />
            <span>Notifications blocked in browser settings</span>
          </div>
        )}
      </div>
    </div>
  );

  const StorageInfo = () => {
    if (!storageEstimate) return null;

    const usagePercentage = (storageEstimate.usage / storageEstimate.quota) * 100;

    return (
      <div className="storage-info">
        <div className="setting-header">
          <h4>Storage Usage</h4>
          <Info size={16} />
        </div>
        
        <div className="storage-visual">
          <div className="storage-bar">
            <div 
              className="storage-used" 
              style={{ width: `${usagePercentage}%` }}
            ></div>
          </div>
          
          <div className="storage-stats">
            <div className="stat">
              <span className="label">Used</span>
              <span className="value">{formatBytes(storageEstimate.usage)}</span>
            </div>
            <div className="stat">
              <span className="label">Available</span>
              <span className="value">{formatBytes(storageEstimate.quota - storageEstimate.usage)}</span>
            </div>
            <div className="stat">
              <span className="label">Total</span>
              <span className="value">{formatBytes(storageEstimate.quota)}</span>
            </div>
          </div>
        </div>
        
        <div className="storage-actions">
          <button className="btn-secondary">Clear Cache</button>
        </div>
      </div>
    );
  };

  const OfflineContent = () => {
    if (isOnline) return null;

    return (
      <div className="offline-notice">
        <div className="notice-content">
          <WifiOff size={48} />
          <h3>You're offline</h3>
          <p>Some features may be limited until you reconnect</p>
          
          <div className="available-features">
            <h4>Available Offline:</h4>
            <ul>
              <li>View previously loaded streams</li>
              <li>Access cached recordings</li>
              <li>Edit stream settings</li>
              <li>Prepare scheduled streams</li>
            </ul>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="pwa-features">
      <NetworkStatus />
      
      <InstallPrompt />
      <UpdateBanner />
      
      <div className="pwa-settings-panel">
        <h3>App Settings</h3>
        
        <NotificationSettings />
        <StorageInfo />
        
        <div className="app-info">
          <div className="setting-header">
            <h4>About</h4>
            <Info size={16} />
          </div>
          
          <div className="app-details">
            <div className="detail-item">
              <span className="label">Version</span>
              <span className="value">2.5.0</span>
            </div>
            <div className="detail-item">
              <span className="label">Build</span>
              <span className="value">20250208-1530</span>
            </div>
            <div className="detail-item">
              <span className="label">Environment</span>
              <span className="value">Production</span>
            </div>
          </div>
          
          <div className="app-actions">
            <button className="btn-secondary">
              <Settings size={16} />
              Advanced Settings
            </button>
            <button className="btn-secondary">
              <Home size={16} />
              Set as Homepage
            </button>
          </div>
        </div>
      </div>
      
      <OfflineContent />
    </div>
  );
};

export default PWAFeatures;