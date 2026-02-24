import React, { useState, useRef, useEffect } from 'react'
import './chat-panel.css'

export default function ChatPanel({ messages, onSendMessage, isStreaming, onDockMove }) {
  const [messageInput, setMessageInput] = useState('')
  const messagesEndRef = useRef(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSendMessage = () => {
    if (messageInput.trim()) {
      onSendMessage(messageInput)
      setMessageInput('')
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  return (
    <div className="chat-panel panel-component">
      <div className="panel-header">
        <h3 className="panel-title">
          <span className="panel-icon">💬</span>
          Live Comments
        </h3>
        <span className="panel-count">{messages.length}</span>
      </div>

      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="empty-state">
            <p>No messages yet</p>
            <span className="empty-icon">◈</span>
          </div>
        ) : (
          messages.map((msg, idx) => (
            <div key={idx} className="chat-message">
              <div className="message-header">
                <span className="message-sender">{msg.sender || 'Viewer'}</span>
                <span className="message-time">{new Date(msg.timestamp).toLocaleTimeString()}</span>
              </div>
              <p className="message-content">{msg.message}</p>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-area">
        <textarea
          className="chat-input"
          placeholder={isStreaming ? "Comment as broadcaster..." : "Stream offline"}
          value={messageInput}
          onChange={(e) => setMessageInput(e.target.value)}
          onKeyPress={handleKeyPress}
          disabled={!isStreaming}
          rows="2"
        />
        <button 
          className="send-btn"
          onClick={handleSendMessage}
          disabled={!isStreaming || !messageInput.trim()}
        >
          Send
        </button>
      </div>
    </div>
  )
}
