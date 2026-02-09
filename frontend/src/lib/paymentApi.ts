// Payment API utilities for Razorpay integration

const API_BASE_URL = import.meta.env.VITE_REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL || '';

interface CreateOrderRequest {
  amount: number;
  item_type: 'session' | 'event' | 'blog';
  item_id: string;
  item_name: string;
  user_email?: string;
  user_name?: string;
  user_phone?: string;
}

interface CreateOrderResponse {
  transaction_id: string;
  razorpay_order_id: string;
  amount: number;
  currency: string;
  razorpay_key_id: string;
}

interface VerifyPaymentRequest {
  razorpay_order_id: string;
  razorpay_payment_id: string;
  razorpay_signature: string;
}

interface VerifyPaymentResponse {
  success: boolean;
  transaction_id: string;
  message: string;
}

interface RazorpayConfig {
  key_id: string;
  enabled: boolean;
}

export const paymentAPI = {
  /**
   * Create a payment order
   */
  createOrder: async (orderData: CreateOrderRequest): Promise<CreateOrderResponse> => {
    const response = await fetch(`${API_BASE_URL}/api/phase12/payments/create-order`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(orderData),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to create order' }));
      throw new Error(error.detail || 'Failed to create order');
    }

    return response.json();
  },

  /**
   * Verify payment after successful Razorpay transaction
   */
  verifyPayment: async (paymentData: VerifyPaymentRequest): Promise<VerifyPaymentResponse> => {
    const response = await fetch(`${API_BASE_URL}/api/phase12/payments/verify-payment`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(paymentData),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Payment verification failed' }));
      throw new Error(error.detail || 'Payment verification failed');
    }

    return response.json();
  },

  /**
   * Get Razorpay configuration (key_id)
   */
  getConfig: async (): Promise<RazorpayConfig> => {
    const response = await fetch(`${API_BASE_URL}/api/phase12/payments/config`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error('Failed to fetch payment config');
    }

    return response.json();
  },

  /**
   * Get transaction details
   */
  getTransaction: async (transactionId: string): Promise<any> => {
    const response = await fetch(`${API_BASE_URL}/api/phase12/payments/transaction/${transactionId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error('Failed to fetch transaction');
    }

    return response.json();
  },
};
