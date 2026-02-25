import React, { useState } from 'react'
import './guest-manager.css'

export default function GuestManager({ guests, selectedGuests, onGuestToggle, onDockMove }) {
  return (
    <div className="guest-manager panel-component">
      <div className="panel-header">
        <h3 className="panel-title">
          <span className="panel-icon">◎</span>
          Guest Management
        </h3>
        <span className="panel-count">{selectedGuests.length}/{guests.length}</span>
      </div>

      <div className="guest-list">
        {guests.length === 0 ? (
          <div className="empty-state">
            <p>No guests connected</p>
            <span className="empty-icon">◎</span>
          </div>
        ) : (
          guests.map((guest, idx) => (
            <div
              key={guest.id}
              className={`guest-item ${selectedGuests.includes(guest.id) ? 'selected' : ''}`}
              onClick={() => onGuestToggle(guest.id)}
            >
              <div className="guest-header">
                <span className={`guest-status-light ${guest.connected ? 'connected' : 'offline'}`}></span>
                <span className="guest-name">{guest.name || `Guest ${idx + 1}`}</span>
              </div>
              <div className="guest-details">
                <span className="detail-label">{guest.resolution || '1080p'}</span>
                <span className="detail-label">{guest.bitrate || '3Mbps'}</span>
              </div>
              <div className="guest-checkbox">
                <input
                  type="checkbox"
                  checked={selectedGuests.includes(guest.id)}
                  onChange={() => onGuestToggle(guest.id)}
                  className="checkbox-input"
                />
              </div>
            </div>
          ))
        )}
      </div>

      {guests.length > 0 && (
        <div className="guest-actions">
          <button className="action-btn">Invite Guest</button>
        </div>
      )}
    </div>
  )
}
