// PDF fetch, poll-after-payment, and browser download helpers.

import { ApiError, getBaseUrl } from "@/src/api/client";
import { STORAGE_KEYS } from "@/src/lib/constants";
import { storage } from "@/src/utils/storage";

export type BlueprintPdfResult =
  | { type: "ready"; blob: Blob }
  | { type: "payment_required" }
  | { type: "error"; status: number; message: string };

const POLL_INTERVAL_MS = 2000;
const POLL_MAX_MS = 30_000;

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function authHeaders(): Promise<Record<string, string>> {
  const token = await storage.secureGet<string>(STORAGE_KEYS.sessionToken, "");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function fetchBlueprintPdf(
  blueprintId: string,
): Promise<BlueprintPdfResult> {
  const url = `${getBaseUrl()}/api/blueprints/${blueprintId}/pdf`;
  const headers = {
    Accept: "application/pdf",
    ...(await authHeaders()),
  };

  let res: Response;
  try {
    res = await fetch(url, { headers });
  } catch (e) {
    throw new ApiError(0, `Network error: ${(e as Error).message}`);
  }

  if (res.status === 200) {
    return { type: "ready", blob: await res.blob() };
  }
  if (res.status === 402) {
    return { type: "payment_required" };
  }

  const text = await res.text();
  let message = res.statusText;
  if (text) {
    try {
      const parsed = JSON.parse(text) as { detail?: unknown };
      if (typeof parsed.detail === "string") {
        message = parsed.detail;
      } else if (parsed.detail !== undefined) {
        message = JSON.stringify(parsed.detail);
      }
    } catch {
      message = text;
    }
  }
  return { type: "error", status: res.status, message };
}

export async function pollUntilPdfReady(
  blueprintId: string,
  onStatus: (message: string) => void,
): Promise<Blob> {
  const deadline = Date.now() + POLL_MAX_MS;
  onStatus("Waiting for payment confirmation...");

  while (Date.now() < deadline) {
    const result = await fetchBlueprintPdf(blueprintId);
    if (result.type === "ready") {
      onStatus("Generating PDF...");
      return result.blob;
    }
    if (result.type === "error") {
      throw new ApiError(result.status, result.message);
    }
    await sleep(POLL_INTERVAL_MS);
  }

  throw new Error(
    "Payment confirmation timed out. Please try downloading again in a moment.",
  );
}

export function downloadPdfBlob(blob: Blob, filename: string): void {
  if (typeof window === "undefined" || typeof document === "undefined") {
    throw new Error("PDF download is only supported on web.");
  }

  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.rel = "noopener";
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}
