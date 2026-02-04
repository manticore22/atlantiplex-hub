// Verily Hub branding token definitions (Phase 1)
export const VERILY_BRAND = {
  brandName: 'Verily',
  studioTabLabel: 'Verily Hub',
  stageLabel: 'Verily Hub MEI',
  palette: {
    primary: '#3bd',
    accent: '#5df',
    bg: '#0a0a0a',
    surface: '#1a1a1a',
    text: '#e6f6ff',
    fontFamily: 'Inter, sans-serif',
  },
  logoPath: '/static/verily-logo.svg',
  faviconPath: '/static/favicon.ico',
  iceServers: [],
  turnServers: [],
}

export function getVerilyBrandLabel(key) {
  return VERILY_BRAND[key] ?? ''
}

export default VERILY_BRAND
