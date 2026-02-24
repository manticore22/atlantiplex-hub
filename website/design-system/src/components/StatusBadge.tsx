import React from 'react';

type Props = {
  status: 'ok' | 'info' | 'warn' | 'error';
  label?: string;
  className?: string;
};

export const StatusBadge: React.FC<Props> = ({ status, label, className }) => {
  const text = label ?? status.toUpperCase();
  return (
    <span className={`ds-status-badge ds-${status} ${className ?? ''}`} role="status" aria-label={text}>
      {text}
    </span>
  );
};
