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
    const token = await storage.secureGet<string>(
      STORAGE_KEYS.sessionToken,
      "",
    );
    if (!token) {
      set({ status: "unauthenticated", user: null, token: null });
      return;
    }
    try {
      const user = await authApi.getMe(token);
      set({ status: "authenticated", user, token });
    } catch {
      await storage.secureRemove(STORAGE_KEYS.sessionToken);
      set({ status: "unauthenticated", user: null, token: null });
    }
  },

  loginWithSessionId: async (sessionId) => {
    set({ error: null });
    try {
      const { session_token, user } = await authApi.exchangeSession(sessionId);
      await storage.secureSet(STORAGE_KEYS.sessionToken, session_token);
      set({ status: "authenticated", user, token: session_token });
    } catch (e) {
      set({ error: (e as Error).message });
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
