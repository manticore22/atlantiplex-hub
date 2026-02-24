import React from 'react';

type PanelProps = {
  title?: string;
  className?: string;
  children?: React.ReactNode;
};

export const Panel: React.FC<PanelProps> = ({ title, className, children }) => {
  return (
    <section className={`ds-panel ${className ?? ''}`} aria-label={title ?? 'Panel'}>
      {title ? <h3 className="ds-panel-title">{title}</h3> : null}
      <div className="ds-panel-content">{children}</div>
    </section>
  );
};
