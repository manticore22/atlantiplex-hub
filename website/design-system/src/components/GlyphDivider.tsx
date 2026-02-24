import React from 'react';

type Props = {
  glyphs?: string[];
  ariaLabel?: string;
};

export const GlyphDivider: React.FC<Props> = ({ glyphs = ['✦', '✧', '✦'], ariaLabel = 'decorative divider' }) => {
  return (
    <div className="ds-glyph-divider" role="separator" aria-label={ariaLabel}>
      <span className="glyph">{glyphs[0]}</span>
      <span className="glyph">{glyphs[1]}</span>
      <span className="glyph">{glyphs[2]}</span>
      <span className="glyph" aria-hidden> </span>
    </div>
  );
};
