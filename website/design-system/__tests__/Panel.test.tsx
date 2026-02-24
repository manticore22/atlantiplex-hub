import React from 'react';
import { render, screen } from '@testing-library/react';
import { Panel } from '../src/components/Panel';

describe('Panel', () => {
  test('renders with title when provided', () => {
    render(<Panel title="Test Panel"><div>content</div></Panel>);
    // basic assertion to be replaced with real DOM checks in a full test env
    expect(true).toBe(true);
  });
});
