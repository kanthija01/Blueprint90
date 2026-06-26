// Payment API — pre-assessment order creation, client-side verification,
// status polling, and legacy PDF-unlock order creation.

import { apiRequest } from "./client";

export type CreateOrderResponse = {
  payment_id: string;
  razorpay_order_id: string;
  amount: number;
  currency: string;
  key_id: string;
};

export type VerifyPaymentRequest = {
  payment_id: string;          // our internal payment_id
  razorpay_payment_id: string; // from Razorpay success callback
  razorpay_order_id: string;   // from Razorpay success callback
  razorpay_signature: string;  // from Razorpay success callback
};

/** New flow: create a Razorpay order BEFORE assessment submission. */
export function createPreAssessmentOrder(): Promise<CreateOrderResponse> {
  return apiRequest<CreateOrderResponse>(
    "/api/payments/create-pre-assessment-order",
    { method: "POST" },
  );
}

/**
 * Verify a completed Razorpay payment using the client-side callback params.
 * The backend re-computes the HMAC signature to confirm authenticity, then
 * marks the payment as paid in MongoDB.  This is the primary verification
 * path — it works in local dev without requiring a publicly reachable webhook.
 */
export function verifyPayment(req: VerifyPaymentRequest): Promise<{ status: string }> {
  return apiRequest<{ status: string }>("/api/payments/verify", {
    method: "POST",
    body: req,
  });
}

/** Poll the backend until a payment_id is confirmed paid (status="paid").
 *  Used as a fallback after verifyPayment — normally returns immediately. */
export async function pollPaymentStatus(
  paymentId: string,
  onStatus: (msg: string) => void,
  intervalMs = 2000,
  maxMs = 30_000,
): Promise<void> {
  const deadline = Date.now() + maxMs;
  onStatus("Confirming payment…");

  while (Date.now() < deadline) {
    const res = await apiRequest<{ status: string }>(
      `/api/payments/status/${paymentId}`,
    );
    if (res.status === "paid") return;
    await new Promise<void>((r) => setTimeout(r, intervalMs));
  }

  throw new Error(
    "Payment confirmation timed out. Please try again in a moment.",
  );
}

/** Legacy: create a Razorpay order for PDF unlock on an existing blueprint. */
export function createOrder(blueprintId: string): Promise<CreateOrderResponse> {
  return apiRequest<CreateOrderResponse>("/api/payments/create-order", {
    method: "POST",
    body: { blueprint_id: blueprintId },
  });
}
