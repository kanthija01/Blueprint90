// Orchestrates paid PDF download for the legacy flow (blueprint already exists).
// Flow: fetch PDF → if 402 → create order → Razorpay checkout →
//       verify payment (client-side HMAC check) → poll until paid → download.

import { useCallback, useState } from "react";
import { Platform } from "react-native";

import { ApiError } from "@/src/api/client";
import { createOrder, verifyPayment } from "@/src/api/payments";
import {
  downloadPdfBlob,
  fetchBlueprintPdf,
  pollUntilPdfReady,
} from "@/src/lib/blueprint-pdf";
import { loadRazorpayScript, openRazorpayCheckout } from "@/src/lib/razorpay-checkout";

export function useBlueprintPdfDownload(blueprintId: string | undefined) {
  const [status, setStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const download = useCallback(async () => {
    if (!blueprintId) return;

    setError(null);

    try {
      setStatus("Downloading PDF...");
      const initial = await fetchBlueprintPdf(blueprintId);

      if (initial.type === "ready") {
        if (Platform.OS !== "web") {
          throw new Error("PDF download is available on the website.");
        }
        downloadPdfBlob(initial.blob, `blueprint-${blueprintId}.pdf`);
        return;
      }

      if (initial.type === "error") {
        throw new ApiError(initial.status, initial.message);
      }

      if (Platform.OS !== "web") {
        throw new Error(
          "PDF purchase is available on the website. Viewing your blueprint here is free.",
        );
      }

      // Create a Razorpay order for this blueprint.
      setStatus("Preparing payment...");
      let order;
      try {
        order = await createOrder(blueprintId);
      } catch (e) {
        if (e instanceof ApiError && e.status === 409) {
          // Already paid — retry the PDF fetch directly.
          const retry = await fetchBlueprintPdf(blueprintId);
          if (retry.type === "ready") {
            setStatus("Downloading PDF...");
            downloadPdfBlob(retry.blob, `blueprint-${blueprintId}.pdf`);
            return;
          }
        }
        throw e;
      }

      // Open Razorpay checkout — resolves with callback params on success.
      await loadRazorpayScript();
      const rzResult = await openRazorpayCheckout(order);

      // Verify the payment using the client-side callback params.
      // This marks status="paid" in MongoDB without needing a public webhook.
      setStatus("Verifying payment...");
      try {
        await verifyPayment({
          payment_id: order.payment_id,
          razorpay_payment_id: rzResult.razorpay_payment_id,
          razorpay_order_id: rzResult.razorpay_order_id,
          razorpay_signature: rzResult.razorpay_signature,
        });
      } catch {
        // Fall back to polling if verify fails (e.g. webhook already fired).
      }

      const blob = await pollUntilPdfReady(blueprintId, setStatus);
      setStatus("Downloading PDF...");
      downloadPdfBlob(blob, `blueprint-${blueprintId}.pdf`);
    } catch (e) {
      const msg =
        e instanceof ApiError
          ? e.message
          : (e as Error).message || "Could not download PDF.";
      setError(msg);
    } finally {
      setStatus(null);
    }
  }, [blueprintId]);

  return {
    download,
    status,
    error,
    busy: status !== null,
  };
}
