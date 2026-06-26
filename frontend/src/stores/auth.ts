// Auth store — Zustand. Bootstraps from secure storage on app mount.

import { create } from "zustand";

import * as authApi from "@/src/api/auth";
import { STORAGE_KEYS } from "@/src/lib/constants";
import { storage } from "@/src/utils/storage";

type AuthState = {
  user: authApi.UserPublic | null;
  token: string | null;
  status: "booting" | "unauthenticated" | "authenticated";
  error: string | null;
  // actions
  bootstrap: () => Promise<void>;
  loginWithSessionId: (sessionId: string) => Promise<void>;
  logout: () => Promise<void>;
  clearError: () => void;
};

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  token: null,
  status: "booting",
  error: null,

  bootstrap: async () => {
    console.log("[auth] bootstrap() start");
    const token = await storage.secureGet<string>(
      STORAGE_KEYS.sessionToken,
      "",
    );
    console.log(
      "[auth] bootstrap() token from storage:",
      token ? "present" : "missing",
    );
    if (!token) {
      set((state) => {
        if (state.status === "authenticated") {
          console.log(
            "[auth] bootstrap() no token in storage but already authenticated — keeping session",
          );
          return state;
        }
        console.log("[auth] bootstrap() → unauthenticated (no token)");
        return { status: "unauthenticated", user: null, token: null };
      });
      return;
    }
    try {
      const user = await authApi.getMe(token);
      console.log("[auth] bootstrap() getMe OK:", user.user_id);
      set({ status: "authenticated", user, token });
    } catch (e) {
      console.log("[auth] bootstrap() getMe failed:", (e as Error).message);
      const current = get();
      if (current.status === "authenticated" && current.token === token) {
        console.log(
          "[auth] bootstrap() getMe failed but login already validated token — keeping session",
        );
        return;
      }
      await storage.secureRemove(STORAGE_KEYS.sessionToken);
      set({ status: "unauthenticated", user: null, token: null });
      console.log("[auth] bootstrap() → unauthenticated (getMe failed)");
    }
  },

  loginWithSessionId: async (sessionId) => {
    console.log("[auth] loginWithSessionId() start, session_id:", `${sessionId.slice(0, 8)}…`);
    set({ error: null });
    try {
      const { session_token, user } = await authApi.exchangeSession(sessionId);
      console.log("[auth] exchangeSession OK, user:", user.user_id);
      const stored = await storage.secureSet(
        STORAGE_KEYS.sessionToken,
        session_token,
      );
      console.log("[auth] token stored:", stored);
      set({ status: "authenticated", user, token: session_token });
      console.log("[auth] status → authenticated");
    } catch (e) {
      console.log("[auth] loginWithSessionId() failed:", (e as Error).message);
      set({ status: "unauthenticated", error: (e as Error).message });
      throw e;
    }
  },

  logout: async () => {
    try {
      if (get().token) {
        await authApi.logout();
      }
    } catch {
      // ignore — we still want to log out locally
    }
    await storage.secureRemove(STORAGE_KEYS.sessionToken);
    set({ status: "unauthenticated", user: null, token: null });
  },

  clearError: () => set({ error: null }),
}));
