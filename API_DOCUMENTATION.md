# 📚 Atlantiplex Studio API Documentation

## 🚀 Overview

Welcome to the comprehensive API documentation for Atlantiplex Studio. This document covers all available endpoints for payment processing, authentication, analytics, storage, and studio management.

---

## 🔐 Authentication

### Base URL
```
https://api.atlantiplex.com/v1
```

### Authentication Headers
```
Authorization: Bearer <your_jwt_token>
Content-Type: application/json
```

---

## 💳 Payment APIs

### Stripe Integration

#### Create Payment Intent
```http
POST /api/create-payment-intent
```

**Request Body:**
```json
{
  "amount": 1999,
  "currency": "USD",
  "userId": "user123",
  "metadata": {
    "plan": "pro",
    "duration": "monthly"
  }
}
```

**Response:**
```json
{
  "clientSecret": "pi_12345_secret_abcdef",
  "paymentIntentId": "pi_12345"
}
```

#### Stripe Configuration
```http
GET /api/stripe-config
```

**Response:**
```json
{
  "publishableKey": "pk_test_1234567890abcdef",
  "country": "US",
  "currency": "USD",
  "supportedPaymentMethods": ["card", "apple_pay", "google_pay"]
}
```

### PayPal Integration

#### Create PayPal Order
```http
POST /api/paypal/create-order
```

**Request Body:**
```json
{
  "amount": 1999,
  "currency": "USD",
  "description": "Pro Plan Monthly Subscription"
}
```

**Response:**
```json
{
  "orderID": "PAY-1234567890",
  "status": "CREATED"
}
```

#### Capture PayPal Payment
```http
POST /api/paypal/capture-order
```

**Request Body:**
```json
{
  "orderID": "PAY-1234567890"
}
```

**Response:**
```json
{
  "captured": true,
  "transactionId": "TRANSACTION_ID",
  "amount": "19.99",
  "currency": "USD",
  "status": "COMPLETED"
}
```

#### PayPal Webhook
```http
POST /api/paypal/webhook
```

**Webhook Events:**
- `PAYMENT.CAPTURE.COMPLETED`
- `PAYMENT.CAPTURE.DENIED`
- `PAYMENT.CAPTURE.REFUNDED`

---

## 🔒 Two-Factor Authentication (2FA)

### Setup 2FA with Authenticator App
```http
POST /api/auth/2fa/setup
```

**Request Body:**
```json
{
  "userId": "user123"
}
```

**Response:**
```json
{
  "secret": "JBSWY3DPEHPK3PXP",
  "qrCodeUrl": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
  "backupCodes": ["12345678", "87654321", "..."],
  "manualEntryKey": "JBSWY3DPEHPK3PXP"
}
```

### Verify Authenticator Code
```http
POST /api/auth/2fa/verify
```

**Request Body:**
```json
{
  "userId": "user123",
  "token": "123456"
}
```

**Response:**
```json
{
  "verified": true,
  "message": "2FA enabled successfully"
}
```

### Send SMS OTP
```http
POST /api/auth/2fa/send-otp
```

**Request Body:**
```json
{
  "userId": "user123",
  "phoneNumber": "+1234567890"
}
```

**Response:**
```json
{
  "success": true,
  "message": "OTP sent successfully"
}
```

### Verify SMS OTP
```http
POST /api/auth/2fa/verify-otp
```

**Request Body:**
```json
{
  "userId": "user123",
  "code": "123456"
}
```

**Response:**
```json
{
  "verified": true,
  "message": "Phone number verified successfully"
}
```

### Login 2FA Verification
```http
POST /api/auth/2fa/login-verify
```

**Request Body:**
```json
{
  "userId": "user123",
  "token": "123456",
  "backupCode": "12345678"
}
```

**Response:**
```json
{
  "verified": true,
  "method": "authenticator",
  "message": "2FA verification successful"
}
```

---

## 📊 Analytics APIs

### Dashboard Analytics
```http
GET /api/analytics/dashboard?timeRange=7d
```

**Query Parameters:**
- `timeRange`: `24h`, `7d`, `30d`, `90d`, `1y`

**Response:**
```json
{
  "overview": {
    "totalUsers": 1250,
    "activeStreams": 45,
    "revenue": 15000,
    "engagementRate": 78.5,
    "userGrowth": 12.3,
    "streamGrowth": 8.7,
    "revenueGrowth": 15.2
  },
  "userEngagement": [
    {
      "date": "2024-02-01",
      "newUsers": 45,
      "activeUsers": 320,
      "pageViews": 1250,
      "interactions": 890
    }
  ],
  "streamingMetrics": {
    "totalStreams": 1250,
    "averageDuration": 45,
    "peakConcurrent": 850,
    "platformDistribution": [
      {"platform": "youtube", "streams": 450},
      {"platform": "facebook", "streams": 380}
    ]
  }
}
```

