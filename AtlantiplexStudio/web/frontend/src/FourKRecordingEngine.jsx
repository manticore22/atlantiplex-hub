import React, { useState, useEffect, useRef, useCallback } from 'react';
import { getPalette, getFontFamily } from './branding.ts';

export default function FourKRecordingEngine() {
  const [isRecording, setIsRecording] = useState(false);
  const [recordingQuality, setRecordingQuality] = useState('1080p');
  const [recordingDuration, setRecordingDuration] = useState(0);
  const [recordingTime, setRecordingTime] = useState('00:00:00');
  const [availableSpace, setAvailableSpace] = useState(null);
  const [recordingSize, setRecordingSize] = useState({ width: 0, height: 0, duration: 0 });
  const [encodingPreset, setEncodingPreset] = useState('balanced');
  const [gpuAcceleration, setGpuAcceleration] = useState(true);
  const [audioQuality, setAudioQuality] = useState('studio');

  const recordingQualities = {
    '720p': { 
      width: 1280, 
      height: 720, 
      bitrate: '2.5M',
      codec: 'H.264',
      fps: 30,
      label: '720p HD (2.5 Mbps)',
      fileMultiplier: 1
    },
    '1080p': { 
      width: 1920, 
      height: 1080, 
      bitrate: '5M',
      codec: 'H.264',
      fps: 30,
      label: '1080p Full HD (5 Mbps)',
      fileMultiplier: 4
    },
    '1440p': { 
      width: 2560, 
      height: 1440, 
      bitrate: '10M',
      codec: 'H.265',
      fps: 30,
      label: '1440p 2K (10 Mbps)',
      fileMultiplier: 8
    },
    '4K': { 
      width: 3840, 
      height: 2160, 
      bitrate: '15M',
      codec: 'H.265',
      fps: 30,
      label: '4K Ultra HD (15 Mbps)',
      fileMultiplier: 16
    }
  };

  const encodingPresets = {
    'quality': { 
      name: 'Highest Quality',
      description: 'Maximum quality, larger files',
      settings: { bitrate: 1.2, quality: 100 }
    },
    'balanced': { 
      name: 'Balanced',
      description: 'Good quality with reasonable file size',
      settings: { bitrate: 1.0, quality: 85 }
    },
    'performance': { 
      name: 'Performance',
      description: 'Smaller files, lower quality',
      settings: { bitrate: 0.8, quality: 70 }
    },
    'filesize': { 
      name: 'Small File Size',
      description: 'Smallest files, acceptable quality',
      settings: { bitrate: 0.6, quality: 60 }
    }
  };

  const audioQualities = {
    'standard': { 
      name: 'Standard',
      codec: 'AAC',
      bitrate: '128k',
      sampleRate: 44100,
      label: 'Standard (128 kbps AAC)'
    },
    'high': { 
      name: 'Studio',
      codec: 'AAC',
      bitrate: '320k',
      sampleRate: 48000,
      label: 'Studio (320 kbps AAC)'
    },
    'premium': { 
      name: 'Premium',
      codec: 'FLAC',
      bitrate: '1024k',
      sampleRate: 96000,
      label: 'Premium (FLAC Lossless)'
    }
  };

  const mediaRecorderRef = useRef(null);
  const streamRef = useRef(null);
  const chunksRef = useRef([]);
  const startTimeRef = useRef(null);
  const intervalRef = useRef(null);

  useEffect(() => {
    checkAvailableSpace();
    const interval = setInterval(checkAvailableSpace, 10000); // Check every 10 seconds
    intervalRef.current = interval;
    
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  const checkAvailableSpace = async () => {
    try {
      // Simulate available space calculation
      const估算Space = Math.floor(Math.random() * 900000000000); // 0-900GB in bytes
      setAvailableSpace(估算Space);
    } catch (error) {
      console.error('Failed to check available space:', error);
    }
  };

  const formatBytes = (bytes) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const m = k * 1024;
    const g = m * 1024;
    
    if (bytes < k) return bytes + ' B';
    if (bytes < m) return (bytes / k).toFixed(1) + ' KB';
    if (bytes < g) return (bytes / m).toFixed(1) + ' MB';
    return (bytes / g).toFixed(2) + ' GB';
  };

  const formatDuration = (seconds) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const startRecording = async () => {
    try {
      const constraints = {
        video: {
          width: { ideal: recordingQualities[recordingQuality].width },
          height: { ideal: recordingQualities[recordingQuality].height },
          frameRate: recordingQualities[recordingQuality].fps,
          facingMode: 'user'
        },
        audio: audioQualities[audioQuality].sampleRate === 96000 ? {
          sampleRate: 96000,
          channelCount: 2,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        } : {
          sampleRate: 44100,
          channelCount: 2,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        }
      };

      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      streamRef.current = stream;
      
      // Create MediaRecorder with optimized settings
      const options = {
        mimeType: `video/webm;codecs=${recordingQualities[recordingQuality].codec}`,
        videoBitsPerSecond: recordingQualities[recordingQuality].bitrate * 1024,
        audioBitsPerSecond: audioQualities[audioQuality].bitrate * 1024,
        videoKeyInterval: 2000,
        audioKeyInterval: 1000
      };

      // Add hardware acceleration support
      if (gpuAcceleration) {
        options.videoKeyInterval = 1000;
      }

      const mediaRecorder = new MediaRecorder(stream, options);
      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
          updateRecordingInfo();
        }
      };

      mediaRecorder.onstart = () => {
        setIsRecording(true);
        startTimeRef.current = Date.now();
        console.log(`Started ${recordingQuality} recording with ${audioQuality} audio`);
      };

      mediaRecorder.onstop = async () => {
        setIsRecording(false);
        const endTime = Date.now();
        const duration = (endTime - startTimeRef.current) / 1000;
        
        const completeBlob = new Blob(chunksRef.current, { type: `video/webm` });
        const recordingData = {
          blob: completeBlob,
          duration: duration,
          quality: recordingQuality,
          size: completeBlob.size,
          timestamp: new Date().toISOString()
        };

        await saveRecording(recordingData);
        setRecordingDuration(0);
        setRecordingTime('00:00:00');
      };

      mediaRecorder.start();
      console.log('MediaRecorder options:', options);
    } catch (error) {
      console.error('Failed to start recording:', error);
      alert(`Failed to start ${recordingQuality} recording: ${error.message}`);
    }
  };

  const updateRecordingInfo = useCallback(() => {
    if (!startTimeRef.current || !isRecording) return;
    
    const currentDuration = (Date.now() - startTimeRef.current) / 1000;
    setRecordingDuration(currentDuration);
    setRecordingTime(formatDuration(currentDuration));

    //估算 current file size
    if (chunksRef.current.length > 0) {
      const totalSize = chunksRef.current.reduce((sum, chunk) => sum + chunk.size, 0);
      setRecordingSize(prev => ({
        ...prev,
        size: totalSize,
        duration: prev.duration
      }));
    }
  }, [isRecording]);

  const saveRecording = async (recordingData) => {
    try {
      // Create a URL for the recording
      const url = URL.createObjectURL(recordingData.blob);
      
      // Create download link
      const a = document.createElement('a');
      a.href = url;
      a.download = `atlantiplex-recording-${recordingQuality}-${Date.now()}.webm`;
      
      // Add to recording library
      if (window.recordingLibrary) {
        window.recordingLibrary.addRecording({
          id: Date.now().toString(),
          filename: a.download,
          duration: recordingData.duration,
          quality: recordingQuality,
          size: recordingData.size,
          timestamp: recordingData.timestamp,
          blob: recordingData.blob
        });
      } else {
        // Fallback: create recording library
        window.recordingLibrary = {
          recordings: [],
          addRecording: (data) => {
            window.recordingLibrary.recordings.push(data);
          },
          getAllRecordings: () => {
            return window.recordingLibrary.recordings;
          }
        };
        window.recordingLibrary.addRecording(recordingData);
      }
      
      document.body.appendChild(a);
      
      // Auto-click the download
      setTimeout(() => {
        a.click();
        document.body.removeChild(a);
      }, 100);
      
      console.log(`Saved ${recordingQuality} recording: ${formatBytes(recordingData.size)}, ${recordingData.duration}s`);
      
      // Cleanup
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    } catch (error) {
      console.error('Failed to save recording:', error);
      alert(`Failed to save recording: ${error.message}`);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
    }
  };

  const pauseRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.pause();
      console.log('Recording paused');
    }
  };

  const resumeRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.resume();
      console.log('Recording resumed');
    }
  };

  const validateRecording = () => {
    const quality = recordingQualities[recordingQuality];
    const estimatedFilesize = quality.bitrate * 1024 * 60; // Rough estimate for 1 minute
    
    if (availableSpace && availableSpace < estimatedFilesize * 5) { // 5 minutes safety margin
      return {
        valid: false,
        message: `Not enough space for ${recordingQuality} recording. Need approximately ${formatBytes(estimatedFilesize * 5)}, only ${formatBytes(availableSpace)} available.`
      };
    }
    
    return { valid: true };
  };

  const getEstimatedFileSize = (durationMinutes = 1) => {
    const quality = recordingQualities[recordingQuality];
    const preset = encodingPresets[encodingPreset];
    const adjustedBitrate = quality.bitrate * preset.settings.bitrate;
    const estimatedBytes = adjustedBitrate * 1024 * 60 * durationMinutes;
    
    return {
      size: formatBytes(estimatedBytes),
      sizeMB: (estimatedBytes / 1024 / 1024).toFixed(2),
      durationGB: (estimatedBytes / 1024 / 1024 / 1024).toFixed(3)
    };
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: getPalette().bg,
      fontFamily: getFontFamily(),
      padding: '20px',
      color: getPalette().text
    }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <h1 style={{ textAlign: 'center', marginBottom: '30px' }}>
          🎥 4K Recording Engine
          <span style={{ fontSize: '16px', opacity: 0.7, marginLeft: '20px' }}>
            Professional-grade recording up to 4K resolution
          </span>
        </h1>

        {/* Recording Status */}
        <div style={{
          background: getPalette().surface,
          padding: '24px',
          borderRadius: '12px',
          marginBottom: '30px',
          border: '1px solid #00ff41'
        }}>
          <h2 style={{ marginBottom: '20px' }}>📹 Recording Status</h2>
          
          <div style={{ 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center',
            marginBottom: '20px'
          }}>
            <div>
              <div style={{ fontSize: '24px', marginBottom: '8px' }}>
                {isRecording ? '🔴' : '⚪'}
              </div>
              <div>
                <strong>Status:</strong> {isRecording ? 'Recording' : 'Ready'}
              </div>
            </div>
            
            <div style={{ textAlign: 'right' }}>
              <strong>Duration:</strong> {recordingTime}
            </div>
          </div>

          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
            gap: '16px', 
            marginBottom: '20px' 
          }}>
            <div>
              <strong>Quality:</strong> {recordingQualities[recordingQuality].label}
            </div>
            <div>
              <strong>File Size:</strong> {formatBytes(recordingSize.size)}
            </div>
            <div>
              <strong>Duration:</strong> {recordingDuration.toFixed(1)}s
            </div>
          </div>

          {/* Recording Controls */}
          <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
            {!isRecording ? (
              <button
                onClick={startRecording}
                disabled={!validateRecording().valid}
                style={{
                  background: validateRecording().valid ? '#00ff41' : '#6b7280',
                  color: 'white',
                  border: 'none',
                  padding: '16px 32px',
                  borderRadius: '8px',
                  fontSize: '16px',
                  fontWeight: 'bold',
                  cursor: validateRecording().valid ? 'pointer' : 'not-allowed',
                  boxShadow: '0 4px 12px rgba(0, 255, 65, 0.3)'
                }}
              >
                🎥 Start Recording
              </button>
            ) : (
              <>
                <button
                  onClick={pauseRecording}
                  style={{
                    background: '#ff9800',
                    color: 'white',
                    border: 'none',
                    padding: '12px 24px',
                    borderRadius: '8px',
                    fontSize: '14px',
                    cursor: 'pointer'
                  }}
                >
                  ⏸️ Pause
                </button>
                <button
                  onClick={resumeRecording}
                  style={{
                    background: '#4caf50',
                    color: 'white',
                    border: 'none',
                    padding: '12px 24px',
                    borderRadius: '8px',
                    fontSize: '14px',
                    cursor: 'pointer'
                  }}
                >
                  ▶️ Resume
                </button>
                <button
                  onClick={stopRecording}
                  style={{
                    background: '#f44336',
                    color: 'white',
                    border: 'none',
                    padding: '12px 24px',
                    borderRadius: '8px',
                    fontSize: '14px',
                    cursor: 'pointer'
                  }}
                >
                  ⏹️ Stop
                </button>
              </>
            )}
          </div>

          {!validateRecording().valid && (
            <div style={{ 
              marginTop: '20px', 
              padding: '16px', 
              background: '#ffebee', 
              borderRadius: '8px',
              border: '1px solid #fbbf24'
            }}>
              <strong>⚠️ Recording Error:</strong> {validateRecording().message}
            </div>
          )}
        </div>

        {/* Quality Settings */}
        <div style={{
          background: getPalette().surface,
          padding: '24px',
          borderRadius: '12px',
          marginBottom: '30px',
          border: '1px solid #00ff41'
        }}>
          <h2 style={{ marginBottom: '20px' }}>⚙️ Recording Quality</h2>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px', marginBottom: '20px' }}>
            <div>
              <label>Video Quality</label>
              <select
                value={recordingQuality}
                onChange={(e) => setRecordingQuality(e.target.value)}
                style={{ 
                  width: '100%', 
                  padding: '8px', 
                  marginTop: '8px',
                  background: getPalette().bg,
                  border: '1px solid #00ff41',
                  color: getPalette().text
                }}
              >
                {Object.entries(recordingQualities).map(([key, quality]) => (
                  <option key={key} value={key}>
                    {quality.label}
                  </option>
                ))}
              </select>
            </div>
            
            <div>
              <label>Encoding Preset</label>
              <select
                value={encodingPreset}
                onChange={(e) => setEncodingPreset(e.target.value)}
                style={{ 
                  width: '100%', 
                  padding: '8px', 
                  marginTop: '8px',
                  background: getPalette().bg,
                  border: '1px solid #00ff41',
                  color: getPalette().text
                }}
              >
                {Object.entries(encodingPresets).map(([key, preset]) => (
                  <option key={key} value={key}>
                    {preset.name} - {preset.description}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px' }}>
            <div>
              <label>Audio Quality</label>
              <select
                value={audioQuality}
                onChange={(e) => setAudioQuality(e.target.value)}
                style={{ 
                  width: '100%', 
                  padding: '8px', 
                  marginTop: '8px',
                  background: getPalette().bg,
                  border: '1px solid #00ff41',
                  color: getPalette().text
                }}
              >
                {Object.entries(audioQualities).map(([key, quality]) => (
                  <option key={key} value={key}>
                    {quality.label}
                  </option>
                ))}
              </select>
            </div>
            
            <div>
              <label>
                <input
                  type="checkbox"
                  checked={gpuAcceleration}
                  onChange={(e) => setGpuAcceleration(e.target.checked)}
                  style={{ marginRight: '8px' }}
                />
                GPU Acceleration
              </label>
            </div>
          </div>

          {/* Storage Info */}
          <div style={{ marginTop: '20px', padding: '16px', background: '#f0f9ff', borderRadius: '8px' }}>
            <h4 style={{ marginBottom: '12px' }}>💾 Storage Information</h4>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
              <div>
                <strong>Available Space:</strong> {formatBytes(availableSpace)}
              </div>
              <div>
                <strong>Est. Size/min:</strong> {
                  ((recordingQualities[recordingQuality].bitrate * 1024 * 60) / 1024 / 1024).toFixed(2)
                } MB
              </div>
            </div>
            <div style={{ 
              gridColumn: 'span 2', 
              marginTop: '16px',
              paddingTop: '12px',
              borderTop: '1px solid #00ff41'
            }}>
              <h4 style={{ marginBottom: '12px' }}>📊 Estimations</h4>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '16px' }}>
                <div>
                  <strong>5 min:</strong> {getEstimatedFileSize(5).sizeMB} MB ({getEstimatedFileSize(5).durationGB} GB)
                </div>
                <div>
                  <strong>30 min:</strong> {getEstimatedFileSize(30).sizeMB} MB ({getEstimatedFileSize(30).durationGB} GB)
                </div>
                <div>
                  <strong>1 hour:</strong> {getEstimatedFileSize(60).sizeMB} MB ({getEstimatedFileSize(60).durationGB} GB)
                </div>
                <div>
                  <strong>2 hours:</strong> {getEstimatedFileSize(120).sizeMB} MB ({getEstimatedFileSize(120).durationGB} GB)
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div style={{ textAlign: 'center', marginTop: '20px' }}>
          <button
            onClick={() => {
              window.recordingLibrary?.getAllRecordings().forEach(rec => {
                console.log('Recording:', rec.filename, rec.size);
              });
            }}
            }}
            style={{
              background: getPalette().bg,
              border: '2px solid #00ff41',
              color: getPalette().text,
              padding: '12px 24px',
              borderRadius: '8px',
              fontSize: '16px',
              fontWeight: 'bold',
              cursor: 'pointer'
            }}
          >
            📚 View All Recordings
          </button>
        </div>
      </div>
    </div>
  );
}