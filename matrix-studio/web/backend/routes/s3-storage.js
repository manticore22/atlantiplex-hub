const express = require('express');
const multer = require('multer');
const AWS = require('aws-sdk');
const multerS3 = require('multer-s3');
const router = express.Router();
const { v4: uuidv4 } = require('uuid');

// Configure AWS S3
const s3 = new AWS.S3({
  accessKeyId: process.env.AWS_ACCESS_KEY_ID,
  secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
  region: process.env.AWS_REGION || 'us-east-1'
});

// Configure multer for S3 uploads
const upload = multer({
  storage: multerS3({
    s3: s3,
    bucket: process.env.S3_BUCKET_NAME,
    metadata: function (req, file, cb) {
      cb(null, { fieldName: file.fieldname });
    },
    key: function (req, file, cb) {
      const uniqueName = `${uuidv4()}-${Date.now()}-${file.originalname}`;
      cb(null, `recordings/${req.body.userId}/${uniqueName}`);
    }
  }),
  limits: {
    fileSize: 5 * 1024 * 1024 * 1024 // 5GB limit
  },
  fileFilter: function (req, file, cb) {
    const allowedTypes = ['video/', 'audio/'];
    if (allowedTypes.some(type => file.mimetype.startsWith(type))) {
      cb(null, true);
    } else {
      cb(new Error('Invalid file type. Only video and audio files are allowed.'));
    }
  }
});

// Get presigned URL for direct upload
router.post('/presigned-url', async (req, res) => {
  try {
    const { fileName, fileType, userId } = req.body;
    
    if (!fileName || !fileType || !userId) {
      return res.status(400).json({ error: 'Missing required fields' });
    }

    const fileId = uuidv4();
    const keyName = `recordings/${userId}/${fileId}-${fileName}`;

    const s3Params = {
      Bucket: process.env.S3_BUCKET_NAME,
      Key: keyName,
      Expires: 60, // URL expires in 60 seconds
      ContentType: fileType,
      ACL: 'private'
    };

    const uploadUrl = s3.getSignedUrl('putObject', s3Params);
    const fileUrl = `https://${process.env.S3_BUCKET_NAME}.s3.${process.env.AWS_REGION || 'us-east-1'}.amazonaws.com/${keyName}`;

    res.json({
      uploadUrl,
      fileUrl,
      fileId,
      key: keyName
    });
  } catch (error) {
    console.error('Presigned URL error:', error);
    res.status(500).json({ error: 'Failed to generate presigned URL' });
  }
});

// Save recording metadata to database
router.post('/recording', async (req, res) => {
  try {
    const { fileId, userId, url, metadata } = req.body;

    // Validate user storage limits
    const storageInfo = await getUserStorageInfo(userId);
    if (storageInfo.used + metadata.size > storageInfo.limit) {
      return res.status(413).json({ 
        error: 'Storage limit exceeded',
        used: storageInfo.used,
        limit: storageInfo.limit
      });
    }

    // Save to database
    const recordingData = {
      id: fileId,
      userId,
      url,
      metadata: {
        ...metadata,
        uploadedAt: new Date(),
        lastAccessed: new Date()
      },
      status: 'active'
    };

    const recording = await saveRecordingToDatabase(recordingData);

    // Update user storage usage
    await updateUserStorageUsage(userId, storageInfo.used + metadata.size);

    res.json(recording);
  } catch (error) {
    console.error('Save recording error:', error);
    res.status(500).json({ error: 'Failed to save recording' });
  }
});

// Get user recordings
router.get('/recordings/:userId', async (req, res) => {
  try {
    const { userId } = req.params;
    const { page = 1, limit = 20, sortBy = 'uploadedAt', sortOrder = 'desc' } = req.query;

    const recordings = await getUserRecordings(userId, {
      page: parseInt(page),
      limit: parseInt(limit),
      sortBy,
      sortOrder
    });

    res.json(recordings);
  } catch (error) {
    console.error('Get recordings error:', error);
    res.status(500).json({ error: 'Failed to fetch recordings' });
  }
});

