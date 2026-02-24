import React from 'react';

type Props = {
  icon?: React.ReactNode;
  primary: string;
  secondary?: string;
  trailing?: React.ReactNode;
  onClick?: () => void;
};

export const ListRow: React.FC<Props> = ({ icon, primary, secondary, trailing, onClick }) => {
  return (
    <div className="ds-list-row" role="listitem" tabIndex={0} onClick={onClick} aria-label={primary}>
      <div className="ds-list-row-left">
        {icon ? <span className="ds-icon" aria-hidden>{icon}</span> : null}
        <span className="ds-primary">{primary}</span>
        {secondary ? <span className="ds-secondary">{secondary}</span> : null}
      </div>
      <div className="ds-list-row-right">{trailing ?? null}</div>
    </div>
  );
};
