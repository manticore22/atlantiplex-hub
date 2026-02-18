const express = require('express');
const router = express.Router();
const { MongoClient, ObjectId } = require('mongodb');

// Analytics database connection
let db;
MongoClient.connect(process.env.MONGODB_URI)
  .then(client => {
    db = client.db('atlantiplex_analytics');
  })
  .catch(err => console.error('Analytics DB connection failed:', err));

// Main Analytics Dashboard
router.get('/dashboard', async (req, res) => {
  try {
    const { timeRange = '7d' } = req.query;
    const timeFilter = getTimeFilter(timeRange);
    
    const [
      overview,
      userEngagement,
      streamingMetrics,
      revenueAnalytics,
      featureUsage,
      geographicalData,
      conversionFunnel,
      cohortAnalysis
    ] = await Promise.all([
      getOverviewMetrics(timeFilter),
      getUserEngagementMetrics(timeFilter),
      getStreamingMetrics(timeFilter),
      getRevenueAnalytics(timeFilter),
      getFeatureUsageAnalytics(timeFilter),
      getGeographicalAnalytics(timeFilter),
      getConversionFunnel(timeFilter),
      getCohortAnalysis(timeFilter)
    ]);

    res.json({
      overview,
      userEngagement,
      streamingMetrics,
      revenueAnalytics,
      featureUsage,
      geographicalData,
      conversionFunnel,
      cohortAnalysis
    });
  } catch (error) {
    console.error('Analytics dashboard error:', error);
    res.status(500).json({ error: 'Failed to load analytics data' });
  }
});