// Download recording (presigned URL)
router.get('/download/:recordingId', async (req, res) => {
  try {
    const { recordingId } = req.params;
    
    const recording = await getRecordingById(recordingId);
    if (!recording) {
      return res.status(404).json({ error: 'Recording not found' });
    }

    // Generate presigned download URL
    const s3Params = {
      Bucket: process.env.S3_BUCKET_NAME,
      Key: recording.metadata.s3Key,
      Expires: 3600, // URL expires in 1 hour
      ResponseContentDisposition: `attachment; filename="${recording.metadata.originalName}"`
    };

    const downloadUrl = s3.getSignedUrl('getObject', s3Params);

    // Update last accessed
    await updateRecordingLastAccessed(recordingId);

    res.json({ downloadUrl });
  } catch (error) {
    console.error('Download error:', error);
    res.status(500).json({ error: 'Failed to generate download URL' });
  }
});

// Generate preview for recording
router.get('/preview/:recordingId', async (req, res) => {
  try {
    const { recordingId } = req.params;
    
    const recording = await getRecordingById(recordingId);
    if (!recording) {
      return res.status(404).json({ error: 'Recording not found' });
    }

    // Check if preview already exists
    if (recording.metadata.thumbnail) {
      return res.json({ previewUrl: recording.metadata.thumbnail });
    }

    // Generate thumbnail using AWS Lambda or local processing
    const thumbnailUrl = await generateVideoThumbnail(recording);

    // Update recording with thumbnail
    await updateRecordingThumbnail(recordingId, thumbnailUrl);

    res.json({ previewUrl: thumbnailUrl });
  } catch (error) {
    console.error('Preview generation error:', error);
    res.status(500).json({ error: 'Failed to generate preview' });
  }
});

// Delete recording
router.delete('/recording/:recordingId', async (req, res) => {
  try {
    const { recordingId } = req.params;
    
    const recording = await getRecordingById(recordingId);
    if (!recording) {
      return res.status(404).json({ error: 'Recording not found' });
    }

    // Delete from S3
    await s3.deleteObject({
      Bucket: process.env.S3_BUCKET_NAME,
      Key: recording.metadata.s3Key
    }).promise();

    // Delete from database
    await deleteRecordingFromDatabase(recordingId);

    // Update user storage usage
    const storageInfo = await getUserStorageInfo(recording.userId);
    await updateUserStorageUsage(recording.userId, storageInfo.used - recording.metadata.size);

    res.json({ success: true });
  } catch (error) {
    console.error('Delete recording error:', error);
    res.status(500).json({ error: 'Failed to delete recording' });
  }
});

// Get storage information for user
router.get('/storage/:userId', async (req, res) => {
  try {
    const { userId } = req.params;
    
    const storageInfo = await getUserStorageInfo(userId);
    
    res.json({
      used: storageInfo.used,
      limit: storageInfo.limit,
      available: storageInfo.limit - storageInfo.used,
      percentage: (storageInfo.used / storageInfo.limit) * 100
    });
  } catch (error) {
    console.error('Storage info error:', error);
    res.status(500).json({ error: 'Failed to get storage info' });
  }
});

// Upload file directly (alternative method)
router.post('/upload/:userId', upload.single('recording'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No file uploaded' });
    }

    const recordingData = {
      id: uuidv4(),
      userId: req.params.userId,
      url: req.file.location,
      metadata: {
        originalName: req.file.originalname,
        size: req.file.size,
        type: req.file.mimetype,
        uploadedAt: new Date(),
        s3Key: req.file.key
      }
    };

    const recording = await saveRecordingToDatabase(recordingData);

    res.json(recording);
  } catch (error) {
    console.error('Direct upload error:', error);
    res.status(500).json({ error: 'Failed to upload file' });
  }
});

// Batch operations
router.post('/batch-upload', async (req, res) => {
  try {
    const { userId, files } = req.body;
    
    const results = [];
    for (const fileData of files) {
      try {
        const result = await processFileUpload(userId, fileData);
        results.push({ success: true, file: fileData.name, result });
      } catch (error) {
        results.push({ success: false, file: fileData.name, error: error.message });
      }
    }

    res.json(results);
  } catch (error) {
    console.error('Batch upload error:', error);
    res.status(500).json({ error: 'Batch upload failed' });
  }
});

