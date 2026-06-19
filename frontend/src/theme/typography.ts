// Type ramp. Apple-inspired: large display headlines, tight kerning.
// React Native uses the platform's default sans-serif when fontFamily is
// undefined, which is exactly what we want — no need to import Platform here,
// keeping this module pure / Node-testable.

// Local shape so this module stays react-native-free at the type layer too.
// (RN's TextStyle is structurally a superset of what we declare.)
type TextVariant = {
  fontSize: number;
  lineHeight?: number;
  fontWeight?:
    | "100" | "200" | "300" | "400" | "500" | "600" | "700" | "800" | "900";
  letterSpacing?: number;
  textTransform?: "none" | "uppercase" | "lowercase" | "capitalize";
};

export const typography = {
  // Hero / landing
  display: {
    fontSize: 44,
    lineHeight: 50,
    fontWeight: "800" as const,
    letterSpacing: -1.2,
  } satisfies TextVariant,

  // Screen titles
  h1: {
    fontSize: 32,
    lineHeight: 38,
    fontWeight: "800" as const,
    letterSpacing: -0.8,
  } satisfies TextVariant,

  h2: {
    fontSize: 24,
    lineHeight: 30,
    fontWeight: "700" as const,
    letterSpacing: -0.4,
  } satisfies TextVariant,

  h3: {
    fontSize: 18,
    lineHeight: 24,
    fontWeight: "700" as const,
    letterSpacing: -0.2,
  } satisfies TextVariant,

  body: {
    fontSize: 16,
    lineHeight: 24,
    fontWeight: "400" as const,
  } satisfies TextVariant,

  bodyStrong: {
    fontSize: 16,
    lineHeight: 24,
    fontWeight: "600" as const,
  } satisfies TextVariant,

  caption: {
    fontSize: 13,
    lineHeight: 18,
    fontWeight: "500" as const,
    letterSpacing: 0.1,
  } satisfies TextVariant,

  // ALL CAPS micro-label (Nike-ish accent label)
  overline: {
    fontSize: 11,
    lineHeight: 14,
    fontWeight: "700" as const,
    letterSpacing: 1.6,
    textTransform: "uppercase" as const,
  } satisfies TextVariant,

  button: {
    fontSize: 16,
    lineHeight: 20,
    fontWeight: "700" as const,
    letterSpacing: 0.2,
  } satisfies TextVariant,
} as const;

export type TypographyVariant = keyof typeof typography;
