import React, { useState, useEffect, useCallback } from 'react';
import { Line, Bar, Pie, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const AdvancedAnalytics = () => {
  const [timeRange, setTimeRange] = useState('7d');
  const [analyticsData, setAnalyticsData] = useState({
    overview: {},
    userEngagement: [],
    streamingMetrics: [],
    revenueAnalytics: [],
    featureUsage: {},
    geographicalData: [],
    deviceAnalytics: [],
    conversionFunnel: [],
    cohortAnalysis: [],
    realtimeMetrics: {}
  });
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    fetchAnalyticsData();
    
    // Set up real-time updates
    const interval = setInterval(() => {
      fetchRealtimeMetrics();
    }, 30000); // Update every 30 seconds

    return () => clearInterval(interval);
  }, [timeRange]);

  const fetchAnalyticsData = async () => {
    setLoading(true);
    try {
      const response = await fetch(`/api/analytics/dashboard?timeRange=${timeRange}`);
      const data = await response.json();
      setAnalyticsData(data);
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchRealtimeMetrics = async () => {
    try {
      const response = await fetch('/api/analytics/realtime');
      const data = await response.json();
      setAnalyticsData(prev => ({
        ...prev,
        realtimeMetrics: data
      }));
    } catch (error) {
      console.error('Failed to fetch realtime metrics:', error);
    }
  };

  const exportReport = async (format = 'csv') => {
    try {
      const response = await fetch(`/api/analytics/export?format=${format}&timeRange=${timeRange}`);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `analytics-report-${timeRange}.${format}`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Failed to export report:', error);
    }
  };

  const renderOverviewTab = () => (
    <div className="analytics-overview">
      <div className="metrics-grid">
        <div className="metric-card">
          <h3>Total Users</h3>
          <div className="metric-value">
            {analyticsData.overview.totalUsers?.toLocaleString() || 0}
          </div>
          <div className="metric-change positive">
            +{analyticsData.overview.userGrowth || 0}% from last period
          </div>
        </div>
        
        <div className="metric-card">
          <h3>Active Streams</h3>
          <div className="metric-value">
            {analyticsData.overview.activeStreams?.toLocaleString() || 0}
          </div>
          <div className="metric-change positive">
            +{analyticsData.overview.streamGrowth || 0}% from last period
          </div>
        </div>
        
        <div className="metric-card">
          <h3>Revenue</h3>
          <div className="metric-value">
            ${analyticsData.overview.revenue?.toLocaleString() || 0}
          </div>
          <div className="metric-change positive">
            +{analyticsData.overview.revenueGrowth || 0}% from last period
          </div>
        </div>
        
        <div className="metric-card">
          <h3>Engagement Rate</h3>
          <div className="metric-value">
            {analyticsData.overview.engagementRate || 0}%
          </div>
          <div className="metric-change negative">
            -{analyticsData.overview.engagementChange || 0}% from last period
          </div>
        </div>
      </div>

      <div className="chart-section">
        <div className="chart-container">
          <h3>User Growth Trend</h3>
          <ResponsiveContainer width="100%" height={300}>
            <Area data={analyticsData.userEngagement}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Area type="monotone" dataKey="newUsers" stackId="1" stroke="#8884d8" fill="#8884d8" />
              <Area type="monotone" dataKey="activeUsers" stackId="1" stroke="#82ca9d" fill="#82ca9d" />
            </Area>
          </ResponsiveContainer>
        </div>

        <div className="chart-container">
          <h3>Revenue Breakdown</h3>
          <ResponsiveContainer width="100%" height={300}>
            <Pie>
              <Pie
                data={analyticsData.revenueAnalytics}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              />
              <Tooltip />
            </Pie>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );

  const renderStreamingTab = () => (
    <div className="streaming-analytics">
      <div className="metrics-grid">
        <div className="metric-card">
          <h3>Total Streams</h3>
          <div className="metric-value">
            {analyticsData.streamingMetrics.totalStreams?.toLocaleString() || 0}
          </div>
        </div>
        
        <div className="metric-card">
          <h3>Avg Duration</h3>
          <div className="metric-value">
            {analyticsData.streamingMetrics.averageDuration || 0} min
          </div>
        </div>
        
        <div className="metric-card">
          <h3>Peak Concurrent</h3>
          <div className="metric-value">
            {analyticsData.streamingMetrics.peakConcurrent?.toLocaleString() || 0}
          </div>
        </div>
        
        <div className="metric-card">
          <h3>Platform Distribution</h3>
          <ResponsiveContainer width="100%" height={150}>
            <Bar data={analyticsData.streamingMetrics.platformDistribution}>
              <XAxis dataKey="platform" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="streams" fill="#82ca9d" />
            </Bar>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="chart-container">
        <h3>Streaming Quality Metrics</h3>
        <ResponsiveContainer width="100%" height={400}>
          <Line data={analyticsData.streamingMetrics.qualityMetrics}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="avgBitrate" stroke="#8884d8" name="Avg Bitrate (Mbps)" />
            <Line type="monotone" dataKey="bufferRate" stroke="#82ca9d" name="Buffer Rate (%)" />
            <Line type="monotone" dataKey="dropRate" stroke="#ffc658" name="Drop Rate (%)" />
          </Line>
        </ResponsiveContainer>
      </div>
    </div>
  );

  const renderUserBehaviorTab = () => (
    <div className="user-behavior-analytics">
      <div className="behavior-metrics">
        <div className="metric-card">
          <h3>Session Duration</h3>
          <div className="metric-value">
            {analyticsData.userEngagement.avgSessionDuration || 0} min
          </div>
        </div>
        
        <div className="metric-card">
          <h3>Bounce Rate</h3>
          <div className="metric-value">
            {analyticsData.userEngagement.bounceRate || 0}%
          </div>
        </div>
        
        <div className="metric-card">
          <h3>Pages per Session</h3>
          <div className="metric-value">
            {analyticsData.userEngagement.pagesPerSession || 0}
          </div>
        </div>
      </div>

      <div className="feature-usage">
        <h3>Feature Usage Analytics</h3>
        <div className="feature-grid">
          {Object.entries(analyticsData.featureUsage || {}).map(([feature, data]) => (
            <div key={feature} className="feature-card">
              <h4>{feature}</h4>
              <div className="usage-metrics">
                <div className="usage-stat">
                  <span>Active Users:</span>
                  <strong>{data.activeUsers?.toLocaleString() || 0}</strong>
                </div>
                <div className="usage-stat">
                  <span>Usage Frequency:</span>
                  <strong>{data.frequency || 0}/day</strong>
                </div>
                <div className="usage-progress">
                  <div 
                    className="progress-bar" 
                    style={{ width: `${data.adoptionRate || 0}%` }}
                  ></div>
                  <span>{data.adoptionRate || 0}% adoption</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="conversion-funnel">
        <h3>Conversion Funnel</h3>
        <ResponsiveContainer width="100%" height={400}>
          <Bar data={analyticsData.conversionFunnel} layout="horizontal">
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis type="number" />
            <YAxis dataKey="stage" type="category" />
            <Tooltip />
            <Bar dataKey="users" fill="#8884d8" />
          </Bar>
        </ResponsiveContainer>
      </div>
    </div>
  );

  const renderGeographicalTab = () => (
    <div className="geographical-analytics">
      <h3>User Distribution by Region</h3>
      <div className="geo-metrics">
        {analyticsData.geographicalData.map((region, index) => (
          <div key={index} className="region-card">
            <h4>{region.country}</h4>
            <div className="region-stats">
              <div className="stat">
                <span>Users:</span>
                <strong>{region.users?.toLocaleString() || 0}</strong>
              </div>
              <div className="stat">
                <span>Revenue:</span>
                <strong>${region.revenue?.toLocaleString() || 0}</strong>
              </div>
              <div className="stat">
                <span>Engagement:</span>
                <strong>{region.engagementRate || 0}%</strong>
              </div>
            </div>
            <div className="growth-indicator">
              {region.growth > 0 ? (
                <span className="positive">+{region.growth}%</span>
              ) : (
                <span className="negative">{region.growth}%</span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderRealtimeTab = () => (
    <div className="realtime-analytics">
      <h3>Real-Time Metrics</h3>
      <div className="realtime-grid">
        <div className="realtime-card">
          <h4>Current Online Users</h4>
          <div className="realtime-value">
            {analyticsData.realtimeMetrics.onlineUsers?.toLocaleString() || 0}
          </div>
        </div>
        
        <div className="realtime-card">
          <h4>Active Streams</h4>
          <div className="realtime-value">
            {analyticsData.realtimeMetrics.activeStreams?.toLocaleString() || 0}
          </div>
        </div>
        
        <div className="realtime-card">
          <h4>Server Load</h4>
          <div className="realtime-value">
            {analyticsData.realtimeMetrics.serverLoad || 0}%
          </div>
        </div>
        
        <div className="realtime-card">
          <h4>API Requests/min</h4>
          <div className="realtime-value">
            {analyticsData.realtimeMetrics.apiRequests?.toLocaleString() || 0}
          </div>
        </div>
      </div>

      <div className="recent-activity">
        <h3>Recent Activity Feed</h3>
        <div className="activity-feed">
          {analyticsData.realtimeMetrics.recentActivity?.map((activity, index) => (
            <div key={index} className="activity-item">
              <span className="activity-time">{new Date(activity.timestamp).toLocaleTimeString()}</span>
              <span className="activity-type">{activity.type}</span>
              <span className="activity-user">{activity.user}</span>
              <span className="activity-action">{activity.action}</span>
            </div>
          )) || <p>No recent activity</p>}
        </div>
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="analytics-loading">
        <div className="spinner"></div>
        <p>Loading analytics data...</p>
      </div>
    );
  }

  return (
    <div className="advanced-analytics">
      <div className="analytics-header">
        <h2>Advanced Analytics Dashboard</h2>
        
        <div className="analytics-controls">
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="time-range-selector"
          >
            <option value="24h">Last 24 Hours</option>
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
            <option value="90d">Last 90 Days</option>
            <option value="1y">Last Year</option>
          </select>
          
          <div className="export-controls">
            <button onClick={() => exportReport('csv')} className="export-btn">
              📊 Export CSV
            </button>
            <button onClick={() => exportReport('pdf')} className="export-btn">
              📄 Export PDF
            </button>
          </div>
        </div>
      </div>

      <div className="analytics-tabs">
        <button
          className={`tab-btn ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button
          className={`tab-btn ${activeTab === 'streaming' ? 'active' : ''}`}
          onClick={() => setActiveTab('streaming')}
        >
          Streaming
        </button>
        <button
          className={`tab-btn ${activeTab === 'behavior' ? 'active' : ''}`}
          onClick={() => setActiveTab('behavior')}
        >
          User Behavior
        </button>
        <button
          className={`tab-btn ${activeTab === 'geographical' ? 'active' : ''}`}
          onClick={() => setActiveTab('geographical')}
        >
          Geographical
        </button>
        <button
          className={`tab-btn ${activeTab === 'realtime' ? 'active' : ''}`}
          onClick={() => setActiveTab('realtime')}
        >
          Real-Time
        </button>
      </div>

      <div className="analytics-content">
        {activeTab === 'overview' && renderOverviewTab()}
        {activeTab === 'streaming' && renderStreamingTab()}
        {activeTab === 'behavior' && renderUserBehaviorTab()}
        {activeTab === 'geographical' && renderGeographicalTab()}
        {activeTab === 'realtime' && renderRealtimeTab()}
      </div>
    </div>
  );
};

export default AdvancedAnalytics;