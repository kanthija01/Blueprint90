// Emergent Google sign-in handshake. Encapsulates the platform-specific
// glue documented in the integration playbook:
//   * mobile: WebBrowser.openAuthSessionAsync + result.url parsing
//   * web:    window.location redirect + URL parsing on app mount
// The result is a one-time `session_id` that we hand to the backend's
// /api/auth/session endpoint.

import { Platform } from "react-native";
import * as Linking from "expo-linking";
import * as WebBrowser from "expo-web-browser";

const EMERGENT_AUTH_URL = "https://auth.emergentagent.com/";

WebBrowser.maybeCompleteAuthSession();

function getRedirectUrl(): string {
  if (Platform.OS === "web") {
    // Must be an existing route on web.
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const w = (globalThis as any).window;
    return w ? `${w.location.origin}/` : "/";
  }
  return Linking.createURL("auth");
}

function parseSessionId(url: string): string | null {
  // Supports both `#session_id=...` and `?session_id=...`.
  try {
    const hashIdx = url.indexOf("#");
    const qIdx = url.indexOf("?");
    const fragments: string[] = [];
    if (hashIdx >= 0) fragments.push(url.slice(hashIdx + 1));
    if (qIdx >= 0) fragments.push(url.slice(qIdx + 1, hashIdx >= 0 ? hashIdx : undefined));
    for (const frag of fragments) {
      const params = new URLSearchParams(frag);
      const sid = params.get("session_id");
      if (sid) return sid;
    }
  } catch {
    // fall through
  }
  return null;
}

/**
 * Launch the Google sign-in flow.
 * Mobile: returns the session_id from the openAuthSessionAsync result.
 * Web: navigates to Emergent's auth UI — returns null (caller should not
 *      treat this as failure; the redirect handler picks up the session_id
 *      on mount).
 */
export async function startGoogleSignIn(): Promise<string | null> {
  const redirectUrl = getRedirectUrl();
  const authUrl = `${EMERGENT_AUTH_URL}?redirect=${encodeURIComponent(redirectUrl)}`;

  if (Platform.OS === "web") {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const w = (globalThis as any).window;
    if (w) {
      w.location.href = authUrl;
    }
    return null;
  }

  const result = await WebBrowser.openAuthSessionAsync(authUrl, redirectUrl);
  if (result.type !== "success" || !result.url) return null;
  return parseSessionId(result.url);
}

/**
 * On web only: read the session_id off the current URL (hash or query),
 * clean it from the URL bar, and return it. Returns null otherwise.
 */
export function readWebSessionIdFromUrl(): string | null {
  if (Platform.OS !== "web") return null;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const w = (globalThis as any).window;
  if (!w?.location) return null;
  const url = w.location.href as string;
  const sid = parseSessionId(url);
  if (sid) {
    w.history.replaceState(null, "", w.location.pathname);
  }
  return sid;
}

/** Cold-start fallback for mobile: check deep-link initial URL. */
export async function readInitialDeepLinkSessionId(): Promise<string | null> {
  if (Platform.OS === "web") return null;
  const initial = await Linking.getInitialURL();
  if (!initial) return null;
  return parseSessionId(initial);
}
