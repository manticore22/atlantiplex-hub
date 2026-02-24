import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Brain, Sparkles, MessageCircle, Lightbulb, TrendingUp, AlertCircle, CheckCircle, X, Send, Bot, User } from 'lucide-react';

const AIAssistant = ({ user, context, onAction, theme }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [suggestions, setSuggestions] = useState([]);
  const [activeTab, setActiveTab] = useState('chat');
  const [insights, setInsights] = useState([]);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    // Initialize with welcome message
    const welcomeMessage = {
      id: 'welcome',
      type: 'assistant',
      content: `Hi ${user?.name || 'there'}! I'm your AI assistant. I can help you with streaming optimization, analytics insights, and platform features. What would you like to know?`,
      timestamp: new Date(),
      suggestions: [
        'How can I improve stream quality?',
        'Show me my analytics insights',
        'What are the best streaming settings?',
        'Help me grow my audience'
      ]
    };
    setMessages([welcomeMessage]);

    // Generate initial insights
    generateInsights();
  }, [user]);

  useEffect(() => {
    // Scroll to bottom when new messages arrive
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    // Focus input when chat opens
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  const generateInsights = useCallback(() => {
    const mockInsights = [
      {
        id: 1,
        type: 'optimization',
        title: 'Stream Quality Optimization',
        description: 'Your current bitrate of 5000 kbps is optimal for 1080p streaming. Consider increasing to 6000 kbps for 4K content.',
        icon: TrendingUp,
        priority: 'high',
        action: 'Adjust Settings'
      },
      {
        id: 2,
        type: 'engagement',
        title: 'Audience Engagement Trend',
        description: 'Your peak engagement occurs between 8-10 PM. Consider scheduling more streams during this time.',
        icon: Sparkles,
        priority: 'medium',
        action: 'View Analytics'
      },
      {
        id: 3,
        type: 'growth',
        title: 'Growth Opportunity',
        description: 'Your viewership increased 25% this week. Focus on consistent streaming to maintain momentum.',
        icon: Lightbulb,
        priority: 'low',
        action: 'Growth Tips'
      }
    ];
    setInsights(mockInsights);
  }, []);

  const generateResponse = useCallback(async (userMessage) => {
    setIsTyping(true);

    // Simulate AI processing delay
    await new Promise(resolve => setTimeout(resolve, 1500));

    let response = '';
    let suggestions = [];

    // Simple keyword-based responses (in real app, this would be an AI API call)
    const message = userMessage.toLowerCase();
    
    if (message.includes('quality') || message.includes('bitrate')) {
      response = 'For optimal streaming quality, I recommend:\n\n• 1080p: 5000-6000 kbps\n• 720p: 2500-4000 kbps\n• 4K: 8000-15000 kbps\n\nYour current settings look good! Would you like me to help you adjust them?';
      suggestions = ['Adjust bitrate', 'Test quality', 'Optimize for platform'];
    } else if (message.includes('analytics') || message.includes('insights')) {
      response = 'Based on your recent analytics:\n\n• Average viewers: 245 (+12% this week)\n• Peak engagement: 8-10 PM\n• Top platform: YouTube (65% of views)\n• Average duration: 45 minutes\n\nWould you like me to dive deeper into any of these metrics?';
      suggestions = ['Show detailed analytics', 'Compare platforms', 'Engagement tips'];
    } else if (message.includes('grow') || message.includes('audience')) {
      response = 'Here are proven strategies to grow your audience:\n\n1. **Consistency**: Stream at the same time daily\n2. **Engagement**: Respond to chat within 30 seconds\n3. **Content**: Plan your streams with clear topics\n4. **Promotion**: Share clips on social media\n5. **Collaboration**: Partner with other streamers\n\nWhich area would you like to focus on first?';
      suggestions = ['Content planning', 'Social media tips', 'Collaboration ideas'];
    } else if (message.includes('settings') || message.includes('optimize')) {
      response = 'I can help optimize your settings! Based on your setup:\n\n• **Video**: 1080p at 60fps ✓\n• **Audio**: 128 kbps ✓\n• **Bitrate**: 5000 kbps ✓\n\nEverything looks optimized! Would you like me to suggest advanced settings?';
      suggestions = ['Advanced settings', 'Test performance', 'Platform-specific optimization'];
    } else {
      response = 'I understand you\'re asking about ' + userMessage + '. Let me help you with that. Could you provide more details about what specific aspect you\'d like to know?';
      suggestions = ['Stream settings', 'Analytics help', 'Growth strategies', 'Technical support'];
    }

    const assistantMessage = {
      id: Date.now(),
      type: 'assistant',
      content: response,
      timestamp: new Date(),
      suggestions
    };

    setMessages(prev => [...prev, assistantMessage]);
    setIsTyping(false);
  }, []);

  const handleSendMessage = useCallback(async () => {
    if (!inputValue.trim()) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputValue,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setSuggestions([]);

    await generateResponse(inputValue);
  }, [inputValue, generateResponse]);

  const handleSuggestionClick = useCallback((suggestion) => {
    setInputValue(suggestion);
    inputRef.current?.focus();
  }, []);

  const handleInsightAction = useCallback((insight) => {
    onAction?.(insight);
  }, [onAction]);

  const formatTimestamp = useCallback((timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  }, []);

  const ChatInterface = () => (
    <div className="ai-chat-interface">
      <div className="chat-messages">
        {messages.map(message => (
          <div 
            key={message.id} 
            className={`message ${message.type}`}
          >
            <div className="message-avatar">
              {message.type === 'assistant' ? (
                <Bot size={20} />
              ) : (
                <User size={20} />
              )}
            </div>
            <div className="message-content">
              <div className="message-text">
                {message.content.split('\n').map((line, index) => (
                  <p key={index}>{line}</p>
                ))}
              </div>
              <div className="message-time">
                {formatTimestamp(message.timestamp)}
              </div>
              {message.suggestions && (
                <div className="message-suggestions">
                  {message.suggestions.map((suggestion, index) => (
                    <button
                      key={index}
                      onClick={() => handleSuggestionClick(suggestion)}
                      className="suggestion-btn"
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        
        {isTyping && (
          <div className="message assistant typing">
            <div className="message-avatar">
              <Bot size={20} />
            </div>
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input">
        <div className="input-container">
          <input
            ref={inputRef}
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSendMessage();
              }
            }}
            placeholder="Ask me anything about streaming..."
            className="ai-input"
          />
          <button
            onClick={handleSendMessage}
            disabled={!inputValue.trim() || isTyping}
            className="send-btn"
          >
            <Send size={20} />
          </button>
        </div>
      </div>
    </div>
  );

  const InsightsInterface = () => (
    <div className="ai-insights-interface">
      <div className="insights-header">
        <h3>AI-Powered Insights</h3>
        <button onClick={generateInsights} className="refresh-btn">
          <Sparkles size={16} />
          Refresh
        </button>
      </div>
      
      <div className="insights-list">
        {insights.map(insight => (
          <div key={insight.id} className={`insight-card priority-${insight.priority}`}>
            <div className="insight-icon">
              <insight.icon size={24} />
            </div>
            <div className="insight-content">
              <h4>{insight.title}</h4>
              <p>{insight.description}</p>
              <button 
                onClick={() => handleInsightAction(insight)}
                className="insight-action"
              >
                {insight.action}
              </button>
            </div>
            <div className="insight-priority">
              <span className={`priority-badge ${insight.priority}`}>
                {insight.priority}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="ai-assistant-fab"
        title="AI Assistant"
      >
        <Brain size={24} />
        <div className="fab-pulse"></div>
      </button>
    );
  }

  return (
    <div className="ai-assistant-panel">
      <div className="assistant-header">
        <div className="header-left">
          <div className="assistant-avatar">
            <Brain size={24} />
            <div className="status-indicator online"></div>
          </div>
          <div className="assistant-info">
            <h3>AI Assistant</h3>
            <span className="status-text">Online • Ready to help</span>
          </div>
        </div>
        
        <div className="header-right">
          <div className="assistant-tabs">
            <button
              className={`tab-btn ${activeTab === 'chat' ? 'active' : ''}`}
              onClick={() => setActiveTab('chat')}
            >
              <MessageCircle size={16} />
              Chat
            </button>
            <button
              className={`tab-btn ${activeTab === 'insights' ? 'active' : ''}`}
              onClick={() => setActiveTab('insights')}
            >
              <Lightbulb size={16} />
              Insights
            </button>
          </div>
          
          <button
            onClick={() => setIsOpen(false)}
            className="close-btn"
            title="Close AI Assistant"
          >
            <X size={20} />
          </button>
        </div>
      </div>

      <div className="assistant-content">
        {activeTab === 'chat' && <ChatInterface />}
        {activeTab === 'insights' && <InsightsInterface />}
      </div>

      <div className="assistant-footer">
        <div className="quick-actions">
          <button 
            onClick={() => setInputValue('How can I improve my stream quality?')}
            className="quick-action-btn"
          >
            <TrendingUp size={16} />
            Improve Quality
          </button>
          <button 
            onClick={() => setInputValue('Show me my analytics')}
            className="quick-action-btn"
          >
            <BarChart size={16} />
            View Analytics
          </button>
          <button 
            onClick={() => setInputValue('Help me grow my audience')}
            className="quick-action-btn"
          >
            <Users size={16} />
            Grow Audience
          </button>
        </div>
        
        <div className="disclaimer">
          <AlertCircle size={12} />
          <span>AI responses are for guidance. Verify important settings.</span>
        </div>
      </div>
    </div>
  );
};

export default AIAssistant;