// Atlantiplex Studio branding module with Verily Hub support (Phase 1)

const ATL_BRAND = {
  brandName: 'Atlantiplex Lightning Studio',
  studioTabLabel: 'Atlantiplex Lightning Studio - Broadcast Platform',
  stageLabel: 'Metacommunication Entanglement Interface (MEI)',
  palette: {
    primary: '#1e3c72',
    accent: '#ffeb3b',
    secondary: '#2a5298',
    bg: '#0a0f1b',
    surface: '#1a2942',
    surfaceElevated: '#243351',
    text: '#eaf6ff',
    textSecondary: '#b8c5d6',
    glow: '0 0 20px rgba(255, 235, 59, 0.4)',
    glowAccent: '0 0 30px rgba(30, 60, 114, 0.6)',
    fontFamily: "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
    fontWeight: '400',
    borderRadius: '12px',
    shadow: '0 4px 20px rgba(0, 0, 0, 0.3)',
    shadowElevated: '0 8px 40px rgba(30, 60, 114, 0.2)',
  },
  logoPath: '/static/atlantiplex-lightning-logo.svg',
  logoPathSmall: '/static/atlantiplex-lightning-logo-small.svg',
  logoPathTiny: '/static/atlantiplex-lightning-logo-tiny.svg',
  faviconPath: '/static/favicon.ico',
  iceServers: [ { urls: ['stun:stun.l.google.com:19302'] } ],
  turnServers: [],
}

const VERILY_BRAND = {
  brandName: 'Verily',
  studioTabLabel: 'Verily Hub',
  stageLabel: 'Verily Hub MEI',
  palette: {
    primary: '#3bd',
    accent: '#5df',
    bg: '#0a0a0a',
    surface: '#1a1a1a',
    text: '#e6f6ff',
    glow: '0 0 12px rgba(0, 255, 255, 0.8)',
    fontFamily: 'Inter, sans-serif',
  },
  logoPath: '/static/verily-logo.svg',
  faviconPath: '/static/favicon.ico',
  iceServers: [],
  turnServers: [],
}

const BRANDS = {
  AtlantiplexStudio: ATL_BRAND,
  VerilyHub: VERILY_BRAND,
}

function activeBrand() {
  if (typeof window !== 'undefined') {
    const b = new URLSearchParams(window.location.search).get('branding') || new URLSearchParams(window.location.search).get('hub')
    if (b && b.toLowerCase() === 'verily') return VERILY_BRAND
  }
  return ATL_BRAND
}

export function getBrandLabel(key) { return activeBrand()[key] ?? '' }
export const getPalette = () => activeBrand().palette
export const getLogoPath = () => activeBrand().logoPath
export const getLogoPathSmall = () => activeBrand().logoPathSmall || activeBrand().logoPath
export const getLogoPathTiny = () => activeBrand().logoPathTiny || activeBrand().logoPath
export const getFontFamily = () => activeBrand().palette.fontFamily
export const getBrandName = () => activeBrand().brandName
export const getStudioTabLabel = () => activeBrand().studioTabLabel
export const getStageLabel = () => activeBrand().stageLabel
export const getIceServers = () => activeBrand().iceServers
export const getTurnServers = () => activeBrand().turnServers
export default activeBrand
