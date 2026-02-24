import React from 'react';

type Props = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  label?: string;
};

export const SonarButton: React.FC<Props> = ({ label, children, ...rest }) => {
  return (
    <button aria-label={label ?? 'Pulse'} className="ds-sonar-btn" {...rest}>
      {children ?? '⟲'}
    </button>
  );
};
