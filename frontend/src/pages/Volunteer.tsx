import { useState } from "react";
import { Link } from "react-router-dom";
import { Layout } from "@/components/layout/Layout";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Checkbox } from "@/components/ui/checkbox";
import { ScrollReveal } from "@/components/ui/scroll-reveal";
import { Heart, Users, Calendar, Megaphone, ArrowRight, CheckCircle } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import volunteerBg from "@/assets/bg-careers.jpg";
import { volunteerAPI } from "@/lib/api";

const opportunities = [
  { icon: Calendar, title: "Event Support", description: "Help organize and run our mental health events, workshops, and community gatherings." },
  { icon: Megaphone, title: "Outreach", description: "Spread awareness about mental health and our services in your community." },
  { icon: Users, title: "Peer Support", description: "Provide peer support in our Open Circle Conversations and community forums." },
  { icon: Heart, title: "Administrative", description: "Assist with administrative tasks, content creation, and social media management." },
];

const benefits = [
  "Make a meaningful difference in your community",
  "Gain experience in mental health advocacy",
  "Connect with like-minded individuals",
  "Receive training and professional development",
  "Flexible commitment hours",
  "Certificate of volunteer service",
];

const Volunteer = () => {
  const [acceptedTerms, setAcceptedTerms] = useState(false);
  const [formData, setFormData] = useState({
    firstName: "",
    lastName: "",
    email: "",
    phone: "",
    interestArea: "",
    availability: "",
    experience: "",
    motivation: ""
  });
  const { toast } = useToast();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!acceptedTerms) {
      toast({ title: "Please accept the Terms & Conditions", variant: "destructive" });
      return;
    }

    try {
      const volunteerData = {
        full_name: `${formData.firstName} ${formData.lastName}`,
        email: formData.email,
        phone: formData.phone,
        interest_area: formData.interestArea,
        availability: formData.availability,
        experience: formData.experience,
        motivation: formData.motivation
      };

      await volunteerAPI.submitApplication(volunteerData);
      
      toast({ 
        title: "Application submitted!", 
        description: "We'll be in touch soon." 
      });

      // Reset form
      setFormData({
        firstName: "",
        lastName: "",
        email: "",
        phone: "",
        interestArea: "",
        availability: "",
        experience: "",
        motivation: ""
      });
      setAcceptedTerms(false);
    } catch (error) {
      console.error("Error submitting volunteer application:", error);
      toast({ 
        title: "Submission failed", 
        description: "Please try again later.",
        variant: "destructive"
      });
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setFormData({
      ...formData,
      [e.target.id]: e.target.value
    });
  };

  return (
    <Layout>
      <section className="relative py-20 md:py-28 overflow-hidden">
        <div 
          className="absolute inset-0 bg-cover bg-center"
          style={{ backgroundImage: `url(${volunteerBg})` }}
        />
        <div className="absolute inset-0 bg-gradient-to-t from-background/95 via-background/80 to-background/70" />
        <div className="container mx-auto px-4 relative z-10">
          <div className="max-w-3xl mx-auto text-center">
            <Heart className="w-12 h-12 text-primary mx-auto mb-6 animate-float" />
            <h1 className="font-display text-4xl md:text-5xl font-semibold text-foreground mb-6">Volunteer With Us</h1>
            <p className="text-lg text-muted-foreground">Join our community of compassionate volunteers and help us make mental health support accessible to everyone.</p>
          </div>
        </div>
      </section>

      <section className="py-20 md:py-28">
        <div className="container mx-auto px-4">
          <ScrollReveal><div className="text-center mb-16"><h2 className="font-display text-3xl md:text-4xl font-semibold text-foreground mb-4">Volunteer Opportunities</h2></div></ScrollReveal>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {opportunities.map((opp, i) => (
              <ScrollReveal key={i} delay={i * 100}>
                <div className="p-6 rounded-2xl bg-card border border-border text-center card-hover h-full">
                  <div className="w-14 h-14 rounded-xl bg-primary/10 flex items-center justify-center mx-auto mb-4"><opp.icon className="w-6 h-6 text-primary" /></div>
                  <h3 className="font-semibold text-foreground mb-2">{opp.title}</h3>
                  <p className="text-sm text-muted-foreground">{opp.description}</p>
                </div>
              </ScrollReveal>
            ))}
          </div>
        </div>
      </section>

      <section className="py-20 md:py-28 bg-card border-y border-border">
        <div className="container mx-auto px-4">
          <div className="grid lg:grid-cols-2 gap-12 items-start max-w-6xl mx-auto">
            <ScrollReveal>
              <h2 className="font-display text-3xl font-semibold text-foreground mb-6">Why Volunteer?</h2>
              <ul className="space-y-4">
                {benefits.map((benefit, i) => (
                  <li key={i} className="flex items-center gap-3"><CheckCircle className="w-5 h-5 text-primary flex-shrink-0" /><span className="text-foreground">{benefit}</span></li>
                ))}
              </ul>
            </ScrollReveal>
            <ScrollReveal delay={200}>
              <div className="p-8 rounded-2xl bg-background border border-border shadow-soft">
                <h3 className="font-display text-2xl font-semibold text-foreground mb-6">Apply to Volunteer</h3>
                <form className="space-y-5" onSubmit={handleSubmit}>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2"><Label htmlFor="firstName">First Name</Label><Input id="firstName" value={formData.firstName} onChange={handleInputChange} placeholder="Your first name" required /></div>
                    <div className="space-y-2"><Label htmlFor="lastName">Last Name</Label><Input id="lastName" value={formData.lastName} onChange={handleInputChange} placeholder="Your last name" required /></div>
                  </div>
                  <div className="space-y-2"><Label htmlFor="email">Email Address</Label><Input id="email" type="email" value={formData.email} onChange={handleInputChange} placeholder="you@example.com" required /></div>
                  <div className="space-y-2"><Label htmlFor="phone">Phone Number</Label><Input id="phone" type="tel" value={formData.phone} onChange={handleInputChange} placeholder="+1 (234) 567-890" required /></div>
                  <div className="space-y-2"><Label htmlFor="interestArea">Area of Interest</Label>
                    <select id="interestArea" value={formData.interestArea} onChange={handleInputChange} className="flex h-11 w-full rounded-lg border border-input bg-background px-4 py-2 text-sm ring-offset-background focus:outline-none focus:ring-2 focus:ring-primary" required>
                      <option value="">Select an area</option><option value="events">Event Support</option><option value="outreach">Outreach</option><option value="peer">Peer Support</option><option value="admin">Administrative</option>
                    </select>
                  </div>
                  <div className="space-y-2"><Label htmlFor="availability">Availability</Label><Input id="availability" value={formData.availability} onChange={handleInputChange} placeholder="e.g., Weekends, Evenings" required /></div>
                  <div className="space-y-2"><Label htmlFor="experience">Previous Experience</Label><Textarea id="experience" value={formData.experience} onChange={handleInputChange} placeholder="Tell us about your relevant experience..." rows={3} required /></div>
                  <div className="space-y-2"><Label htmlFor="motivation">Why do you want to volunteer?</Label><Textarea id="motivation" value={formData.motivation} onChange={handleInputChange} placeholder="Tell us about your motivation..." rows={4} required /></div>
                  <div className="flex items-start gap-3">
                    <Checkbox id="terms" checked={acceptedTerms} onCheckedChange={(c) => setAcceptedTerms(c === true)} className="mt-1" />
                    <Label htmlFor="terms" className="text-sm text-muted-foreground leading-relaxed">I agree to the <Link to="/terms" className="text-primary hover:underline">Terms & Conditions</Link> and <Link to="/privacy" className="text-primary hover:underline">Privacy Policy</Link></Label>
                  </div>
                  <Button variant="hero" className="w-full" type="submit">Submit Application<ArrowRight className="w-4 h-4" /></Button>
                </form>
              </div>
            </ScrollReveal>
          </div>
        </div>
      </section>
    </Layout>
  );
};

export default Volunteer;