### Real-time Metrics
```http
GET /api/analytics/realtime
```

**Response:**
```json
{
  "onlineUsers": 45,
  "activeStreams": 12,
  "serverLoad": 65,
  "apiRequests": 1250,
  "recentActivity": [
    {
      "timestamp": "2024-02-01T12:30:00Z",
      "type": "stream_start",
      "user": "user123",
      "action": "Started streaming to YouTube"
    }
  ]
}
```

### Track Custom Events
```http
POST /api/analytics/track
```

**Request Body:**
```json
{
  "userId": "user123",
  "event": "feature_used",
  "properties": {
    "feature": "ai_clips",
    "duration": 45,
    "success": true
  }
}
```

### Export Analytics Data
```http
GET /api/analytics/export?format=csv&timeRange=30d&type=dashboard
```

**Query Parameters:**
- `format`: `csv`, `pdf`
- `timeRange`: `24h`, `7d`, `30d`, `90d`, `1y`
- `type`: `dashboard`, `users`, `revenue`

---

## ☁️ AWS S3 Storage APIs

### Get Presigned Upload URL
```http
POST /api/s3/presigned-url
```

**Request Body:**
```json
{
  "fileName": "recording-2024-02-01.mp4",
  "fileType": "video/mp4",
  "userId": "user123"
}
```

**Response:**
```json
{
  "uploadUrl": "https://s3.amazonaws.com/bucket/presigned-url",
  "fileUrl": "https://bucket.s3.region.amazonaws.com/path",
  "fileId": "rec_123456789",
  "key": "recordings/user123/rec_123456789-filename.mp4"
}
```

### Save Recording Metadata
```http
POST /api/s3/recording
```

**Request Body:**
```json
{
  "fileId": "rec_123456789",
  "userId": "user123",
  "url": "https://bucket.s3.region.amazonaws.com/path",
  "metadata": {
    "originalName": "recording-2024-02-01.mp4",
    "size": 1048576000,
    "type": "video/mp4",
    "duration": 3600,
    "s3Key": "recordings/user123/rec_123456789-filename.mp4"
  }
}
```

### Get User Recordings
```http
GET /api/s3/recordings/{userId}?page=1&limit=20&sortBy=uploadedAt&sortOrder=desc
```

**Response:**
```json
{
  "recordings": [
    {
      "id": "rec_123456789",
      "userId": "user123",
      "url": "https://bucket.s3.region.amazonaws.com/path",
      "metadata": {
        "originalName": "recording-2024-02-01.mp4",
        "size": 1048576000,
        "type": "video/mp4",
        "duration": 3600,
        "uploadedAt": "2024-02-01T12:00:00Z",
        "thumbnail": "https://example.com/thumb.jpg"
      }
    }
  ],
  "total": 25,
  "page": 1,
  "totalPages": 2
}
```

### Download Recording
```http
GET /api/s3/download/{recordingId}
```

**Response:**
```json
{
  "downloadUrl": "https://s3.amazonaws.com/bucket/presigned-download-url"
}
```

### Generate Recording Preview
```http
GET /api/s3/preview/{recordingId}
```

**Response:**
```json
{
  "previewUrl": "https://example.com/previews/rec_123456789.jpg"
}
```

### Delete Recording
```http
DELETE /api/s3/recording/{recordingId}
```

**Response:**
```json
{
  "success": true
}
```

### Get Storage Information
```http
GET /api/s3/storage/{userId}
```

**Response:**
```json
{
  "used": 2147483648,
  "limit": 5368709120,
  "available": 3221225472,
  "percentage": 40.0
}
```

---

## 🎥 Studio Management APIs

### Start Multistream
```http
POST /api/multistream/start
```

**Request Body:**
```json
{
  "userId": "user123",
  "platforms": ["youtube", "facebook", "linkedin"],
  "title": "My Live Stream",
  "description": "Join me for an amazing stream!",
  "settings": {
    "quality": "1080p",
    "bitrate": 5000,
    "framerate": 30
  }
}
```

**Response:**
```json
{
  "streamId": "stream_123456789",
  "platforms": {
    "youtube": {
      "streamKey": "youtube_key_123",
      "rtmpUrl": "rtmp://a.rtmp.youtube.com/live2",
      "status": "active"
    },
    "facebook": {
      "streamKey": "fb_key_456",
      "rtmpUrl": "rtmp://live-api-s.facebook.com/rtmp",
      "status": "active"
    }
  },
  "webRTCUrl": "wss://webrtc.atlantiplex.com/stream/stream_123456789"
}
```

