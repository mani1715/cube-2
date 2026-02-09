import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Navbar } from '@/components/layout/Navbar';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { CheckCircle2, Download, Home, LayoutDashboard, Loader2 } from 'lucide-react';
import { paymentAPI } from '@/lib/phase12Api';
import SEO from '@/components/SEO';

const PaymentSuccess = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [transaction, setTransaction] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  const transactionId = searchParams.get('transaction_id');

  useEffect(() => {
    const fetchTransaction = async () => {
      if (!transactionId) {
        setIsLoading(false);
        return;
      }

      try {
        const response = await paymentAPI.getTransaction(transactionId);
        if (response.success) {
          setTransaction(response.transaction);
        }
      } catch (error) {
        console.error('Failed to fetch transaction:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchTransaction();
  }, [transactionId]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        <Navbar />
        <div className="container mx-auto px-4 pt-32 pb-20">
          <div className="flex items-center justify-center h-64">
            <Loader2 className="w-8 h-8 animate-spin text-primary" />
          </div>
        </div>
      </div>
    );
  }

  return (
    <>
      <SEO
        title="Payment Successful - A-Cube"
        description="Your payment has been processed successfully."
      />
      <div className="min-h-screen bg-gradient-to-br from-green-50 via-background to-background dark:from-green-950/20">
        <Navbar />
        
        <div className="container mx-auto px-4 pt-32 pb-20">
          <div className="max-w-2xl mx-auto">
            {/* Success Icon */}
            <div className="text-center mb-8 animate-fade-in">
              <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-green-500/10 mb-4 animate-bounce">
                <CheckCircle2 className="w-12 h-12 text-green-500" />
              </div>
              <h1 className="text-3xl md:text-4xl font-display font-bold mb-2 text-green-600 dark:text-green-400">
                Payment Successful!
              </h1>
              <p className="text-muted-foreground text-lg">
                Thank you for your payment. Your transaction has been completed.
              </p>
            </div>

            {/* Transaction Details Card */}
            {transaction && (
              <Card className="animate-slide-in-up shadow-xl">
                <CardHeader>
                  <CardTitle>Transaction Details</CardTitle>
                  <CardDescription>Your payment receipt</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-muted-foreground">Transaction ID</p>
                      <p className="text-sm font-mono font-medium">{transaction.transaction_id.slice(0, 16)}...</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Amount Paid</p>
                      <p className="text-lg font-bold text-green-600">₹{transaction.amount.toFixed(2)}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Payment Method</p>
                      <p className="text-sm font-medium capitalize">{transaction.payment_method || 'Online'}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Status</p>
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                        Success
                      </span>
                    </div>
                    <div className="col-span-2">
                      <p className="text-sm text-muted-foreground">Item</p>
                      <p className="text-sm font-medium">{transaction.item_name}</p>
                    </div>
                    <div className="col-span-2">
                      <p className="text-sm text-muted-foreground">Date & Time</p>
                      <p className="text-sm">{new Date(transaction.created_at).toLocaleString()}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Action Buttons */}
            <div className="mt-8 flex flex-col sm:flex-row gap-4 animate-slide-in-up" style={{ animationDelay: '0.2s' }}>
              <Button
                onClick={() => navigate('/user/dashboard')}
                className="flex-1 gap-2"
                size="lg"
              >
                <LayoutDashboard className="w-4 h-4" />
                Go to Dashboard
              </Button>
              <Button
                onClick={() => navigate('/')}
                variant="outline"
                className="flex-1 gap-2"
                size="lg"
              >
                <Home className="w-4 h-4" />
                Back to Home
              </Button>
            </div>

            {/* Additional Info */}
            <div className="mt-6 p-4 bg-muted/50 rounded-lg text-center text-sm text-muted-foreground">
              <p>A confirmation email has been sent to your registered email address.</p>
              <p className="mt-2">For any queries, please contact our support team.</p>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default PaymentSuccess;
