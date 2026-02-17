import React from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Navbar } from '@/components/layout/Navbar';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { XCircle, Home, RefreshCw, HelpCircle } from 'lucide-react';
import SEO from '@/components/SEO';

const PaymentFailure = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  
  const error = searchParams.get('error') || 'Payment failed';

  return (
    <>
      <SEO
        title="Payment Failed - A-Cube"
        description="Your payment could not be processed. Please try again."
      />
      <div className="min-h-screen bg-gradient-to-br from-red-50 via-background to-background dark:from-red-950/20">
        <Navbar />
        
        <div className="container mx-auto px-4 pt-32 pb-20">
          <div className="max-w-2xl mx-auto">
            {/* Failure Icon */}
            <div className="text-center mb-8 animate-fade-in">
              <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-destructive/10 mb-4">
                <XCircle className="w-12 h-12 text-destructive" />
              </div>
              <h1 className="text-3xl md:text-4xl font-display font-bold mb-2 text-destructive">
                Payment Failed
              </h1>
              <p className="text-muted-foreground text-lg">
                Unfortunately, we couldn't process your payment.
              </p>
            </div>

            {/* Error Details Card */}
            <Card className="animate-slide-in-up shadow-xl border-destructive/50">
              <CardHeader>
                <CardTitle className="text-destructive">What Went Wrong?</CardTitle>
                <CardDescription>Please check the following:</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="p-4 bg-destructive/5 rounded-lg border border-destructive/20">
                  <p className="text-sm font-medium text-destructive">{error}</p>
                </div>

                <div className="space-y-2">
                  <p className="text-sm font-medium">Common reasons for payment failure:</p>
                  <ul className="text-sm text-muted-foreground space-y-1 list-disc list-inside">
                    <li>Insufficient funds in your account</li>
                    <li>Incorrect payment details entered</li>
                    <li>Bank server issues or network problems</li>
                    <li>Payment cancelled by user</li>
                    <li>Card expired or blocked</li>
                  </ul>
                </div>
              </CardContent>
            </Card>

            {/* Action Buttons */}
            <div className="mt-8 flex flex-col sm:flex-row gap-4 animate-slide-in-up" style={{ animationDelay: '0.2s' }}>
              <Button
                onClick={() => navigate(-1)}
                className="flex-1 gap-2"
                size="lg"
              >
                <RefreshCw className="w-4 h-4" />
                Try Again
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

            {/* Help Section */}
            <div className="mt-6 p-6 bg-muted/50 rounded-lg text-center">
              <HelpCircle className="w-8 h-8 mx-auto mb-3 text-muted-foreground" />
              <p className="text-sm font-medium mb-2">Need Help?</p>
              <p className="text-sm text-muted-foreground mb-4">
                If you continue to face issues, please contact our support team.
              </p>
              <Button variant="outline" size="sm" onClick={() => navigate('/contact')}>
                Contact Support
              </Button>
            </div>

            {/* Safety Note */}
            <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-950/20 rounded-lg text-center text-xs text-muted-foreground">
              <p><strong>Note:</strong> Your payment has not been processed. No amount has been deducted from your account.</p>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default PaymentFailure;
