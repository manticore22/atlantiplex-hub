# Atlantiplex Studio Livestreaming Interface - Visual Reference Guide

## Layout Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ ◈ Atlantiplex Studio  │  LIVE BROADCASTING CONTROL CENTER  │  ● LIVE      │
│                       │  Multi-Participant Livestream Management             │
├──────────────┬────────────────────────────────────┬──────────────┬──────────┤
│              │                                    │              │          │
│ SCENES       │      PREVIEW                       │ GUESTS       │  CHAT    │
│ ──────       │      ────────────────────────────  │ ──────       │  ────    │
│ ◆ Main       │  ┌──────────────────────────────┐  │ ◎ John Doe   │ 14:23    │
│   Camera     │  │  Scene: Main Camera           │  │ ✓ Connected  │ ────────┤
│ (2 sources)  │  │  REC ────────────┐            │  │ 1080p 3Mbps  │ "Great  │
│              │  │                   │ Guest 1    │  │ ☐ Guest 2    │ stream  │
│ ◆ Screen     │  │                   └────────┐  │  │ ✗ Offline    │ setup!" │
│   Share      │  │                   ┌────────┐│  │  │ 720p 2Mbps   │         │
│ (1 source)   │  │                   │Guest 2 ││  │  │              │ 14:25   │
│              │  │                   └────────┘│  │  │ [Invite]     │ ────────┤
│ [+New Scene] │  │                            │  │  │              │ "Will   │
│ [Duplicate]  │  │  [Source Icons]            │  │  │              │ join    │
│              │  └──────────────────────────────┘  │  │              │ soon!"  │
├──────────────┼────────────────────────────────────┼──────────────┼──────────┤
│              │  ⏺ START BROADCAST                 │              │          │
│              │  Scenes: 2  |  Guests: 1          │              │ [Send]   │
│              │  [⚙ Settings] [📊 Analytics]      │              │          │
└──────────────┴────────────────────────────────────┴──────────────┴──────────┘
│  SOURCES & MEDIA                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ 📷 Camera    │  │ 🎙 Microphone│  │ 📺 Screen    │  │ 🎬 Media     │ │
│  │ Video        │  │ Audio        │  │ Video        │  │ Video        │ │
│  │ ● Connected  │  │ ● Connected  │  │ ○ Standby    │  │ ○ Idle       │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘ │
│  [+ Add Source] [Manage Layers]                                          │
└───────────────────────────────────────────────────────────────────────────┘
│ Bitrate: 6.5 Mbps │ Resolution: 1920x1080p60 │ Latency: 2.1ms │ FPS: 60 │ Viewers: 1,234 │
└───────────────────────────────────────────────────────────────────────────┘
```

## Color Palette

### Primary Colors
```
Accent Electric:     #00ff88  (Glowing Cyan-Green)
Accent Cyber:        #00d6ff  (Ocean Blue)
Live Indicator:      #ff0088  (Magenta-Red)
Background Primary:  #0a0b0f  (Deep Dark)
Surface Primary:     #0b2a55  (Atlantean Blue)
```

### Effects
```
Glow (Electric):     0 0 20px rgba(0, 255, 136, 0.6)
Glow (Cyber):        0 0 30px rgba(0, 214, 255, 0.6)
Glow (Live):         0 0 15px rgba(255, 0, 136, 0.8)
Panel Glass:         rgba(11, 42, 85, 0.4) with backdrop blur
```

## Component Anatomy

### Header
```
┌──────────────────────────────────────────────────────────┐
│ ◈ LOGO     Title + Subtitle          Status Indicator ●  │
│            Subtitle                                       │
└──────────────────────────────────────────────────────────┘
 │─────────────────── 1px gradient line ───────────────────│
```

### Scene Item (Active State)
```
┌─ SCENE ITEM (ACTIVE) ─────────────────────────────────┐
│ ┌──────┐  Main Camera              ●                 │
│ │ ◆    │  2 sources                                  │
│ └──────┘                                              │
└────────────────────────────────────────────────────────┘
  Background gradient: Electric green tint
  Glow effect: 0 0 15px rgba(0, 255, 136, 0.3)
```

### Guest Manager Item
```
┌─ GUEST ──────────────────────────────────────────────┐
│ ● John Doe              1080p  3Mbps         ☑       │
│                                                       │
│ ✗ Jane Smith            720p   2Mbps         ☐       │
└───────────────────────────────────────────────────────┘
  ● = Connected (glow), ✗ = Offline (gray)
```

### Chat Message Bubble
```
┌─ CHAT MESSAGE ──────────────────────────────────────┐
│ John Doe ─────────────────────────── 14:23          │
│                                                     │
│ Great broadcast setup! The audio is clear.          │
└─────────────────────────────────────────────────────┘
  Left border: 2px #00ff88
  Animation: Slide in from bottom 0.3s ease-out
