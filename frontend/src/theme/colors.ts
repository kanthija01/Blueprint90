// Single source of truth for color tokens. Luxury black + yellow.
// Apple × Nike × Notion aesthetic — high contrast, restrained accent.

export const colors = {
  // Surfaces
  background: "#0B0B0B",
  card: "#141414",
  cardElevated: "#1A1A1A",
  overlay: "rgba(0,0,0,0.6)",

  // Accents
  primary: "#FFD60A",
  primaryPressed: "#F5C518",
  primaryMuted: "rgba(255, 214, 10, 0.16)",

  // Text
  text: "#FFFFFF",
  textMuted: "#A0A0A0",
  textDim: "#6B6B6B",
  textOnPrimary: "#0B0B0B",

  // Borders + lines
  border: "#2A2A2A",
  borderStrong: "#3A3A3A",
  divider: "#1F1F1F",

  // Semantic
  success: "#3DDC84",
  danger: "#FF453A",
  warning: "#FFB020",
} as const;

export type ColorToken = keyof typeof colors;
