/**
 * PHASE 12 - Payment Modal Component
 * Handles Razorpay payment integration
 */

import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Loader2, CreditCard, Check } from 'lucide-react';
import { paymentAPI } from '@/lib/phase12Api';
import { toast } from 'sonner';

interface PaymentModalProps {
  isOpen: boolean;
  onClose: () => void;
  amount: number;
  itemType: 'session' | 'event' | 'blog';
  itemId: string;
  itemName: string;
  userEmail?: string;
  userName?: string;
  userPhone?: string;
  onSuccess?: (transactionData: any) => void;
  onFailure?: (error: any) => void;
}

declare global {
  interface Window {
    Razorpay: any;
  }
}

const PaymentModal: React.FC<PaymentModalProps> = ({
  isOpen,
  onClose,
  amount,
  itemType,
  itemId,
  itemName,
  userEmail,
  userName,
  userPhone,
  onSuccess,
  onFailure,
}) => {
  const [isProcessing, setIsProcessing] = useState(false);
  const [razorpayConfig, setRazorpayConfig] = useState<any>(null);

  useEffect(() => {
    // Fetch Razorpay configuration
    const fetchConfig = async () => {
      try {
        const config = await paymentAPI.getConfig();
        setRazorpayConfig(config);
      } catch (error) {
        console.error('Failed to fetch payment config:', error);
      }
    };

    if (isOpen) {
      fetchConfig();
    }
  }, [isOpen]);

  const handlePayment = async () => {
    if (!razorpayConfig || !razorpayConfig.razorpay_key_id) {
      toast.error('Payment gateway not configured');
      return;
    }

    setIsProcessing(true);

    try {
      // Create order
      const orderResponse = await paymentAPI.createOrder({
        amount,
        item_type: itemType,
        item_id: itemId,
        item_name: itemName,
        user_email: userEmail,
        user_name: userName,
        user_phone: userPhone,
      });

      if (!orderResponse.success) {
        throw new Error('Failed to create order');
      }

      // Initialize Razorpay
      const options = {
        key: razorpayConfig.razorpay_key_id,
        amount: orderResponse.amount_paise,
        currency: orderResponse.currency,
        name: 'A-Cube Mental Health',
        description: itemName,
        order_id: orderResponse.order_id,
        prefill: {
          name: userName || '',
          email: userEmail || '',
          contact: userPhone || '',
        },
        theme: {
          color: '#667eea',
        },
        handler: async function (response: any) {
          try {
            // Verify payment
            const verifyResponse = await paymentAPI.verifyPayment({
              razorpay_order_id: response.razorpay_order_id,
              razorpay_payment_id: response.razorpay_payment_id,
              razorpay_signature: response.razorpay_signature,
            });

            if (verifyResponse.success) {
              toast.success('Payment successful!');
              onSuccess?.(verifyResponse.transaction);
              onClose();
            } else {
              throw new Error('Payment verification failed');
            }
          } catch (error) {
            console.error('Payment verification error:', error);
            toast.error('Payment verification failed');
            onFailure?.(error);
          } finally {
            setIsProcessing(false);
          }
        },
        modal: {
          ondismiss: function () {
            setIsProcessing(false);
            toast.info('Payment cancelled');
          },
        },
      };

      const razorpay = new window.Razorpay(options);
      razorpay.open();
    } catch (error: any) {
      console.error('Payment error:', error);
      toast.error(error.message || 'Failed to initiate payment');
      setIsProcessing(false);
      onFailure?.(error);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <CreditCard className="w-5 h-5 text-primary" />
            Complete Payment
          </DialogTitle>
          <DialogDescription>
            Secure payment powered by Razorpay
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {/* Payment Details */}
          <div className="space-y-3">
            <div className="flex justify-between items-center p-3 bg-muted rounded-lg">
              <span className="text-sm text-muted-foreground">Item</span>
              <span className="text-sm font-medium">{itemName}</span>
            </div>
            
            <div className="flex justify-between items-center p-3 bg-muted rounded-lg">
              <span className="text-sm text-muted-foreground">Amount</span>
              <span className="text-lg font-bold text-primary">₹{amount.toFixed(2)}</span>
            </div>

            {userEmail && (
              <div className="flex justify-between items-center p-3 bg-muted rounded-lg">
                <span className="text-sm text-muted-foreground">Email</span>
                <span className="text-sm">{userEmail}</span>
              </div>
            )}
          </div>

          {/* Payment Methods */}
          <div className="border rounded-lg p-4 bg-muted/50">
            <p className="text-sm font-medium mb-2">Supported Payment Methods:</p>
            <div className="flex flex-wrap gap-2 text-xs text-muted-foreground">
              <span className="px-2 py-1 bg-background rounded">UPI</span>
              <span className="px-2 py-1 bg-background rounded">Cards</span>
              <span className="px-2 py-1 bg-background rounded">Net Banking</span>
              <span className="px-2 py-1 bg-background rounded">Wallets</span>
            </div>
          </div>

          {/* Security Badge */}
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <Check className="w-4 h-4 text-green-500" />
            <span>Secure payment gateway with 256-bit encryption</span>
          </div>
        </div>

        <DialogFooter className="gap-2 sm:gap-0">
          <Button
            type="button"
            variant="outline"
            onClick={onClose}
            disabled={isProcessing}
          >
            Cancel
          </Button>
          <Button
            type="button"
            onClick={handlePayment}
            disabled={isProcessing}
            className="gap-2"
          >
            {isProcessing ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Processing...
              </>
            ) : (
              <>
                <CreditCard className="w-4 h-4" />
                Pay ₹{amount.toFixed(2)}
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default PaymentModal;