```

### Source Card
```
┌─ SOURCE CARD ──────────────────────────────────────┐
│ ┌────┐  Camera           ●                         │
│ │📷  │  Video                                      │
│ └────┘                                             │
└────────────────────────────────────────────────────┘
  ● = Active (glowing #00ff88)
  ○ = Standby (gray)
```

### Stream Control Button

#### Inactive State
```
┌──────────────────────────────────────┐
│  ⏺  START BROADCAST                  │
│                                      │
│  Background: rgba(255, 0, 136, 0.2)  │
│  Border: 2px rgba(255, 0, 136, 0.4)  │
│  Color: #ff0088                      │
└──────────────────────────────────────┘
```

#### Active State (Broadcasting)
```
┌──────────────────────────────────────┐
│  ◾  STOP BROADCAST                   │
│                                      │
│  Background: rgba(255, 0, 136, 0.4)  │
│  Border: 2px rgba(255, 0, 136, 0.8)  │
│  Glow: 0 0 25px rgba(255, 0, 136, 1) │
│  Animation: Pulse 1.5s infinite      │
└──────────────────────────────────────┘
```

## Animation Sequences

### Status Light Pulse (Live Indicator)
```
Cycle 1.5s:
0%    → Box-shadow: 0 0 10px #00ff88, scale: 1
50%   → Box-shadow: 0 0 20px #00ff88, scale: 1.2
100%  → Box-shadow: 0 0 10px #00ff88, scale: 1
```

### Scene Icon Crystalline Pulse
```
Cycle 2s:
0%    → Scale: 1, Rotate: 0°, Opacity: 0.8
50%   → Scale: 1.1, Rotate: 180°, Opacity: 1
100%  → Scale: 1, Rotate: 0°, Opacity: 0.8
```

### Chat Message Slide In
```
Duration: 0.3s ease-out
From:  opacity 0, transform translateY(10px)
To:    opacity 1, transform translateY(0)
```

### Button Shimmer (On Hover)
```
Duration: 0.6s ease
0%    → left: -100%
50%   → left: 50%
100%  → left: 100%
```

## Typography Hierarchy

```
Title (h1):           2rem (32px), weight 700, letter-spacing 1px
Subtitle:             0.875rem (14px), weight 600, uppercase
Panel Header (h3):    0.875rem (14px), weight 700, uppercase
Body Text:            1rem (16px), weight 400
Small Text:           0.75rem (12px), weight 600
Monospace (Metrics):  0.875rem (14px), family JetBrains Mono
```

## Responsive Transformations

### Desktop (1600px+)
```
Columns: [320px] 1fr [320px]
Height: Full viewport minus headers
Guest Grid: 4 tiles (2x2 + overflow)
```

### Tablet (1200px - 1599px)
```
Columns: [280px] 1fr [280px]
Height: Proportional scaling
Guest Grid: 4 tiles (2x2)
Bottom Panel: Full width with flex wrapping
```

### Mobile (< 1200px)
```
Layout: Single column stack
Panels: Sequential vertical
Guest Grid: 2 columns
Bottom Panel: Scrollable horizontal
Header: Compact with hamburger menu ready
```

## Icon System (Atlantean Glyphs)

```
Scenes:        ◆  (Solid Diamond)
Guests:        ◎  (Circle Outline)
Sources:       ◈  (Asterisk Diamond)
Settings:      ⚙  (Gear)
Analytics:     📊 (Chart)
Camera:        📷 (Camera)
Microphone:    🎙  (Microphone)
Screen:        📺 (Screen)
Media:         🎬 (Film)
Status On:     ●  (Solid Circle)
Status Off:    ✗  (X Mark)
```

## Accessibility Features

### High Contrast Mode
```
Text: Maintained 4.5:1+ ratio
Borders: Increased width + contrast
Icons: Alternative text labels ready
Focus: 2px outline with 2px offset
```

### Motion Reduction
```
@media (prefers-reduced-motion: reduce)
  All animations: disabled
  Transitions: instant (0.15s fallback)
  Glows: static
```

### Keyboard Navigation
```
Tab:   Cycle through controls
Enter: Activate buttons
Space: Toggle checkboxes
Esc:   Close modals (future)
```

## Example CSS Classes

### Glowing Element
```css
.neon-glow {
  box-shadow: 0 0 20px rgba(0, 255, 136, 0.5);
  transition: all 0.3s ease;
}

.neon-glow:hover {
  box-shadow: 0 0 40px rgba(0, 255, 136, 0.8);
  transform: scale(1.05);
}
```

### Pulse Animation
```css
@keyframes statusPulse {
  0%, 100% { box-shadow: 0 0 10px #00ff88; }
  50% { box-shadow: 0 0 20px #00ff88; }
}

.status-light {
  animation: statusPulse 1.5s ease-in-out infinite;
}
```

### Glass Panel
```css
.glass-panel {
  background: rgba(11, 42, 85, 0.4);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(0, 255, 136, 0.2);
  border-radius: 12px;
}
```

## State Indicators

### Connection Status
```
Connected (Online):
  Color: #00ff88 (Electric Green)
  Glow: Pulsing 0 0 12px
  Animation: Beat effect

Offline:
  Color: #666 (Gray)
  Glow: None
  Animation: Dim/fade
```

### Stream Status
```
OFFLINE:
  Button: rgba(255, 0, 136, 0.2)
  Text: #999
  Light: Dim, no animation

LIVE:
  Button: rgba(255, 0, 136, 0.4+)
  Text: #ff0088
  Light: Glowing, pulsing 1.5s
  Shadow: 0 0 25px+ rgba(255, 0, 136, 0.8)
```

---

## Practical Implementation Notes

### When Component Mounts
1. Panel fades in (opacity 0→1) 0.5s
2. Scene list loads from backend
3. Guest avatars populate
4. Chat history scrolls into view
5. Preview canvas initializes

### During Live Stream
1. Status light pulses continuously
2. Viewer count updates (real-time)
3. Chat messages animate in
4. Scene indicators glow
5. Bitrate stabilizes

### Responsive Behavior
- **Desktop**: All panels visible, full layout
- **Tablet**: Panels resize, stacking begins
- **Mobile**: Single column, horizontal scroll on bottom panel

---

**Last Updated**: February 2026  
**Design System**: Atlantiplex Crystalline v1.0
