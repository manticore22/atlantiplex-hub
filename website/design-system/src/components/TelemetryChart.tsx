import React from 'react';

type Props = {
  data?: number[];
  width?: number;
  height?: number;
};

export const TelemetryChart: React.FC<Props> = ({ data = [0, 0.3, 0.6, 0.2, 0.9], width = 240, height = 80 }) => {
  const n = Math.max(2, data.length);
  const pts = data.map((v, i) => {
    const x = (i / (n - 1)) * width;
    const y = height - v * height;
    return `${x},${y}`;
  }).join(' ');

  return (
    <svg className="ds-telemetry" width={width} height={height} viewBox={`0 0 ${width} ${height}`} aria-label="Telemetry chart">
      <polyline fill="none" stroke="var(--accent)" strokeWidth={2} points={pts} />
      <g stroke="var(--grid)" opacity={0.5}>
        {/* simple grid lines for depth feel */}
        <line x1={0} y1={0} x2={width} y2={0} />
        <line x1={0} y1={height} x2={width} y2={height} />
      </g>
    </svg>
  );
};
