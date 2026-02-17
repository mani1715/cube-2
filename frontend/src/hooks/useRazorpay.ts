import { useState, useCallback } from 'react';
import { paymentAPI } from '@/lib/paymentApi';
import { useToast } from '@/hooks/use-toast';

interface RazorpayOptions {
  amount: number;
  item_type: 'session' | 'event' | 'blog';
  item_id: string;
  item_name: string;
  user_email?: string;
  user_name?: string;
  user_phone?: string;
  onSuccess?: (transactionId: string) => void;
  onFailure?: (error: string) => void;
}

declare global {
  interface Window {
    Razorpay: any;
  }
}

export const useRazorpay = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [isInitialized, setIsInitialized] = useState(false);
  const { toast } = useToast();

  // Load Razorpay script
  const loadRazorpayScript = useCallback(() => {
    return new Promise((resolve) => {
      if (window.Razorpay) {
        setIsInitialized(true);
        resolve(true);
        return;
      }

      const script = document.createElement('script');
      script.src = 'https://checkout.razorpay.com/v1/checkout.js';
      script.async = true;
      script.onload = () => {
        setIsInitialized(true);
        resolve(true);
      };
      script.onerror = () => {
        setIsInitialized(false);
        resolve(false);
      };
      document.body.appendChild(script);
    });
  }, []);

  // Open Razorpay payment
  const openPayment = useCallback(async (options: RazorpayOptions) => {
    try {
      setIsLoading(true);

      // Load Razorpay script if not loaded
      const scriptLoaded = await loadRazorpayScript();
      if (!scriptLoaded) {
        throw new Error('Failed to load payment gateway');
      }

      // Get Razorpay config
      const config = await paymentAPI.getConfig();
      if (!config.enabled) {
        throw new Error('Payment gateway is not configured');
      }

      // Create order
      const order = await paymentAPI.createOrder({
        amount: options.amount,
        item_type: options.item_type,
        item_id: options.item_id,
        item_name: options.item_name,
        user_email: options.user_email,
        user_name: options.user_name,
        user_phone: options.user_phone,
      });

      // Razorpay options
      const razorpayOptions = {
        key: config.key_id,
        amount: order.amount * 100, // Convert to paise
        currency: order.currency,
        name: 'A-Cube Mental Health',
        description: options.item_name,
        order_id: order.razorpay_order_id,
        prefill: {
          name: options.user_name || '',
          email: options.user_email || '',
          contact: options.user_phone || '',
        },
        theme: {
          color: '#667eea',
        },
        handler: async (response: any) => {
          try {
            // Verify payment
            const verificationResult = await paymentAPI.verifyPayment({
              razorpay_order_id: response.razorpay_order_id,
              razorpay_payment_id: response.razorpay_payment_id,
              razorpay_signature: response.razorpay_signature,
            });

            if (verificationResult.success) {
              toast({
                title: 'Payment Successful',
                description: 'Your payment has been processed successfully.',
              });
              options.onSuccess?.(verificationResult.transaction_id);
            } else {
              throw new Error('Payment verification failed');
            }
          } catch (error: any) {
            toast({
              title: 'Payment Verification Failed',
              description: error.message || 'Failed to verify payment',
              variant: 'destructive',
            });
            options.onFailure?.(error.message);
          } finally {
            setIsLoading(false);
          }
        },
        modal: {
          ondismiss: () => {
            toast({
              title: 'Payment Cancelled',
              description: 'You cancelled the payment process.',
              variant: 'default',
            });
            options.onFailure?.('Payment cancelled by user');
            setIsLoading(false);
          },
        },
      };

      // Open Razorpay checkout
      const razorpay = new window.Razorpay(razorpayOptions);
      razorpay.open();
    } catch (error: any) {
      console.error('Payment error:', error);
      toast({
        title: 'Payment Failed',
        description: error.message || 'Failed to initiate payment',
        variant: 'destructive',
      });
      options.onFailure?.(error.message);
      setIsLoading(false);
    }
  }, [loadRazorpayScript, toast]);

  return {
    openPayment,
    isLoading,
    isInitialized,
  };
};
