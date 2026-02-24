import React, { useEffect, useState } from 'react';

type Mode = 'deep' | 'glow';

export const DarkModeToggle: React.FC = () => {
  const [mode, setMode] = useState<Mode>('deep');

  // Load persisted mode
  useEffect(() => {
    const saved = (typeof window !== 'undefined') ? (localStorage.getItem('ds-theme') as Mode | null) : null;
    const initial = saved ?? 'deep';
    setMode(initial);
    if (typeof document !== 'undefined') {
      document.documentElement.setAttribute('data-ds-theme', initial);
    }
  }, []);

  const toggle = () => {
    const next: Mode = mode === 'deep' ? 'glow' : 'deep';
    setMode(next);
    if (typeof document !== 'undefined') {
      document.documentElement.setAttribute('data-ds-theme', next);
    }
    try {
      localStorage.setItem('ds-theme', next);
    } catch {
      // ignore
    }
  };

  const label = mode === 'deep' ? 'Enable bioluminescent glow' : 'Disable glow';
  return (
    <button aria-label={label} onClick={toggle} className="ds-darkmode-toggle">
      {mode === 'deep' ? '🌊' : '✨'}
    </button>
  );
};
