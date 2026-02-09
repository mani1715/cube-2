import { useState } from 'react';
import { Layout } from '@/components/layout/Layout';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Checkbox } from '@/components/ui/checkbox';
import { AlertTriangle, CheckCircle, AlertCircle } from 'lucide-react';
import { toast } from 'sonner';
import SEO from '@/components/SEO';
import contactBg from '@/assets/bg-contact.jpg';

const AccountDeletion = () => {
  const [email, setEmail] = useState('');
  const [reason, setReason] = useState('');
  const [confirmation, setConfirmation] = useState(false);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const handleDeletion = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!email) {
      toast.error('Please enter your email address');
      return;
    }

    if (!confirmation) {
      toast.error('Please confirm that you understand the consequences');
      return;
    }

    setLoading(true);
    
    try {
      const backendUrl = import.meta.env.VITE_SUPABASE_URL || import.meta.env.REACT_APP_BACKEND_URL || '';
      const response = await fetch(`${backendUrl}/api/phase9/compliance/account-deletion`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,
          confirmation,
          reason
        }),
      });

      const result = await response.json();

      if (response.ok) {
        setSuccess(true);
        toast.success('Account deletion request submitted successfully');
      } else {
        toast.error(result.detail || 'Failed to process deletion request');
      }
    } catch (error) {
      console.error('Deletion error:', error);
      toast.error('An error occurred while processing your request');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <SEO 
        title="Account Deletion Request"
        description="Request permanent deletion of your account and personal data from A-Cube Mental Health Platform."
        keywords={['account deletion', 'GDPR', 'right to erasure', 'data removal']}
      />
      
      {/* Hero Section */}
      <section className="relative py-20 md:py-28 overflow-hidden">
        <div 
          className="absolute inset-0 bg-cover bg-center"
          style={{ backgroundImage: `url(${contactBg})` }}
        />
        <div className="absolute inset-0 bg-gradient-to-br from-background/95 via-background/80 to-background/70" />
        <div className="container mx-auto px-4 relative z-10">
          <div className="max-w-3xl mx-auto text-center">
            <h1 className="font-display text-4xl md:text-5xl font-semibold text-foreground mb-6">
              Account Deletion Request
            </h1>
            <p className="text-lg text-muted-foreground">
              Exercise your right to erasure (GDPR). Request permanent deletion of your account and all associated data.
            </p>
          </div>
        </div>
      </section>

      {/* Deletion Form Section */}
      <section className="py-16 md:py-24">
        <div className="container mx-auto px-4">
          <div className="max-w-2xl mx-auto">
            {!success ? (
              <div className="bg-card border border-border rounded-2xl p-8">
                <div className="mb-6 p-4 bg-destructive/10 border border-destructive/20 rounded-lg">
                  <div className="flex gap-2">
                    <AlertTriangle className="w-5 h-5 text-destructive flex-shrink-0 mt-0.5" />
                    <div className="text-sm">
                      <p className="font-semibold text-foreground mb-2">Warning: This Action Cannot Be Undone</p>
                      <p className="text-muted-foreground mb-2">
                        Account deletion will permanently remove:
                      </p>
                      <ul className="list-disc list-inside text-muted-foreground space-y-1">
                        <li>All your session bookings and appointment history</li>
                        <li>Contact form submissions</li>
                        <li>Volunteer applications</li>
                        <li>Event registrations</li>
                        <li>Career applications</li>
                        <li>Any other personal data associated with your account</li>
                      </ul>
                    </div>
                  </div>
                </div>

                <form onSubmit={handleDeletion} className="space-y-6">
                  <div>
                    <Label htmlFor="email">Email Address</Label>
                    <Input
                      id="email"
                      type="email"
                      placeholder="your.email@example.com"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      required
                      className="mt-1"
                    />
                    <p className="text-sm text-muted-foreground mt-1">
                      Enter the email address associated with your account
                    </p>
                  </div>

                  <div>
                    <Label htmlFor="reason">Reason for Deletion (Optional)</Label>
                    <Textarea
                      id="reason"
                      placeholder="Please tell us why you're deleting your account (optional)"
                      value={reason}
                      onChange={(e) => setReason(e.target.value)}
                      className="mt-1"
                      rows={4}
                    />
                  </div>

                  <div className="flex items-start space-x-2">
                    <Checkbox
                      id="confirmation"
                      checked={confirmation}
                      onCheckedChange={(checked) => setConfirmation(checked as boolean)}
                      required
                    />
                    <label
                      htmlFor="confirmation"
                      className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                    >
                      I understand that this action is permanent and cannot be undone. All my data will be permanently deleted within 30 days.
                    </label>
                  </div>

                  <Button 
                    type="submit" 
                    variant="destructive" 
                    className="w-full" 
                    disabled={loading || !confirmation}
                  >
                    {loading ? 'Processing...' : 'Delete My Account'}
                  </Button>
                </form>

                <div className="mt-6 p-4 bg-blue-500/10 border border-blue-500/20 rounded-lg">
                  <div className="flex gap-2">
                    <AlertCircle className="w-5 h-5 text-blue-500 flex-shrink-0 mt-0.5" />
                    <div className="text-sm text-muted-foreground">
                      <p className="font-medium text-foreground mb-1">Need a Copy of Your Data?</p>
                      <p>Before deleting your account, you may want to <a href="/data-export" className="text-primary hover:underline">export your data</a> for your records.</p>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-card border border-border rounded-2xl p-8">
                <div className="flex items-center gap-3 text-green-500 mb-6">
                  <CheckCircle className="w-8 h-8" />
                  <h2 className="text-2xl font-semibold text-foreground">Request Submitted</h2>
                </div>

                <div className="bg-green-500/10 border border-green-500/20 rounded-lg p-6 mb-6">
                  <p className="text-muted-foreground mb-4">
                    Your account deletion request has been received and will be processed within 30 days as per our data retention policy.
                  </p>
                  <p className="text-muted-foreground">
                    You will receive a confirmation email at <strong className="text-foreground">{email}</strong> shortly.
                  </p>
                </div>

                <div className="p-4 bg-blue-500/10 border border-blue-500/20 rounded-lg">
                  <div className="flex gap-2">
                    <AlertCircle className="w-5 h-5 text-blue-500 flex-shrink-0 mt-0.5" />
                    <div className="text-sm text-muted-foreground">
                      <p className="font-medium text-foreground mb-1">What Happens Next?</p>
                      <ul className="list-disc list-inside space-y-1">
                        <li>Your data will be marked for deletion immediately</li>
                        <li>You will lose access to your account within 24 hours</li>
                        <li>Complete data removal will occur within 30 days</li>
                        <li>You'll receive a final confirmation email when deletion is complete</li>
                      </ul>
                    </div>
                  </div>
                </div>

                <Button 
                  onClick={() => window.location.href = '/'} 
                  className="w-full mt-6"
                >
                  Return to Homepage
                </Button>
              </div>
            )}
          </div>
        </div>
      </section>
    </Layout>
  );
};

export default AccountDeletion;
