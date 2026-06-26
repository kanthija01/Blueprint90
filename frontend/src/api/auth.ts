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
  console.log("[auth] exchangeSession request, session_id:", `${sessionId.slice(0, 8)}…`);
  return apiRequest<SessionExchangeResponse>("/api/auth/session", {
    method: "POST",
    body: { session_id: sessionId },
    unauthenticated: true,
  }).then((res) => {
    console.log("[auth] exchangeSession response OK, user:", res.user.user_id);
    return res;
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