// Storage management
router.post('/cleanup', async (req, res) => {
  try {
    const { userId, olderThan = '30d' } = req.body;
    
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - parseInt(olderThan));

    const oldRecordings = await getOldRecordings(userId, cutoffDate);
    let deletedCount = 0;
    let freedSpace = 0;

    for (const recording of oldRecordings) {
      try {
        // Delete from S3
        await s3.deleteObject({
          Bucket: process.env.S3_BUCKET_NAME,
          Key: recording.metadata.s3Key
        }).promise();

        // Delete from database
        await deleteRecordingFromDatabase(recording.id);

        deletedCount++;
        freedSpace += recording.metadata.size;
      } catch (error) {
        console.error(`Failed to delete recording ${recording.id}:`, error);
      }
    }

    // Update user storage usage
    if (freedSpace > 0) {
      const storageInfo = await getUserStorageInfo(userId);
      await updateUserStorageUsage(userId, storageInfo.used - freedSpace);
    }

    res.json({
      deletedCount,
      freedSpace,
      message: `Deleted ${deletedCount} recordings, freed ${formatBytes(freedSpace)}`
    });
  } catch (error) {
    console.error('Cleanup error:', error);
    res.status(500).json({ error: 'Cleanup failed' });
  }
});

// Analytics and insights
router.get('/analytics/:userId', async (req, res) => {
  try {
    const { userId } = req.params;
    const { timeRange = '30d' } = req.query;
    
    const analytics = await getRecordingAnalytics(userId, timeRange);
    
    res.json(analytics);
  } catch (error) {
    console.error('Analytics error:', error);
    res.status(500).json({ error: 'Failed to load analytics' });
  }
});

// Helper functions

async function saveRecordingToDatabase(recordingData) {
  // Implement database save logic
  console.log('Saving recording to database:', recordingData);
  return recordingData; // Return saved recording
}

async function getRecordingById(recordingId) {
  // Implement database get logic
  console.log('Getting recording:', recordingId);
  return null; // Return actual recording
}

async function getUserRecordings(userId, options) {
  // Implement database query with pagination
  console.log('Getting recordings for user:', userId, options);
  return { recordings: [], total: 0 }; // Return actual recordings
}

async function getUserStorageInfo(userId) {
  // Implement storage info logic
  console.log('Getting storage info for user:', userId);
  return { used: 0, limit: 5 * 1024 * 1024 * 1024 }; // 5GB default limit
}

async function updateUserStorageUsage(userId, newUsage) {
  // Implement storage usage update
  console.log('Updating storage usage:', userId, newUsage);
}

async function updateRecordingLastAccessed(recordingId) {
  // Implement last accessed update
  console.log('Updating last accessed:', recordingId);
}

async function deleteRecordingFromDatabase(recordingId) {
  // Implement database delete
  console.log('Deleting recording from database:', recordingId);
}

async function generateVideoThumbnail(recording) {
  // Implement thumbnail generation (could use AWS Lambda or FFmpeg)
  console.log('Generating thumbnail for recording:', recording.id);
  return `https://example.com/thumbnails/${recording.id}.jpg`;
}

async function updateRecordingThumbnail(recordingId, thumbnailUrl) {
  // Implement thumbnail update
  console.log('Updating thumbnail:', recordingId, thumbnailUrl);
}

async function processFileUpload(userId, fileData) {
  // Process individual file in batch upload
  console.log('Processing file upload:', userId, fileData.name);
  return { id: uuidv4() };
}

async function getOldRecordings(userId, cutoffDate) {
  // Get recordings older than cutoff date
  console.log('Getting old recordings:', userId, cutoffDate);
  return [];
}

async function getRecordingAnalytics(userId, timeRange) {
  // Get recording analytics and insights
  console.log('Getting recording analytics:', userId, timeRange);
  return {
    totalRecordings: 0,
    totalSize: 0,
    averageSize: 0,
    uploadFrequency: {},
    storageGrowth: []
  };
}

function formatBytes(bytes) {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// S3 event handler (for processing uploads)
router.post('/webhook', async (req, res) => {
  try {
    const { Records } = req.body;
    
    for (const record of Records) {
      if (record.eventName === 'ObjectCreated:Put') {
        const bucket = record.s3.bucket.name;
        const key = record.s3.object.key;
        
        // Process uploaded file (generate thumbnail, extract metadata, etc.)
        await processUploadedFile(bucket, key);
      }
    }
    
    res.status(200).send('OK');
  } catch (error) {
    console.error('S3 webhook error:', error);
    res.status(500).send('Error processing webhook');
  }
});

async function processUploadedFile(bucket, key) {
  // Process uploaded file - generate thumbnail, extract metadata, etc.
  console.log('Processing uploaded file:', bucket, key);
}

module.exports = router;