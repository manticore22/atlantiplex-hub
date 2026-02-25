import React, { useState, useEffect, useCallback } from 'react';
import { Upload, Cloud, Download, Trash2, Play, Pause, Circle } from 'lucide-react';

const S3RecordingManager = ({ userId, onUploadComplete, onError }) => {
  const [recordings, setRecordings] = useState([]);
  const [uploadProgress, setUploadProgress] = useState({});
  const [uploading, setUploading] = useState(false);
  const [storageUsed, setStorageUsed] = useState(0);
  const [storageLimit, setStorageLimit] = useState(0);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [uploadQueue, setUploadQueue] = useState([]);
  const [processingQueue, setProcessingQueue] = useState(false);

  useEffect(() => {
    fetchRecordings();
    fetchStorageInfo();
    
    // Set up periodic sync
    const interval = setInterval(() => {
      syncRecordings();
    }, 30000); // Sync every 30 seconds

    return () => clearInterval(interval);
  }, [userId]);

  const fetchRecordings = async () => {
    try {
      const response = await fetch(`/api/s3/recordings/${userId}`);
      const data = await response.json();
      setRecordings(data.recordings || []);
    } catch (error) {
      console.error('Failed to fetch recordings:', error);
      onError?.(error);
    }
  };

  const fetchStorageInfo = async () => {
    try {
      const response = await fetch(`/api/s3/storage/${userId}`);
      const data = await response.json();
      setStorageUsed(data.used || 0);
      setStorageLimit(data.limit || 0);
    } catch (error) {
      console.error('Failed to fetch storage info:', error);
    }
  };

  const handleFileSelect = (event) => {
    const files = Array.from(event.target.files);
    const validFiles = files.filter(file => {
      const isValidType = file.type.startsWith('video/') || file.type.startsWith('audio/');
      const isValidSize = file.size <= 5 * 1024 * 1024 * 1024; // 5GB limit
      return isValidType && isValidSize;
    });

    setSelectedFiles(prev => [...prev, ...validFiles]);
  };

  const addToUploadQueue = () => {
    if (selectedFiles.length === 0) return;

    const newQueueItems = selectedFiles.map(file => ({
      id: `${Date.now()}_${file.name}`,
      file,
      status: 'pending',
      progress: 0,
      url: null,
      metadata: {
        originalName: file.name,
        size: file.size,
        type: file.type,
        uploadedAt: new Date().toISOString(),
        userId: userId
      }
    }));

    setUploadQueue(prev => [...prev, ...newQueueItems]);
    setSelectedFiles([]);
    processUploadQueue();
  };

  const processUploadQueue = async () => {
    if (processingQueue || uploadQueue.length === 0) return;
    
    setProcessingQueue(true);
    const currentQueue = [...uploadQueue];
    
    for (const item of currentQueue) {
      await uploadFile(item);
    }
    
    setProcessingQueue(false);
  };

  const uploadFile = async (queueItem) => {
    const { id, file, metadata } = queueItem;
    
    try {
      // Update status to uploading
      setUploadQueue(prev => prev.map(item => 
        item.id === id ? { ...item, status: 'uploading' } : item
      ));
      
      // Get presigned URL from backend
      const presignedResponse = await fetch('/api/s3/presigned-url', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          fileName: file.name,
          fileType: file.type,
          userId: userId
        })
      });

      const { uploadUrl, fileUrl, fileId } = await presignedResponse.json();

      // Upload file to S3
      const formData = new FormData();
      
      const xhr = new XMLHttpRequest();
      
      return new Promise((resolve, reject) => {
        xhr.upload.addEventListener('progress', (event) => {
          if (event.lengthComputable) {
            const progress = Math.round((event.loaded / event.total) * 100);
            setUploadProgress(prev => ({ ...prev, [id]: progress }));
            setUploadQueue(prev => prev.map(item => 
              item.id === id ? { ...item, progress } : item
            ));
          }
        });

        xhr.addEventListener('load', async () => {
          if (xhr.status === 200) {
            try {
              // Save recording metadata to database
              const saveResponse = await fetch('/api/s3/recording', {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                  fileId,
                  userId,
                  url: fileUrl,
                  metadata: {
                    ...metadata,
                    s3Key: fileUrl.split('/').pop(),
                    uploadedAt: new Date().toISOString()
                  }
                })
              });

              const savedRecording = await saveResponse.json();

              // Update queue item status
              setUploadQueue(prev => prev.map(item => 
                item.id === id ? { 
                  ...item, 
                  status: 'completed', 
                  url: fileUrl,
                  progress: 100 
                } : item
              ));

              // Add to recordings list
              setRecordings(prev => [savedRecording, ...prev]);
              
              // Update storage info
              fetchStorageInfo();
              
              onUploadComplete?.(savedRecording);
              resolve();
            } catch (error) {
              console.error('Failed to save recording metadata:', error);
              reject(error);
            }
          } else {
            reject(new Error('Upload failed'));
          }
        });

        xhr.addEventListener('error', () => {
          reject(new Error('Upload error'));
        });

        xhr.open('PUT', uploadUrl);
        xhr.send(file);
      });
    } catch (error) {
      console.error('Upload failed:', error);
      
      // Update queue item status to failed
      setUploadQueue(prev => prev.map(item => 
        item.id === id ? { ...item, status: 'failed' } : item
      ));
      
      onError?.(error);
    }
  };

  const downloadRecording = async (recording) => {
    try {
      const response = await fetch(`/api/s3/download/${recording.id}`);
      const { downloadUrl } = await response.json();
      
      // Create download link
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = recording.metadata.originalName;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (error) {
      console.error('Download failed:', error);
      onError?.(error);
    }
  };

  const deleteRecording = async (recordingId) => {
    try {
      await fetch(`/api/s3/recording/${recordingId}`, {
        method: 'DELETE'
      });
      
      // Remove from recordings list
      setRecordings(prev => prev.filter(r => r.id !== recordingId));
      
      // Update storage info
      fetchStorageInfo();
    } catch (error) {
      console.error('Delete failed:', error);
      onError?.(error);
    }
  };

  const generatePreview = async (recording) => {
    try {
      const response = await fetch(`/api/s3/preview/${recording.id}`);
      const { previewUrl } = await response.json();
      
      return previewUrl;
    } catch (error) {
      console.error('Preview generation failed:', error);
      return null;
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDuration = (seconds) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    
    if (hours > 0) {
      return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
  };

  const storagePercentage = storageLimit > 0 ? (storageUsed / storageLimit) * 100 : 0;

  return (
    <div className="s3-recording-manager">
      <div className="storage-header">
        <h2>Cloud Recording Storage</h2>
        
        <div className="storage-info">
          <div className="storage-bar">
            <div 
              className="storage-used" 
              style={{ width: `${Math.min(storagePercentage, 100)}%` }}
            ></div>
          </div>
          <div className="storage-stats">
            <span>{formatFileSize(storageUsed)} used</span>
            <span>of {formatFileSize(storageLimit)}</span>
            <span className={`percentage ${storagePercentage > 90 ? 'warning' : ''}`}>
              {storagePercentage.toFixed(1)}%
            </span>
          </div>
        </div>
      </div>

      <div className="upload-section">
        <div className="file-upload">
          <input
            type="file"
            id="file-input"
            multiple
            accept="video/*,audio/*"
            onChange={handleFileSelect}
            style={{ display: 'none' }}
          />
          <label htmlFor="file-input" className="upload-btn">
            <Upload size={20} />
            Select Recordings
          </label>
        </div>

        {selectedFiles.length > 0 && (
          <div className="selected-files">
            <h4>Selected Files ({selectedFiles.length})</h4>
            <ul>
              {selectedFiles.map((file, index) => (
                <li key={index}>
                  <span>{file.name}</span>
                  <span>{formatFileSize(file.size)}</span>
                </li>
              ))}
            </ul>
            <button 
              onClick={addToUploadQueue}
              className="start-upload-btn"
              disabled={uploading}
            >
              <Cloud size={16} />
              Start Upload
            </button>
          </div>
        )}

        {uploadQueue.length > 0 && (
          <div className="upload-queue">
            <h4>Upload Queue</h4>
            {uploadQueue.map(item => (
              <div key={item.id} className={`queue-item ${item.status}`}>
                <div className="item-info">
                  <span>{item.file.name}</span>
                  <span>{formatFileSize(item.file.size)}</span>
                </div>
                <div className="item-progress">
                  {item.status === 'uploading' && (
                    <>
                      <div className="progress-bar">
                        <div 
                          className="progress-fill" 
                          style={{ width: `${item.progress}%` }}
                        ></div>
                      </div>
                      <span>{item.progress}%</span>
                    </>
                  )}
                  {item.status === 'completed' && (
                    <span className="status-icon">✅</span>
                  )}
                  {item.status === 'failed' && (
                    <span className="status-icon error">❌</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="recordings-section">
        <h3>Your Recordings ({recordings.length})</h3>
        
        <div className="recordings-grid">
          {recordings.map(recording => (
            <div key={recording.id} className="recording-card">
              <div className="recording-thumbnail">
                {recording.metadata.thumbnail ? (
                  <img src={recording.metadata.thumbnail} alt="Thumbnail" />
                ) : (
                  <div className="thumbnail-placeholder">
                    <Play size={24} />
                  </div>
                )}
              </div>
              
              <div className="recording-info">
                <h4>{recording.metadata.originalName}</h4>
                <div className="recording-meta">
                  <span>{formatFileSize(recording.metadata.size)}</span>
                  <span>{formatDuration(recording.metadata.duration || 0)}</span>
                  <span>{new Date(recording.metadata.uploadedAt).toLocaleDateString()}</span>
                </div>
              </div>
              
              <div className="recording-actions">
                <button 
                  onClick={() => downloadRecording(recording)}
                  className="action-btn download"
                  title="Download"
                >
                  <Download size={16} />
                </button>
                <button 
                  onClick={() => deleteRecording(recording.id)}
                  className="action-btn delete"
                  title="Delete"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            </div>
          ))}
        </div>

        {recordings.length === 0 && (
          <div className="empty-state">
            <Cloud size={48} />
            <h3>No recordings yet</h3>
            <p>Upload your first recording to get started</p>
          </div>
        )}
      </div>

      <div className="storage-settings">
        <h3>Storage Settings</h3>
        <div className="settings-grid">
          <div className="setting-item">
            <label>Auto-sync Recordings</label>
            <input type="checkbox" defaultChecked />
          </div>
          <div className="setting-item">
            <label>Backup Frequency</label>
            <select>
              <option>Real-time</option>
              <option>Daily</option>
              <option>Weekly</option>
            </select>
          </div>
          <div className="setting-item">
            <label>Compression</label>
            <select>
              <option>None</option>
              <option>Medium</option>
              <option>High</option>
            </select>
          </div>
        </div>
      </div>
    </div>
  );
};

export default S3RecordingManager;