### Stop Multistream
```http
POST /api/multistream/stop/{streamId}
```

**Response:**
```json
{
  "success": true,
  "stoppedAt": "2024-02-01T12:30:00Z"
}
```

### Invite Guests
```http
POST /api/stream/{streamId}/invite-guest
```

**Request Body:**
```json
{
  "emails": ["guest1@example.com", "guest2@example.com"],
  "role": "participant",
  "permissions": ["video", "audio", "screen_share"]
}
```

**Response:**
```json
{
  "invitations": [
    {
      "id": "inv_123456789",
      "email": "guest1@example.com",
      "inviteLink": "https://atlantiplex.com/join/inv_123456789",
      "expiresAt": "2024-02-02T12:00:00Z"
    }
  ]
}
```

### Get Stream Analytics
```http
GET /api/stream/{streamId}/analytics
```

**Response:**
```json
{
  "streamId": "stream_123456789",
  "startTime": "2024-02-01T12:00:00Z",
  "duration": 3600,
  "peakViewers": 1250,
  "totalViews": 5000,
  "platformStats": {
    "youtube": {
      "peakConcurrent": 850,
      "totalViews": 3200,
      "engagementRate": 78.5
    },
    "facebook": {
      "peakConcurrent": 400,
      "totalViews": 1800,
      "engagementRate": 65.2
    }
  }
}
```

---

## 🔧 User Management APIs

### User Registration
```http
POST /api/auth/register
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123",
  "firstName": "John",
  "lastName": "Doe"
}
```

**Response:**
```json
{
  "success": true,
  "userId": "user_123456789",
  "email": "user@example.com",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### User Login
```http
POST /api/auth/login
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

**Response:**
```json
{
  "success": true,
  "userId": "user_123456789",
  "email": "user@example.com",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "requires2FA": false
}
```

### Get User Profile
```http
GET /api/user/profile
```

**Response:**
```json
{
  "id": "user_123456789",
  "email": "user@example.com",
  "firstName": "John",
  "lastName": "Doe",
  "subscription": {
    "plan": "pro",
    "status": "active",
    "expiresAt": "2024-03-01T12:00:00Z"
  },
  "preferences": {
    "theme": "dark",
    "notifications": true,
    "defaultQuality": "1080p"
  }
}
```

### Update User Profile
```http
PUT /api/user/profile
```

**Request Body:**
```json
{
  "firstName": "John",
  "lastName": "Smith",
  "preferences": {
    "theme": "light",
    "notifications": false
  }
}
```

---

## 🎨 Studio Features APIs

### AI Clips Generation
```http
POST /api/ai/clips/generate
```

**Request Body:**
```json
{
  "recordingId": "rec_123456789",
  "duration": 30,
  "platforms": ["tiktok", "instagram", "youtube_shorts"],
  "options": {
    "highlightType": "peak_engagement",
    "verticalFormat": true,
    "captions": true,
    "music": "trending"
  }
}
```

**Response:**
```json
{
  "clips": [
    {
      "id": "clip_123456789",
      "url": "https://example.com/clips/clip_123456789.mp4",
      "duration": 30,
      "platform": "tiktok",
      "timestamp": 1200,
      "thumbnail": "https://example.com/thumbnails/clip_123456789.jpg"
    }
  ],
  "processingTime": 45
}
```

### Camera Effects
```http
POST /api/studio/camera/effects
```

**Request Body:**
```json
{
  "streamId": "stream_123456789",
  "effect": {
    "type": "shape",
    "shape": "circle",
    "size": "medium",
    "borderColor": "#00ff41",
    "animation": "pulse"
  }
}
```

**Response:**
```json
{
  "success": true,
  "effectId": "effect_123456789",
  "appliedAt": "2024-02-01T12:15:00Z"
}
```

### Recording Management
```http
POST /api/recording/start
```

**Request Body:**
```json
{
  "streamId": "stream_123456789",
  "quality": "4K",
  "format": "mp4",
  "settings": {
    "bitrate": 15000,
    "framerate": 60,
    "codec": "H.265"
  }
}
```

**Response:**
```json
{
  "recordingId": "rec_123456789",
  "status": "recording",
  "startTime": "2024-02-01T12:00:00Z"
}
```

---

## 🚨 Error Handling

