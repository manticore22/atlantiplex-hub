import React from 'react';
import { render } from '@testing-library/react';
import { TelemetryChart } from '../src/components/TelemetryChart';

describe('TelemetryChart', () => {
  test('renders without crashing', () => {
    const { container } = render(<TelemetryChart data={[0.1,0.4,0.8]} />);
    expect(container).toBeTruthy();
  });
});
