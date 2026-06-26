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
const WEB_SESSION_STORAGE_KEY = "bp90.oauth_session_id";

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
  // Supports ?session_id=, #session_id=, hash routes with ?session_id=, sessionId alias.
  try {
    const parsed = new URL(url);
    const fromQuery =
      parsed.searchParams.get("session_id") ??
      parsed.searchParams.get("sessionId");
    if (fromQuery) return fromQuery;

    const hash = parsed.hash.startsWith("#") ? parsed.hash.slice(1) : parsed.hash;
    if (hash) {
      const hashQueryStart = hash.indexOf("?");
      const hashPart = hashQueryStart >= 0 ? hash.slice(hashQueryStart + 1) : hash;
      const hashParams = new URLSearchParams(hashPart);
      const fromHash =
        hashParams.get("session_id") ?? hashParams.get("sessionId");
      if (fromHash) return fromHash;
    }
  } catch {
    // fall through to legacy parser
  }

  try {
    const hashIdx = url.indexOf("#");
    const qIdx = url.indexOf("?");
    const fragments: string[] = [];
    if (hashIdx >= 0) fragments.push(url.slice(hashIdx + 1));
    if (qIdx >= 0)
      fragments.push(url.slice(qIdx + 1, hashIdx >= 0 ? hashIdx : undefined));
    for (const frag of fragments) {
      const params = new URLSearchParams(frag);
      const sid = params.get("session_id") ?? params.get("sessionId");
      if (sid) return sid;
    }
  } catch {
    // fall through
  }
  return null;
}

function readWebSessionStorage(): string | null {
  if (Platform.OS !== "web") return null;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const w = (globalThis as any).window;
  if (!w?.sessionStorage) return null;
  const sid = w.sessionStorage.getItem(WEB_SESSION_STORAGE_KEY);
  if (sid) {
    w.sessionStorage.removeItem(WEB_SESSION_STORAGE_KEY);
  }
  return sid;
}

function stashWebSessionId(sessionId: string): void {
  if (Platform.OS !== "web") return;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const w = (globalThis as any).window;
  w?.sessionStorage?.setItem(WEB_SESSION_STORAGE_KEY, sessionId);
}

function cleanWebUrlBar(): void {
  if (Platform.OS !== "web") return;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const w = (globalThis as any).window;
  if (!w?.location || !w.history) return;
  w.history.replaceState(null, "", w.location.pathname);
}

/**
 * Capture session_id as early as possible on web (before expo-router strips
 * query params). Called from root layout module init.
 */
export function captureWebOAuthSession(): void {
  if (Platform.OS !== "web") return;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const w = (globalThis as any).window;
  if (!w?.location) return;

  const href = w.location.href as string;
  const sid = parseSessionId(href);
  console.log("[auth] captureWebOAuthSession href:", href);
  console.log("[auth] captureWebOAuthSession session_id:", sid ? `${sid.slice(0, 8)}…` : "none");
  if (sid) {
    stashWebSessionId(sid);
    cleanWebUrlBar();
  }
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
  console.log("[auth] startGoogleSignIn redirectUrl:", redirectUrl);

  if (Platform.OS === "web") {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const w = (globalThis as any).window;
    if (w) {
      w.location.href = authUrl;
    }
    return null;
  }

  const result = await WebBrowser.openAuthSessionAsync(authUrl, redirectUrl);
  console.log("[auth] startGoogleSignIn mobile result:", result.type);
  if (result.type !== "success" || !result.url) return null;
  const sid = parseSessionId(result.url);
  console.log("[auth] startGoogleSignIn mobile session_id:", sid ? `${sid.slice(0, 8)}…` : "none");
  return sid;
}

/**
 * On web only: read the session_id off sessionStorage (stashed before React)
 * or the current URL (hash or query), clean the URL bar, and return it.
 */
export function readWebSessionIdFromUrl(): string | null {
  if (Platform.OS !== "web") return null;

  const fromStorage = readWebSessionStorage();
  if (fromStorage) {
    console.log("[auth] readWebSessionIdFromUrl from sessionStorage:", `${fromStorage.slice(0, 8)}…`);
    return fromStorage;
  }

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const w = (globalThis as any).window;
  if (!w?.location) return null;
  const url = w.location.href as string;
  const sid = parseSessionId(url);
  console.log("[auth] readWebSessionIdFromUrl from url:", url, "→", sid ? `${sid.slice(0, 8)}…` : "none");
  if (sid) {
    cleanWebUrlBar();
  }
  return sid;
}

/** Cold-start fallback for mobile: check deep-link initial URL. */
export async function readInitialDeepLinkSessionId(): Promise<string | null> {
  if (Platform.OS === "web") return null;
  const initial = await Linking.getInitialURL();
  console.log("[auth] readInitialDeepLinkSessionId url:", initial ?? "none");
  if (!initial) return null;
  const sid = parseSessionId(initial);
  console.log("[auth] readInitialDeepLinkSessionId session_id:", sid ? `${sid.slice(0, 8)}…` : "none");
  return sid;
}

// Capture on module load — earliest point this file is imported.
captureWebOAuthSession();
