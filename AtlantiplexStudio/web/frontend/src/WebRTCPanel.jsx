import React from 'react'
import { getPalette, getFontFamily, getIceServers } from './branding.ts'

/**
 * Simple WebRTC peer panel for audio/video with Atlantiplex branding
 */
function createPeerConnection(isInitiator, signaling, iceServers) {
  const pc = new RTCPeerConnection({
    iceServers: (iceServers && iceServers.length) ? iceServers : [{ urls: 'stun:stun.l.google.com:19302' }],
  })
  // Add local audio/video tracks (simplified demo; replace with real media)
  ;(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true, video: true })
      stream.getTracks().forEach(track => pc.addTrack(track, stream))
    } catch (err) {
      console.warn('Media access denied or unavailable', err)
    }
  })()
  // Exchange ICE candidates
  pc.onicecandidate = ({ candidate }) => {
    if (candidate) {
      signaling.emit('ice-candidate', { candidate })
    }
  }
  // Remote stream handler
  pc.ontrack = ({ streams }) => {
    const [remoteStream] = streams
    // Attach remoteStream to a <video> element if needed
  }
  if (isInitiator) {
    ;(async () => {
      const offer = await pc.createOffer()
      await pc.setLocalDescription(offer)
      signaling.emit('offer', { offer })
    })()
  }
  // Handle remote offers/answers
  signaling.on('offer', ({ offer }) => {
    if (!isInitiator) {
      ;(async () => {
        await pc.setRemoteDescription(new RTCSessionDescription(offer))
        const answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)
        signaling.emit('answer', { answer })
      })()
    }
  })
  signaling.on('answer', ({ answer }) => {
    if (isInitiator) {
      ;(async () => {
        await pc.setRemoteDescription(new RTCSessionDescription(answer))
      })()
    }
  })
  signaling.on('ice-candidate', ({ candidate }) => {
    ;(async () => {
      await pc.addIceCandidate(new RTCIceCandidate(candidate))
    })()
  })
  return pc
}

export default function WebRTCPanel({ peerId, signaling }) {
  const palette = getPalette()
  const [pc, setPc] = React.useState(null)
  React.useEffect(() => {
    const isInitiator = peerId === 'initiator'
    const iceServers = getIceServers() || []
    const connection = createPeerConnection(isInitiator, signaling, iceServers)
    setPc(connection)
    return () => {
      connection.close()
    }
  }, [peerId, signaling])
  return (
    <div
      style={{
        background: `${palette.bg}`,
        borderRadius: 4,
        marginTop: 6,
        height: 100,
        position: 'relative',
        border: `1px solid ${palette.accent}`,
      }}
    >
      <video
        autoPlay
        playsInline
        muted
        style={{
          width: '100%',
          height: '100%',
          objectFit: 'cover',
          borderRadius: 4,
          fontFamily: getFontFamily(),
        }}
        aria-label={`Peer video for ${peerId}`}
      />
    </div>
  )
}
