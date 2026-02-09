import { useState, useEffect } from "react";
import { Layout } from "@/components/layout/Layout";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Calendar, Video, Clock, User, Mail, Lock, ArrowRight, Users, IndianRupee, FileText, LogOut, CheckCircle, AlertCircle } from "lucide-react";
import { supabase } from "@/integrations/supabase/client";
import { useToast } from "@/hooks/use-toast";
import psychologistBg from "@/assets/bg-psychologists.jpg";

const features = [
  {
    icon: Calendar,
    title: "Session Scheduling",
    description: "Manage your availability and schedule therapy sessions with clients.",
  },
  {
    icon: Video,
    title: "Online Meetings",
    description: "Conduct secure video therapy sessions directly from the platform.",
  },
  {
    icon: Clock,
    title: "Time Management",
    description: "Track your hours, sessions, and client interactions efficiently.",
  },
  {
    icon: User,
    title: "Client Management",
    description: "Access client profiles, notes, and treatment progress.",
  },
];

// Dashboard component shown after authentication
const PsychologistDashboard = ({ user, onLogout }: { user: any; onLogout: () => void }) => {
  const [activeTab, setActiveTab] = useState<'clients' | 'availability' | 'compensation'>('clients');

  // Mock data for demonstration
  const assignedClients = [
    { id: 1, name: "Client A", nextSession: "2026-01-15", sessions: 5 },
    { id: 2, name: "Client B", nextSession: "2026-01-16", sessions: 3 },
    { id: 3, name: "Client C", nextSession: "2026-01-18", sessions: 8 },
  ];

  const availabilitySlots = [
    { day: "Monday", slots: ["10:00 AM - 12:00 PM", "2:00 PM - 5:00 PM"] },
    { day: "Tuesday", slots: ["9:00 AM - 1:00 PM"] },
    { day: "Wednesday", slots: ["10:00 AM - 12:00 PM", "3:00 PM - 6:00 PM"] },
    { day: "Thursday", slots: ["2:00 PM - 6:00 PM"] },
    { day: "Friday", slots: ["10:00 AM - 2:00 PM"] },
  ];

  return (
    <div className="min-h-[calc(100vh-5rem)] bg-background">
      {/* Dashboard Header */}
      <div className="bg-card border-b border-border">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="font-display text-2xl md:text-3xl font-semibold text-foreground">
                Welcome back
              </h1>
              <p className="text-muted-foreground mt-1">{user?.email}</p>
            </div>
            <Button variant="outline" onClick={onLogout} className="gap-2">
              <LogOut className="w-4 h-4" />
              Sign Out
            </Button>
          </div>
        </div>
      </div>

      {/* Dashboard Navigation */}
      <div className="bg-card border-b border-border">
        <div className="container mx-auto px-4">
          <nav className="flex gap-1">
            {[
              { id: 'clients', label: 'Assigned Clients', icon: Users },
              { id: 'availability', label: 'Session Availability', icon: Calendar },
              { id: 'compensation', label: 'Compensation & Guidelines', icon: IndianRupee },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === tab.id
                    ? 'border-primary text-primary'
                    : 'border-transparent text-muted-foreground hover:text-foreground'
                }`}
              >
                <tab.icon className="w-4 h-4" />
                {tab.label}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Dashboard Content */}
      <div className="container mx-auto px-4 py-8">
        {/* Assigned Clients Tab */}
        {activeTab === 'clients' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="font-display text-xl font-semibold text-foreground">Your Assigned Clients</h2>
              <span className="text-sm text-muted-foreground">{assignedClients.length} active clients</span>
            </div>
            
            <div className="grid gap-4">
              {assignedClients.map((client) => (
                <div key={client.id} className="p-6 rounded-2xl bg-card border border-border card-hover">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 rounded-full bg-accent flex items-center justify-center">
                        <User className="w-5 h-5 text-primary" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-foreground">{client.name}</h3>
                        <p className="text-sm text-muted-foreground">Next session: {client.nextSession}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-medium text-foreground">{client.sessions} sessions</p>
                      <p className="text-xs text-muted-foreground">completed</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <div className="p-6 rounded-2xl bg-accent/50 border border-border">
              <p className="text-sm text-muted-foreground text-center">
                Client data is securely managed. For detailed case notes and treatment plans, access the client management system.
              </p>
            </div>
          </div>
        )}

        {/* Availability Tab */}
        {activeTab === 'availability' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="font-display text-xl font-semibold text-foreground">Your Session Availability</h2>
              <Button variant="outline" size="sm">
                Edit Schedule
              </Button>
            </div>

            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
              {availabilitySlots.map((day) => (
                <div key={day.day} className="p-6 rounded-2xl bg-card border border-border">
                  <h3 className="font-semibold text-foreground mb-3">{day.day}</h3>
                  <div className="space-y-2">
                    {day.slots.map((slot, idx) => (
                      <div key={idx} className="flex items-center gap-2 text-sm">
                        <Clock className="w-4 h-4 text-primary" />
                        <span className="text-muted-foreground">{slot}</span>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>

            <div className="p-6 rounded-2xl bg-card border border-border">
              <h3 className="font-semibold text-foreground mb-2">Managing Your Availability</h3>
              <p className="text-sm text-muted-foreground">
                Your availability slots are visible to clients when booking sessions. Please keep your schedule updated to ensure accurate booking options. Sessions can be conducted in-person at our centers or via secure video call.
              </p>
            </div>
          </div>
        )}

        {/* Compensation Tab - PRIVATE */}
        {activeTab === 'compensation' && (
          <div className="space-y-6">
            <h2 className="font-display text-xl font-semibold text-foreground">Compensation & Guidelines</h2>

            {/* Per-Session Compensation */}
            <div className="p-6 rounded-2xl bg-card border border-border">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-xl bg-accent flex items-center justify-center">
                  <IndianRupee className="w-5 h-5 text-primary" />
                </div>
                <h3 className="font-semibold text-foreground">Per-Session Compensation</h3>
              </div>
              
              <div className="p-4 rounded-xl bg-accent/50 mb-4">
                <div className="flex items-center justify-center gap-2">
                  <span className="text-3xl font-display font-semibold text-primary">₹250 – ₹400</span>
                  <span className="text-muted-foreground">per session</span>
                </div>
              </div>
              
              <p className="text-sm text-muted-foreground">
                Compensation is calculated based on session type, complexity, and experience level. Rates are reviewed quarterly and adjusted based on organizational capacity and funding.
              </p>
            </div>

            {/* Conditions & Guidelines */}
            <div className="p-6 rounded-2xl bg-card border border-border">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-xl bg-accent flex items-center justify-center">
                  <FileText className="w-5 h-5 text-primary" />
                </div>
                <h3 className="font-semibold text-foreground">Terms & Conditions</h3>
              </div>
              
              <div className="space-y-4">
                <div className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-primary flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium text-foreground">Ethical Guidelines</p>
                    <p className="text-sm text-muted-foreground">
                      All sessions must adhere to organizational ethical guidelines and professional standards of practice. This includes maintaining client confidentiality, professional boundaries, and evidence-based approaches.
                    </p>
                  </div>
                </div>
                
                <div className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-primary flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium text-foreground">Payment Processing</p>
                    <p className="text-sm text-muted-foreground">
                      Compensation is released after session completion and documentation submission. Payments are processed bi-weekly on the 1st and 15th of each month.
                    </p>
                  </div>
                </div>
                
                <div className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-primary flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium text-foreground">Mission Commitment</p>
                    <p className="text-sm text-muted-foreground">
                      As a non-profit organization, we are committed to providing affordable mental health care. By joining our team, you support our mission to make therapy accessible to underserved communities.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Important Notice */}
            <div className="p-6 rounded-2xl bg-primary/5 border border-primary/20">
              <div className="flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-primary flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-foreground mb-1">Important Reminder</p>
                  <p className="text-sm text-muted-foreground">
                    This compensation information is confidential and for your personal reference only. Please do not share session rates or internal compensation details publicly or with clients.
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

const PsychologistPortal = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [user, setUser] = useState<any>(null);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [license, setLicense] = useState("");
  const [specialty, setSpecialty] = useState("");
  const { toast } = useToast();

  useEffect(() => {
    // Set up auth state listener BEFORE checking session
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user ?? null);
    });

    // Check for existing session
    supabase.auth.getSession().then(({ data: { session } }) => {
      setUser(session?.user ?? null);
    });

    return () => subscription.unsubscribe();
  }, []);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const { error } = await supabase.auth.signInWithPassword({
        email,
        password,
      });

      if (error) throw error;

      toast({
        title: "Welcome back!",
        description: "You have successfully signed in.",
      });
    } catch (error: any) {
      toast({
        title: "Sign in failed",
        description: error.message,
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const { error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          emailRedirectTo: window.location.origin,
          data: {
            full_name: `${firstName} ${lastName}`,
            license_number: license,
            specialty: specialty,
          },
        },
      });

      if (error) throw error;

      toast({
        title: "Registration submitted",
        description: "Your profile has been created. Please sign in to continue.",
      });
      setIsLogin(true);
    } catch (error: any) {
      toast({
        title: "Registration failed",
        description: error.message,
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = async () => {
    await supabase.auth.signOut();
    setUser(null);
    toast({
      title: "Signed out",
      description: "You have been successfully signed out.",
    });
  };

  // If user is authenticated, show dashboard
  if (user) {
    return (
      <Layout showFooter={false}>
        <PsychologistDashboard user={user} onLogout={handleLogout} />
      </Layout>
    );
  }

  // Otherwise show login/register form
  return (
    <Layout showFooter={false}>
      <div className="min-h-[calc(100vh-5rem)] flex">
        {/* Left Panel - Features */}
        <div className="hidden lg:flex lg:w-1/2 p-12 flex-col justify-center relative overflow-hidden">
          <div 
            className="absolute inset-0 bg-cover bg-center"
            style={{ backgroundImage: `url(${psychologistBg})` }}
          />
          <div className="absolute inset-0 bg-primary/85" />
          {/* Background decorative elements */}
          <div className="absolute top-0 right-0 w-64 h-64 bg-white/5 rounded-full blur-3xl" />
          <div className="absolute bottom-0 left-0 w-96 h-96 bg-white/5 rounded-full blur-3xl" />
          
          <div className="max-w-md relative z-10">
            <h2 className="font-display text-3xl font-semibold text-primary-foreground mb-6 animate-fade-up opacity-0" style={{ animationDelay: "0s", animationFillMode: "forwards" }}>
              Psychologist Portal
            </h2>
            <p className="text-primary-foreground/80 mb-12 animate-fade-up opacity-0" style={{ animationDelay: "0.1s", animationFillMode: "forwards" }}>
              Join our community of dedicated mental health professionals. Access your dashboard to manage clients, schedule sessions, and make a meaningful impact.
            </p>

            <div className="space-y-6">
              {features.map((feature, index) => (
                <div 
                  key={index} 
                  className="flex items-start gap-4 animate-fade-up opacity-0"
                  style={{ animationDelay: `${0.2 + index * 0.1}s`, animationFillMode: "forwards" }}
                >
                  <div className="w-12 h-12 rounded-xl bg-primary-foreground/10 flex items-center justify-center flex-shrink-0 transition-transform duration-300 hover:scale-105">
                    <feature.icon className="w-5 h-5 text-primary-foreground" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-primary-foreground mb-1">
                      {feature.title}
                    </h3>
                    <p className="text-sm text-primary-foreground/70">
                      {feature.description}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Panel - Auth Form */}
        <div className="w-full lg:w-1/2 flex items-center justify-center p-8">
          <div className="w-full max-w-md animate-fade-up opacity-0" style={{ animationDelay: "0.1s", animationFillMode: "forwards" }}>
            <div className="text-center mb-8">
              <h1 className="font-display text-2xl md:text-3xl font-semibold text-foreground mb-2">
                {isLogin ? "Welcome Back" : "Create Your Profile"}
              </h1>
              <p className="text-muted-foreground">
                {isLogin
                  ? "Sign in to access your psychologist dashboard"
                  : "Register to join our team of mental health professionals"}
              </p>
            </div>

            <form onSubmit={isLogin ? handleLogin : handleRegister} className="space-y-5">
              {!isLogin && (
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="firstName">First Name</Label>
                    <Input 
                      id="firstName" 
                      placeholder="John" 
                      value={firstName}
                      onChange={(e) => setFirstName(e.target.value)}
                      className="transition-all duration-200" 
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="lastName">Last Name</Label>
                    <Input 
                      id="lastName" 
                      placeholder="Doe" 
                      value={lastName}
                      onChange={(e) => setLastName(e.target.value)}
                      className="transition-all duration-200" 
                      required
                    />
                  </div>
                </div>
              )}

              <div className="space-y-2">
                <Label htmlFor="email">Email Address</Label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                  <Input 
                    id="email" 
                    type="email" 
                    placeholder="you@example.com" 
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="pl-10 transition-all duration-200" 
                    required
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                  <Input 
                    id="password" 
                    type="password" 
                    placeholder="••••••••" 
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="pl-10 transition-all duration-200" 
                    required
                    minLength={6}
                  />
                </div>
              </div>

              {!isLogin && (
                <>
                  <div className="space-y-2">
                    <Label htmlFor="license">License Number</Label>
                    <Input 
                      id="license" 
                      placeholder="PSY-XXXXXX" 
                      value={license}
                      onChange={(e) => setLicense(e.target.value)}
                      className="transition-all duration-200" 
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="specialty">Specialty</Label>
                    <Input 
                      id="specialty" 
                      placeholder="e.g., Cognitive Behavioral Therapy" 
                      value={specialty}
                      onChange={(e) => setSpecialty(e.target.value)}
                      className="transition-all duration-200" 
                      required
                    />
                  </div>
                </>
              )}

              <Button variant="hero" className="w-full" type="submit" disabled={isLoading}>
                {isLoading ? "Please wait..." : isLogin ? "Sign In" : "Create Account"}
                <ArrowRight className="w-4 h-4" />
              </Button>
            </form>

            <div className="mt-6 text-center">
              <button
                type="button"
                onClick={() => setIsLogin(!isLogin)}
                className="text-sm text-primary hover:underline transition-colors duration-200"
              >
                {isLogin
                  ? "Don't have an account? Register here"
                  : "Already have an account? Sign in"}
              </button>
            </div>

            <div className="mt-8 p-4 rounded-xl bg-muted/50 border border-border animate-fade-in">
              <p className="text-sm text-muted-foreground text-center">
                <strong>For Licensed Professionals:</strong> Registration is available exclusively for verified mental health professionals. Your credentials will be reviewed before full access is granted.
              </p>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default PsychologistPortal;
