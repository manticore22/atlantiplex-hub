#!/usr/bin/env node
/*
  Build CSS tokens from design-tokens.json to tokens.css
  This keeps a single source of truth for design tokens across the project.
*/
const fs = require('fs');
const path = require('path');

const tokensPath = path.resolve(__dirname, '../design-tokens.json');
const outPath = path.resolve(__dirname, '../tokens.css'); // design-system/tokens.css

function emitSectionHeader(lines, key) {
  lines.push(`:root {`);
}

function indent(lines, level = 1) {
  return lines.map(l => '  '.repeat(level) + l);
}

function toPx(n) {
  if (typeof n === 'number') return `${n}px`;
  return n;
}

function main() {
  const data = JSON.parse(fs.readFileSync(tokensPath, 'utf8'));
  const lines = [];
  lines.push(':root {');

  // Colors
  if (data.color) {
    const c = data.color;
    Object.keys(c).forEach(k => {
      lines.push(`  --ds-${k}: ${c[k]};`);
    });
  }

  // Background/text if not included in color (fallbacks)
  // (Assuming color.bg and color.text exist and are mapped above.)

  // Spacing
  if (data.spacing) {
    Object.entries(data.spacing).forEach(([k, v]) => {
      lines.push(`  --ds-space-${k}: ${toPx(v)};`);
    });
  }

  // Motion
  if (data.motion) {
    const m = data.motion;
    if (m.durations) {
      Object.entries(m.durations).forEach(([k, v]) => {
        lines.push(`  --ds-duration-${k}: ${v}ms;`);
      });
    }
    if (m.easing) {
      Object.entries(m.easing).forEach(([k, v]) => {
        const name = k === 'ease' ? 'ease' : `ease-${k}`;
        lines.push(`  --ds-${name}: ${v};`);
      });
    }
  }

  // Typography
  if (data.typography) {
    const t = data.typography;
    if (t.fontFamily) {
      if (t.fontFamily.display) lines.push(`  --ds-font-display: ${t.fontFamily.display};`);
      if (t.fontFamily.body) lines.push(`  --ds-font-body: ${t.fontFamily.body};`);
      if (t.fontFamily.monospace) lines.push(`  --ds-font-mono: ${t.fontFamily.monospace};`);
    }
    if (t.fontSizes) {
      Object.entries(t.fontSizes).forEach(([k, v]) => {
        lines.push(`  --ds-font-size-${k}: ${v}px;`);
      });
    }
    if (t.fontWeights) {
      if (t.fontWeights.regular != null) lines.push(`  --ds-font-weight-regular: ${t.fontWeights.regular};`);
      if (t.fontWeights.semibold != null) lines.push(`  --ds-font-weight-semibold: ${t.fontWeights.semibold};`);
      if (t.fontWeights.bold != null) lines.push(`  --ds-font-weight-bold: ${t.fontWeights.bold};`);
    }
    if (t.lineHeight) {
      Object.entries(t.lineHeight).forEach(([k, v]) => {
        const name = k === 'normal' ? 'normal' : k;
        lines.push(`  --ds-line-height-${name}: ${v};`);
      });
    }
  }

  // Layout
  if (data.layout) {
    if (data.layout.maxW) lines.push(`  --ds-max: ${data.layout.maxW};`);
    if (data.layout.radius != null) lines.push(`  --ds-radius: ${data.layout.radius}px;`);
    if (data.layout.spacing) {
      Object.entries(data.layout.spacing).forEach(([k, v]) => {
        lines.push(`  --ds-layout-spacing-${k}: ${toPx(v)};`);
      });
    }
  }

  // Breakpoints
  if (data.breakpoints) {
    Object.entries(data.breakpoints).forEach(([k, v]) => {
      lines.push(`  --ds-breakpoint-${k}: ${v}px;`);
    });
  }

  // Shadow
  if (data.shadow && data.shadow.soft) {
    lines.push(`  --ds-shadow-soft: ${data.shadow.soft};`);
  }

  // Close root
  lines.push('}');

  // Write
  fs.writeFileSync(outPath, lines.join('\n') + '\n', 'utf8');
  console.log(`Tokens CSS generated at ${outPath}`);
}

try {
  main();
} catch (err) {
  console.error('Error generating tokens.css:', err);
  process.exit(1);
}
