// Auth API — wraps the Phase 3 routes.

import { apiRequest } from "./client";

export type UserPublic = {
  user_id: string;
  email: string;
  name: string | null;
  picture: string | null;
};

export type SessionExchangeResponse = {
  session_token: string;
  user: UserPublic;
};

export function exchangeSession(
  sessionId: string,
): Promise<SessionExchangeResponse> {
  return apiRequest<SessionExchangeResponse>("/api/auth/session", {
    method: "POST",
    body: { session_id: sessionId },
    unauthenticated: true,
  });
}

export function getMe(tokenOverride?: string): Promise<UserPublic> {
  return apiRequest<UserPublic>("/api/auth/me", { tokenOverride });
}

export function logout(): Promise<{ success: boolean }> {
  return apiRequest<{ success: boolean }>("/api/auth/logout", {
    method: "POST",
  });
}
