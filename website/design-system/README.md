Design System for underwater-ocean robotics UI (Atlantis + Matrix-inspired)

What this is
- A small, reusable React component library (TypeScript typings) with a CSS tokens layer.
- Provides core widgets: Panel, SonarButton, TelemetryChart.
- Includes CSS variables for easy CSS-only usage as well as a TypeScript-friendly API for React apps.

How to use
- In a React project, import components from design-system/src and include design-system/styles.css (or inject tokens.css).
- For CSS-only usage, consume the CSS variables from design-system/tokens.css and apply classes as shown in examples.

Directory
- tokens.json / tokens.ts: token dataset (colors, typography, spacing)
- tokens.css: CSS variables derived from tokens
- src/: React components and TS typings
- styles.css: base resets and font-face declarations (optional)

Note: This is a starter scaffold. You can evolve it into a full design system as your UI grows.
