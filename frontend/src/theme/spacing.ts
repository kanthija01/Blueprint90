// 8pt grid. Always reference this — do not introduce arbitrary pixel values.

export const spacing = {
  xs: 4,
  sm: 8,
  md: 12,
  lg: 16,
  xl: 24,
  xxl: 32,
  xxxl: 48,
  huge: 64,
} as const;

export const radius = {
  sm: 8,
  md: 12,
  lg: 16,
  xl: 20,
  pill: 999,
} as const;

export const hitSlop = { top: 8, right: 8, bottom: 8, left: 8 } as const;

// Minimum touch target per platform guidelines.
export const minTouchTarget = 48;
