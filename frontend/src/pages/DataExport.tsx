import { useState } from 'react';
import { Layout } from '@/components/layout/Layout';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Download, CheckCircle, AlertCircle } from 'lucide-react';
import { toast } from 'sonner';
import SEO from '@/components/SEO';
import contactBg from '@/assets/bg-contact.jpg';

const DataExport = () => {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [exportData, setExportData] = useState<any>(null);

  const handleExport = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!email) {
      toast.error('Please enter your email address');
      return;
    }

    setLoading(true);
    
    try {
      const backendUrl = import.meta.env.VITE_SUPABASE_URL || import.meta.env.REACT_APP_BACKEND_URL || '';
      const response = await fetch(`${backendUrl}/api/phase9/compliance/data-export`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,
          data_types: ['all']
        }),
      });

      const result = await response.json();

      if (response.ok) {
        setExportData(result.export_data);
        toast.success('Data export generated successfully!');
      } else {
        toast.error(result.detail || 'Failed to export data');
      }
    } catch (error) {
      console.error('Export error:', error);
      toast.error('An error occurred while exporting data');
    } finally {
      setLoading(false);
    }
  };

  const downloadJSON = () => {
    if (!exportData) return;

    const dataStr = JSON.stringify(exportData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `a-cube-data-export-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    toast.success('Download started!');
  };

  return (
    <Layout>
      <SEO 
        title="Data Export Request"
        description="Request a complete export of your personal data from A-Cube Mental Health Platform."
        keywords={['data export', 'GDPR', 'personal data', 'privacy rights']}
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
              Data Export Request
            </h1>
            <p className="text-lg text-muted-foreground">
              Exercise your right to data portability. Request a complete copy of all your personal data stored in our system.
            </p>
          </div>
        </div>
      </section>

      {/* Export Form Section */}
      <section className="py-16 md:py-24">
        <div className="container mx-auto px-4">
          <div className="max-w-2xl mx-auto">
            {!exportData ? (
              <div className="bg-card border border-border rounded-2xl p-8">
                <div className="mb-6">
                  <div className="flex items-center gap-2 text-primary mb-4">
                    <Download className="w-5 h-5" />
                    <h2 className="text-xl font-semibold">Request Your Data</h2>
                  </div>
                  <p className="text-muted-foreground">
                    Enter your email address to receive a complete export of your personal data, including:
                  </p>
                  <ul className="list-disc list-inside text-muted-foreground mt-3 space-y-1">
                    <li>Session bookings and appointments</li>
                    <li>Contact form submissions</li>
                    <li>Volunteer applications</li>
                    <li>Event registrations</li>
                    <li>Career applications</li>
                  </ul>
                </div>

                <form onSubmit={handleExport} className="space-y-4">
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
                  </div>

                  <Button type="submit" className="w-full" disabled={loading}>
                    {loading ? 'Generating Export...' : 'Generate Data Export'}
                  </Button>
                </form>

                <div className="mt-6 p-4 bg-blue-500/10 border border-blue-500/20 rounded-lg">
                  <div className="flex gap-2">
                    <AlertCircle className="w-5 h-5 text-blue-500 flex-shrink-0 mt-0.5" />
                    <div className="text-sm text-muted-foreground">
                      <p className="font-medium text-foreground mb-1">Privacy Notice</p>
                      <p>Your data export will be generated instantly. Please ensure you save it securely as it contains all your personal information.</p>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-card border border-border rounded-2xl p-8">
                <div className="flex items-center gap-3 text-green-500 mb-6">
                  <CheckCircle className="w-8 h-8" />
                  <h2 className="text-2xl font-semibold text-foreground">Export Complete!</h2>
                </div>

                <div className="bg-green-500/10 border border-green-500/20 rounded-lg p-6 mb-6">
                  <p className="text-muted-foreground mb-4">
                    Your data export has been generated successfully. Click the button below to download your data as a JSON file.
                  </p>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-muted-foreground">Export Date:</p>
                      <p className="font-semibold text-foreground">{new Date(exportData.export_date).toLocaleString()}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Email:</p>
                      <p className="font-semibold text-foreground">{exportData.email}</p>
                    </div>
                  </div>
                </div>

                <Button onClick={downloadJSON} className="w-full mb-4">
                  <Download className="w-4 h-4 mr-2" />
                  Download Data Export (JSON)
                </Button>

                <Button 
                  variant="outline" 
                  onClick={() => {
                    setExportData(null);
                    setEmail('');
                  }} 
                  className="w-full"
                >
                  Request Another Export
                </Button>

                <div className="mt-6 p-4 bg-yellow-500/10 border border-yellow-500/20 rounded-lg">
                  <div className="flex gap-2">
                    <AlertCircle className="w-5 h-5 text-yellow-500 flex-shrink-0 mt-0.5" />
                    <div className="text-sm text-muted-foreground">
                      <p className="font-medium text-foreground mb-1">Important</p>
                      <p>Please store this data securely. It contains all your personal information from our platform.</p>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </section>
    </Layout>
  );
};

export default DataExport;
