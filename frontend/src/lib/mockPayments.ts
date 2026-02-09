// Mock payment service for testing/demo purposes
// Replace with real Stripe integration when ready for production

export interface MockPaymentIntent {
  id: string;
  amount: number;
  currency: string;
  status: 'pending' | 'succeeded' | 'failed';
  created: number;
}

export const createMockPaymentIntent = async (
  amount: number,
  currency: string = 'usd'
): Promise<MockPaymentIntent> => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  return {
    id: `pi_mock_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
    amount,
    currency,
    status: 'pending',
    created: Date.now(),
  };
};

export const confirmMockPayment = async (
  paymentIntentId: string
): Promise<MockPaymentIntent> => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 1500));
  
  // 90% success rate for demo purposes
  const succeeded = Math.random() > 0.1;
  
  return {
    id: paymentIntentId,
    amount: 0,
    currency: 'usd',
    status: succeeded ? 'succeeded' : 'failed',
    created: Date.now(),
  };
};

export const formatAmount = (amount: number, currency: string = 'usd'): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency.toUpperCase(),
  }).format(amount / 100);
};
