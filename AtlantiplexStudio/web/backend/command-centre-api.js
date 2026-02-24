/**
 * Command Centre REST API Endpoints
 * 
 * Express router for Command Centre API
 * Base path: /api/command-centre
 */

const express = require('express');
const router = express.Router();
const { requireCommandCentreAccess } = require('./auth/command-centre-auth');
const commandCentreWS = require('./command-centre-websocket');

// All routes require admin access
router.use(requireCommandCentreAccess);

/**
 * GET /api/command-centre/state
 * Get current Command Centre state
 */
router.get('/state', (req, res) => {
  try {
    const state = commandCentreWS.getCommandCentreState();
    res.json({
      success: true,
      data: state
    });
  } catch (error) {
    console.error('[CommandCentre API] Error getting state:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get state'
    });
  }
});

/**
 * GET /api/command-centre/metrics
 * Get current metrics
 */
router.get('/metrics', (req, res) => {
  try {
    const state = commandCentreWS.getCommandCentreState();
    res.json({
      success: true,
      data: state.metrics
    });
  } catch (error) {
    console.error('[CommandCentre API] Error getting metrics:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get metrics'
    });
  }
});

/**
 * POST /api/command-centre/metrics
 * Update metrics from external sources
 */
router.post('/metrics', (req, res) => {
  try {
    const metrics = req.body;
    commandCentreWS.updateMetrics(metrics);
    
    res.json({
      success: true,
      message: 'Metrics updated'
    });
  } catch (error) {
    console.error('[CommandCentre API] Error updating metrics:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to update metrics'
    });
  }
});

/**
 * GET /api/command-centre/chronicle
 * Get chronicle entries
 */
router.get('/chronicle', (req, res) => {
  try {
    const { limit = 50, type } = req.query;
    const state = commandCentreWS.getCommandCentreState();
    
    let entries = state.chronicle;
    
    if (type && type !== 'all') {
      entries = entries.filter(e => e.type === type);
    }
    
    entries = entries.slice(0, parseInt(limit));
    
    res.json({
      success: true,
      data: entries
    });
  } catch (error) {
    console.error('[CommandCentre API] Error getting chronicle:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get chronicle'
    });
  }
});

/**
 * POST /api/command-centre/chronicle
 * Add chronicle entry
 */
router.post('/chronicle', (req, res) => {
  try {
    const entry = req.body;
    const fullEntry = commandCentreWS.addChronicleEntry(entry);
    
    res.json({
      success: true,
      data: fullEntry
    });
  } catch (error) {
    console.error('[CommandCentre API] Error adding chronicle entry:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to add chronicle entry'
    });
  }
});

/**
 * POST /api/command-centre/guests/join
 * Log guest join
 */
router.post('/guests/join', (req, res) => {
  try {
    const guest = req.body;
    commandCentreWS.addGuest(guest);
    
    res.json({
      success: true,
      message: 'Guest join logged'
    });
  } catch (error) {
    console.error('[CommandCentre API] Error logging guest join:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to log guest join'
    });
  }
});

/**
 * POST /api/command-centre/guests/leave
 * Log guest leave
 */
router.post('/guests/leave', (req, res) => {
  try {
    const { guestId } = req.body;
    commandCentreWS.removeGuest(guestId);
    
    res.json({
      success: true,
      message: 'Guest leave logged'
    });
  } catch (error) {
    console.error('[CommandCentre API] Error logging guest leave:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to log guest leave'
    });
  }
});

/**
 * POST /api/command-centre/moderator-action
 * Log moderator action
 */
router.post('/moderator-action', (req, res) => {
  try {
    const { action, target } = req.body;
    commandCentreWS.logModeratorAction(action, target, req.user.username);
    
    res.json({
      success: true,
      message: 'Moderator action logged'
    });
  } catch (error) {
    console.error('[CommandCentre API] Error logging moderator action:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to log moderator action'
    });
  }
});

/**
 * POST /api/command-centre/warning
 * Log system warning
 */
router.post('/warning', (req, res) => {
  try {
    const { title, message } = req.body;
    commandCentreWS.logSystemWarning(title, message);
    
    res.json({
      success: true,
      message: 'Warning logged'
    });
  } catch (error) {
    console.error('[CommandCentre API] Error logging warning:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to log warning'
    });
  }
});

/**
 * POST /api/command-centre/alert
 * Log system alert
 */
router.post('/alert', (req, res) => {
  try {
    const { title, message, severity } = req.body;
    commandCentreWS.logSystemAlert(title, message, severity);
    
    res.json({
      success: true,
      message: 'Alert logged'
    });
  } catch (error) {
    console.error('[CommandCentre API] Error logging alert:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to log alert'
    });
  }
});

/**
 * GET /api/command-centre/health
 * Health check endpoint
 */
router.get('/health', (req, res) => {
  res.json({
    success: true,
    status: 'operational',
    timestamp: new Date().toISOString()
  });
});

module.exports = router;