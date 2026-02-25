import { describe, it, expect } from 'vitest'
import { getBrandLabel } from '../src/branding'

describe('branding tokens', () => {
  it('provides brand name', () => {
    expect(getBrandLabel('brandName')).toBe('Atlantiplex Studio')
  })
})
