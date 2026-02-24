# Tone Guide: Seraphonix Language (Non-Literal, Theme-Only)

- Goal: apply a consistent, elevated tone across UI copy without becoming a literal voice script.
- Pillars: mythic ritual, neon cyberpunk, abyssal-technical, classified‑AI. Use the vocabulary of gateways, glyphs, sigils, and trench-core terminology.
- Voice style:
  - Authority and mystery; avoid casual phrasing.
  - Use vivid, concise phrases that imply depth and mechanism.
  - Favor nouns/verbs that imply action in a system or ritual (e.g., Ascend, Gate, Seal, Align, Render).
- Tone mapping for common UI elements:
  - Headers: succinct, elevated, frame the concept as a gateway or ritual.
  - CTAs: imperative but ceremonial (Ascend, Engage, Seal, Validate).
  - Tooltips: hint with a glyph-like flavor (glyph flicker, sigil glow).
  - Loading: describe a process (pressure equalization, path weaving).
  - Errors: containment warning with specific, actionable next steps.
- Examples (before -> after):
  - "Loading" -> "Pressure equalization in progress. Seals reweave." 
  - "Submit" -> "Seal the sigil" 
  - "Error" -> "Containment breach. Restore integrity to regain access." 
- Implementation notes: keep a single source of truth for tone tokens, then apply across components via text props or centralized strings.