// Real-time Metrics
router.get('/realtime', async (req, res) => {
  try {
    const realtimeData = await Promise.all([
      getCurrentOnlineUsers(),
      getActiveStreams(),
      getServerLoad(),
      getAPIRequestsPerMinute(),
      getRecentActivity()
    ]);

    res.json({
      onlineUsers: realtimeData[0],
      activeStreams: realtimeData[1],
      serverLoad: realtimeData[2],
      apiRequests: realtimeData[3],
      recentActivity: realtimeData[4],
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('Realtime analytics error:', error);
    res.status(500).json({ error: 'Failed to load realtime data' });
  }
});

// User Analytics
router.get('/users', async (req, res) => {
  try {
    const { timeRange, segment } = req.query;
    const timeFilter = getTimeFilter(timeRange);
    
    const userAnalytics = await Promise.all([
      getUserGrowth(timeFilter),
      getUserRetention(timeFilter),
      getUserSegmentation(segment, timeFilter),
      getUserLifecycle(timeFilter)
    ]);

    res.json({
      growth: userAnalytics[0],
      retention: userAnalytics[1],
      segmentation: userAnalytics[2],
      lifecycle: userAnalytics[3]
    });
  } catch (error) {
    console.error('User analytics error:', error);
    res.status(500).json({ error: 'Failed to load user analytics' });
  }
});

// Streaming Analytics
router.get('/streaming', async (req, res) => {
  try {
    const { timeRange, platform, quality } = req.query;
    const timeFilter = getTimeFilter(timeRange);
    
    const streamingData = await Promise.all([
      getStreamingPerformance(timeFilter, platform, quality),
      getStreamingQualityMetrics(timeFilter),
      getStreamingRevenue(timeFilter),
      getStreamingAudience(timeFilter)
    ]);

    res.json({
      performance: streamingData[0],
      quality: streamingData[1],
      revenue: streamingData[2],
      audience: streamingData[3]
    });
  } catch (error) {
    console.error('Streaming analytics error:', error);
    res.status(500).json({ error: 'Failed to load streaming analytics' });
  }
});

// Revenue Analytics
router.get('/revenue', async (req, res) => {
  try {
    const { timeRange, source } = req.query;
    const timeFilter = getTimeFilter(timeRange);
    
    const revenueData = await Promise.all([
      getRevenueBreakdown(timeFilter, source),
      getSubscriptionMetrics(timeFilter),
      getPaymentAnalytics(timeFilter),
      getARPU(timeFilter)
    ]);

    res.json({
      breakdown: revenueData[0],
      subscriptions: revenueData[1],
      payments: revenueData[2],
      arpu: revenueData[3]
    });
  } catch (error) {
    console.error('Revenue analytics error:', error);
    res.status(500).json({ error: 'Failed to load revenue analytics' });
  }
});

// Custom Events Tracking
router.post('/track', async (req, res) => {
  try {
    const { userId, event, properties, timestamp = new Date() } = req.body;
    
    // Validate event data
    if (!userId || !event) {
      return res.status(400).json({ error: 'Missing required fields' });
    }

    // Store event in analytics collection
    await db.collection('events').insertOne({
      userId,
      event,
      properties,
      timestamp,
      userAgent: req.get('User-Agent'),
      ip: req.ip,
      sessionId: req.session?.id
    });

    // Update real-time metrics
    await updateRealtimeMetrics(event, properties);

    res.json({ success: true, tracked: true });
  } catch (error) {
    console.error('Event tracking error:', error);
    res.status(500).json({ error: 'Failed to track event' });
  }
});

// Export Analytics Data
router.get('/export', async (req, res) => {
  try {
    const { format = 'csv', timeRange, type = 'dashboard' } = req.query;
    const timeFilter = getTimeFilter(timeRange);
    
    let data;
    switch (type) {
      case 'dashboard':
        data = await getDashboardDataForExport(timeFilter);
        break;
      case 'users':
        data = await getUserDataForExport(timeFilter);
        break;
      case 'revenue':
        data = await getRevenueDataForExport(timeFilter);
        break;
      default:
        throw new Error('Invalid export type');
    }

    if (format === 'csv') {
      const csv = convertToCSV(data);
      res.setHeader('Content-Type', 'text/csv');
      res.setHeader('Content-Disposition', `attachment; filename="analytics-${Date.now()}.csv"`);
      res.send(csv);
    } else if (format === 'pdf') {
      const pdf = await generatePDFReport(data);
      res.setHeader('Content-Type', 'application/pdf');
      res.setHeader('Content-Disposition', `attachment; filename="analytics-${Date.now()}.pdf"`);
      res.send(pdf);
    } else {
      throw new Error('Unsupported format');
    }
  } catch (error) {
    console.error('Export error:', error);
    res.status(500).json({ error: 'Failed to export data' });
  }
});

// Analytics Helper Functions

function getTimeFilter(timeRange) {
  const now = new Date();
  let startDate;
  
  switch (timeRange) {
    case '24h':
      startDate = new Date(now.getTime() - 24 * 60 * 60 * 1000);
      break;
    case '7d':
      startDate = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
      break;
    case '30d':
      startDate = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
      break;
    case '90d':
      startDate = new Date(now.getTime() - 90 * 24 * 60 * 60 * 1000);
      break;
    case '1y':
      startDate = new Date(now.getTime() - 365 * 24 * 60 * 60 * 1000);
      break;
    default:
      startDate = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
  }
  
  return { $gte: startDate, $lte: now };
}

async function getOverviewMetrics(timeFilter) {
  const [totalUsers, activeStreams, revenue, engagementRate] = await Promise.all([
    db.collection('users').countDocuments({ createdAt: timeFilter }),
    db.collection('streams').countDocuments({ startTime: timeFilter, status: 'active' }),
    db.collection('payments').aggregate([
      { $match: { createdAt: timeFilter, status: 'completed' } },
      { $group: { _id: null, total: { $sum: '$amount' } } }
    ]).toArray(),
    db.collection('events').aggregate([
      { $match: { timestamp: timeFilter, event: { $in: ['page_view', 'interaction'] } } },
      { $group: { _id: '$userId', count: { $sum: 1 } } },
      { $group: { _id: null, avgCount: { $avg: '$count' } } }
    ]).toArray()
  ]);

  return {
    totalUsers: totalUsers || 0,
    activeStreams: activeStreams || 0,
    revenue: revenue[0]?.total || 0,
    engagementRate: Math.round((engagementRate[0]?.avgCount || 0) * 100) / 100,
    userGrowth: calculateGrowth('users', timeFilter),
    streamGrowth: calculateGrowth('streams', timeFilter),
    revenueGrowth: calculateGrowth('revenue', timeFilter)
  };
}

async function getUserEngagementMetrics(timeFilter) {
  const engagementData = await db.collection('events').aggregate([
    { $match: { timestamp: timeFilter } },
    {
      $group: {
        _id: {
          date: { $dateToString: { format: '%Y-%m-%d', date: '$timestamp' } },
          event: '$event'
        },
        count: { $sum: 1 }
      }
    },
    {
      $group: {
        _id: '$_id.date',
        events: {
          $push: {
            event: '$_id.event',
            count: '$count'
          }
        }
      }
    },
    { $sort: { _id: 1 } }
  ]).toArray();

  return engagementData.map(day => ({
    date: day._id,
    newUsers: day.events.find(e => e.event === 'user_signup')?.count || 0,
    activeUsers: day.events.find(e => e.event === 'login')?.count || 0,
    pageViews: day.events.find(e => e.event === 'page_view')?.count || 0,
    interactions: day.events.find(e => e.event === 'interaction')?.count || 0
  }));
}

async function getStreamingMetrics(timeFilter) {
  const [totalStreams, avgDuration, peakConcurrent, platformDistribution, qualityMetrics] = await Promise.all([
    db.collection('streams').countDocuments({ startTime: timeFilter }),
    db.collection('streams').aggregate([
      { $match: { startTime: timeFilter } },
      { $group: { _id: null, avgDuration: { $avg: '$duration' } } }
    ]).toArray(),
    db.collection('streams').aggregate([
      { $match: { startTime: timeFilter } },
      { $group: { _id: null, maxConcurrent: { $max: '$concurrentViewers' } } }
    ]).toArray(),
    db.collection('streams').aggregate([
      { $match: { startTime: timeFilter } },
      { $group: { _id: '$platform', count: { $sum: 1 } } },
      { $sort: { count: -1 } }
    ]).toArray(),
    getStreamingQualityMetrics(timeFilter)
  ]);

  return {
    totalStreams: totalStreams || 0,
    averageDuration: Math.round(avgDuration[0]?.avgDuration || 0),
    peakConcurrent: peakConcurrent[0]?.maxConcurrent || 0,
    platformDistribution: platformDistribution.map(p => ({
      platform: p._id,
      streams: p.count
    })),
    qualityMetrics
  };
}

async function getFeatureUsageAnalytics(timeFilter) {
  const featureEvents = await db.collection('events').aggregate([
    { $match: { timestamp: timeFilter, event: { $regex: '^feature_' } } },
    {
      $group: {
        _id: '$event',
        users: { $addToSet: '$userId' },
        count: { $sum: 1 }
      }
    },
    {
      $project: {
        feature: { $substr: ['$_id', 8, -1] }, // Remove 'feature_' prefix
        activeUsers: { $size: '$users' },
        totalUsage: '$count',
        frequency: { $divide: ['$count', { $size: '$users' }] }
      }
    }
  ]).toArray();

  const totalUsers = await db.collection('users').countDocuments({ createdAt: timeFilter });

  return featureEvents.reduce((acc, feature) => {
    acc[feature.feature] = {
      activeUsers: feature.activeUsers,
      totalUsage: feature.totalUsage,
      frequency: Math.round(feature.frequency * 100) / 100,
      adoptionRate: Math.round((feature.activeUsers / totalUsers) * 100 * 100) / 100
    };
    return acc;
  }, {});
}

async function getRevenueAnalytics(timeFilter) {
  const revenueData = await db.collection('payments').aggregate([
    { $match: { createdAt: timeFilter, status: 'completed' } },
    {
      $group: {
        _id: '$type',
        amount: { $sum: '$amount' },
        count: { $sum: 1 }
      }
    }
  ]).toArray();

  return revenueData.map(item => ({
    name: item._id,
    value: item.amount,
    count: item.count
  }));
}

async function getGeographicalAnalytics(timeFilter) {
  const geoData = await db.collection('users').aggregate([
    { $match: { createdAt: timeFilter, 'location.country': { $exists: true } } },
    {
      $group: {
        _id: '$location.country',
        users: { $sum: 1 },
        revenue: { $sum: '$totalSpent' || 0 }
      }
    },
    { $sort: { users: -1 } },
    { $limit: 10 }
  ]).toArray();

  return geoData.map(country => ({
    country: country._id,
    users: country.users,
    revenue: country.revenue,
    engagementRate: Math.random() * 100, // Placeholder - calculate real engagement
    growth: Math.round((Math.random() - 0.5) * 100) // Placeholder - calculate real growth
  }));
}

async function getConversionFunnel(timeFilter) {
  const funnelStages = [
    'visit',
    'signup',
    'payment_page',
    'payment_complete'
  ];

  const funnelData = await Promise.all(
    funnelStages.map(async (stage) => {
      const count = await db.collection('events').countDocuments({
        timestamp: timeFilter,
        event: stage
      });
      return { stage, users: count };
    })
  );

  return funnelData;
}

async function getCurrentOnlineUsers() {
  const fiveMinutesAgo = new Date(Date.now() - 5 * 60 * 1000);
  return await db.collection('events').distinct('userId', {
    timestamp: { $gte: fiveMinutesAgo },
    event: 'page_view'
  }).then(users => users.length);
}

async function getActiveStreams() {
  return await db.collection('streams').countDocuments({
    status: 'active'
  });
}

async function getServerLoad() {
  // Implement server load monitoring
  return Math.round(Math.random() * 100); // Placeholder
}

async function getAPIRequestsPerMinute() {
  const oneMinuteAgo = new Date(Date.now() - 60 * 1000);
  return await db.collection('api_logs').countDocuments({
    timestamp: { $gte: oneMinuteAgo }
  });
}

async function getRecentActivity() {
  const tenMinutesAgo = new Date(Date.now() - 10 * 60 * 1000);
  return await db.collection('events').find({
    timestamp: { $gte: tenMinutesAgo }
  })
  .sort({ timestamp: -1 })
  .limit(20)
  .toArray();
}

async function updateRealtimeMetrics(event, properties) {
  // Update real-time counters
  await db.collection('realtime_metrics').updateOne(
    { _id: 'counters' },
    {
      $inc: { [`counters.${event}`]: 1 },
      $set: { lastUpdated: new Date() }
    },
    { upsert: true }
  );
}

function calculateGrowth(metric, timeFilter) {
  // Calculate growth compared to previous period
  return Math.round(Math.random() * 50); // Placeholder
}

function convertToCSV(data) {
  // Convert data to CSV format
  if (Array.isArray(data)) {
    const headers = Object.keys(data[0] || {});
    const csvRows = [headers.join(',')];
    data.forEach(row => {
      csvRows.push(headers.map(header => row[header]).join(','));
    });
    return csvRows.join('\n');
  }
  return JSON.stringify(data);
}

async function generatePDFReport(data) {
  // Generate PDF report (would use a PDF library like puppeteer)
  return 'PDF content'; // Placeholder
}

// Additional helper functions for other analytics endpoints
async function getUserGrowth(timeFilter) { /* Implementation */ }
async function getUserRetention(timeFilter) { /* Implementation */ }
async function getUserSegmentation(segment, timeFilter) { /* Implementation */ }
async function getUserLifecycle(timeFilter) { /* Implementation */ }
async function getStreamingPerformance(timeFilter, platform, quality) { /* Implementation */ }
async function getStreamingQualityMetrics(timeFilter) { /* Implementation */ }
async function getStreamingRevenue(timeFilter) { /* Implementation */ }
async function getStreamingAudience(timeFilter) { /* Implementation */ }
async function getRevenueBreakdown(timeFilter, source) { /* Implementation */ }
async function getSubscriptionMetrics(timeFilter) { /* Implementation */ }
async function getPaymentAnalytics(timeFilter) { /* Implementation */ }
async function getARPU(timeFilter) { /* Implementation */ }
async function getCohortAnalysis(timeFilter) { /* Implementation */ }
async function getDashboardDataForExport(timeFilter) { /* Implementation */ }
async function getUserDataForExport(timeFilter) { /* Implementation */ }
async function getRevenueDataForExport(timeFilter) { /* Implementation */ }

module.exports = router;