### Standard Error Response Format
```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "The request is invalid",
    "details": "Missing required parameter: userId",
    "timestamp": "2024-02-01T12:00:00Z",
    "requestId": "req_123456789"
  }
}
```

### Common Error Codes
- `INVALID_REQUEST` - Bad request parameters
- `UNAUTHORIZED` - Authentication required
- `FORBIDDEN` - Insufficient permissions
- `NOT_FOUND` - Resource not found
- `RATE_LIMIT_EXCEEDED` - Too many requests
- `INTERNAL_SERVER_ERROR` - Server error
- `PAYMENT_REQUIRED` - Subscription required
- `STORAGE_EXCEEDED` - Storage limit exceeded

---

## 📝 Rate Limiting

### Rate Limits by Endpoint
- Authentication: 5 requests per minute
- Payment: 10 requests per minute
- Analytics: 100 requests per minute
- Storage: 50 requests per minute
- Studio: 200 requests per minute

### Rate Limit Headers
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1643673600
```

---

## 🔧 SDK Examples

### JavaScript/TypeScript
```typescript
import { AtlantiplexSDK } from '@atlantiplex/sdk';

const sdk = new AtlantiplexSDK({
  apiKey: 'your_api_key',
  baseURL: 'https://api.atlantiplex.com/v1'
});

// Start a stream
const stream = await sdk.streams.start({
  platforms: ['youtube', 'facebook'],
  title: 'My Awesome Stream'
});

// Upload recording
const upload = await sdk.storage.upload({
  file: fileObject,
  userId: 'user123'
});

// Get analytics
const analytics = await sdk.analytics.dashboard({
  timeRange: '7d'
});
```

### Python
```python
from atlantiplex_sdk import AtlantiplexSDK

sdk = AtlantiplexSDK(
    api_key='your_api_key',
    base_url='https://api.atlantiplex.com/v1'
)

# Start a stream
stream = sdk.streams.start(
    platforms=['youtube', 'facebook'],
    title='My Awesome Stream'
)

# Get analytics
analytics = sdk.analytics.dashboard(time_range='7d')
```

---

## 🔄 Webhooks

### Configure Webhooks
```http
POST /api/webhooks/configure
```

**Request Body:**
```json
{
  "url": "https://your-app.com/webhook",
  "events": [
    "stream.started",
    "stream.ended",
    "payment.completed",
    "user.signed_up"
  ],
  "secret": "webhook_secret_key"
}
```

### Webhook Event Types
- `stream.started` - Stream began
- `stream.ended` - Stream completed
- `payment.completed` - Payment successful
- `payment.failed` - Payment failed
- `user.signed_up` - New user registration
- `user.cancelled` - Subscription cancelled

### Webhook Signature Verification
```javascript
const crypto = require('crypto');

function verifyWebhook(payload, signature, secret) {
  const expectedSignature = crypto
    .createHmac('sha256', secret)
    .update(payload)
    .digest('hex');
  
  return signature === expectedSignature;
}
```

---

## 🌍 Regional Endpoints

### Available Regions
- `us-east-1` - US East (N. Virginia)
- `us-west-2` - US West (Oregon)
- `eu-west-1` - EU (Ireland)
- `ap-southeast-1` - Asia Pacific (Singapore)
- `ap-northeast-1` - Asia Pacific (Tokyo)

### Regional Base URLs
```
US: https://api-us.atlantiplex.com/v1
EU: https://api-eu.atlantiplex.com/v1
Asia: https://api-asia.atlantiplex.com/v1
```

---

## 📞 Support

### Support Channels
- **API Support**: api-support@atlantiplex.com
- **Technical Documentation**: https://docs.atlantiplex.com
- **Status Page**: https://status.atlantiplex.com
- **Community Forum**: https://community.atlantiplex.com

### Support Request Format
When contacting support, please include:
- Your API key or organization ID
- The specific endpoint and request details
- Error messages and timestamps
- Your region and environment

---

## 🚀 Getting Started

### Quick Start Guide
1. **Get API Key**: Register at https://dashboard.atlantiplex.com
2. **Choose Region**: Select the closest regional endpoint
3. **Install SDK**: Install the appropriate SDK for your language
4. **Make First Request**: Test authentication with a simple API call
5. **Implement Features**: Start building your integration

### Testing Environment
- **Sandbox URL**: https://sandbox-api.atlantiplex.com/v1
- **Test Credentials**: Available in developer dashboard
- **Test Data**: Pre-populated with sample users and streams

---

**Last Updated: February 8, 2026**  
**API Version: v1.2.0**  
**Documentation Version: 2.5**

For the most up-to-date information, visit our [developer portal](https://developers.atlantiplex.com).