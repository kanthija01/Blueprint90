// Thin fetch wrapper that injects the bearer token + base URL.
// All API calls in the app go through this.

import { storage } from "@/src/utils/storage";
import { STORAGE_KEYS } from "@/src/lib/constants";

// Single env var — set EXPO_PUBLIC_API_URL in your .env (local) or
// Render / EAS dashboard (production).
const BASE_URL = process.env.EXPO_PUBLIC_API_URL ?? "";

export class ApiError extends Error {
  status: number;
  body: unknown;
  constructor(status: number, message: string, body?: unknown) {
    super(message);
    this.status = status;
    this.body = body;
  }
}

type RequestOptions = {
  method?: "GET" | "POST" | "PUT" | "DELETE";
  body?: unknown;
  // If true, no Authorization header is sent (used for /auth/session).
  unauthenticated?: boolean;
  // Optional explicit token override (used during the login handshake).
  tokenOverride?: string | null;
};

async function getToken(): Promise<string | null> {
  return storage.secureGet<string>(STORAGE_KEYS.sessionToken, "");
}

export async function apiRequest<T>(
  path: string,
  opts: RequestOptions = {},
): Promise<T> {
  const url = `${BASE_URL}${path.startsWith("/") ? "" : "/"}${path}`;
  console.log("[auth] apiRequest", opts.method ?? "GET", url);

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    Accept: "application/json",
  };
  if (!opts.unauthenticated) {
    const token =
      opts.tokenOverride !== undefined ? opts.tokenOverride : await getToken();
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
  }

  let res: Response;
  try {
    res = await fetch(url, {
      method: opts.method ?? "GET",
      headers,
      body: opts.body !== undefined ? JSON.stringify(opts.body) : undefined,
    });
  } catch (e) {
    throw new ApiError(0, `Network error: ${(e as Error).message}`);
  }

  const text = await res.text();
  let parsed: unknown = null;
  if (text) {
    try {
      parsed = JSON.parse(text);
    } catch {
      parsed = text;
    }
  }

  if (!res.ok) {
    const detail =
      (parsed && typeof parsed === "object" && "detail" in parsed
        ? (parsed as { detail: unknown }).detail
        : undefined) ?? res.statusText;
    const message =
      typeof detail === "string" ? detail : JSON.stringify(detail);
    console.log("[auth] apiRequest failed", res.status, url, message);
    throw new ApiError(res.status, message, parsed);
  }

  return parsed as T;
}

export function getBaseUrl(): string {
  return BASE_URL;
}
