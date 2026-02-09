import { useState } from "react";
import { Layout } from "@/components/layout/Layout";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { ScrollReveal } from "@/components/ui/scroll-reveal";
import { Link } from "react-router-dom";
import { ArrowRight, Briefcase, Heart, Users, Clock, Award, CheckCircle } from "lucide-react";
import careersBg from "@/assets/bg-careers.jpg";

const benefits = [
  { icon: Clock, title: "Flexible Schedule", description: "Set your own hours and work-life balance." },
  { icon: Heart, title: "Meaningful Work", description: "Make a real difference in people's lives." },
  { icon: Users, title: "Supportive Community", description: "Join a team of passionate professionals." },
  { icon: Award, title: "Professional Growth", description: "Continuous learning and development opportunities." },
];

const requirements = [
  "Licensed psychologist (PhD, PsyD, or equivalent)",
  "Minimum 2 years of clinical experience",
  "Valid state licensure in good standing",
  "Experience with telehealth platforms preferred",
  "Strong communication and empathy skills",
  "Commitment to ethical practice",
];

const openPositions = [
  { title: "Clinical Psychologist", type: "Full-time / Part-time", location: "Remote / Hybrid", description: "Join our team to provide individual therapy sessions to clients seeking mental health support." },
  { title: "Group Therapy Facilitator", type: "Part-time", location: "Remote", description: "Lead group therapy sessions focused on various mental health topics." },
  { title: "Child & Adolescent Specialist", type: "Full-time", location: "San Francisco, CA", description: "Specialize in providing therapy to young clients and their families." },
];

const Careers = () => {
  const [acceptedTerms, setAcceptedTerms] = useState(false);

  return (
    <Layout>
      <section className="relative py-20 md:py-28 overflow-hidden">
        <div 
          className="absolute inset-0 bg-cover bg-center"
          style={{ backgroundImage: `url(${careersBg})` }}
        />
        <div className="absolute inset-0 bg-gradient-to-br from-background/90 via-background/75 to-background/60" />
        <div className="container mx-auto px-4 relative z-10">
          <div className="max-w-3xl mx-auto text-center">
            <h1 className="font-display text-4xl md:text-5xl font-semibold text-foreground mb-6 animate-fade-up">Join Our Team</h1>
            <p className="text-lg text-muted-foreground mb-8 animate-fade-up" style={{ animationDelay: "0.1s" }}>Are you a passionate mental health professional looking to make a difference?</p>
            <Link to="/psychologist-portal"><Button variant="hero" size="lg">Psychologist Portal<ArrowRight className="w-5 h-5" /></Button></Link>
          </div>
        </div>
      </section>

      <section className="py-20 md:py-28">
        <div className="container mx-auto px-4">
          <ScrollReveal><div className="text-center mb-16"><h2 className="font-display text-3xl md:text-4xl font-semibold text-foreground mb-4">Why Work With Us?</h2></div></ScrollReveal>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {benefits.map((b, i) => (
              <ScrollReveal key={i} delay={i * 100}>
                <div className="p-6 rounded-2xl bg-card border border-border text-center card-hover h-full">
                  <div className="w-14 h-14 rounded-xl bg-primary/10 flex items-center justify-center mx-auto mb-4"><b.icon className="w-6 h-6 text-primary" /></div>
                  <h3 className="font-semibold text-foreground mb-2">{b.title}</h3>
                  <p className="text-sm text-muted-foreground">{b.description}</p>
                </div>
              </ScrollReveal>
            ))}
          </div>
        </div>
      </section>

      <section className="py-20 md:py-28 bg-card border-y border-border">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-2 gap-12 items-center max-w-5xl mx-auto">
            <ScrollReveal>
              <h2 className="font-display text-3xl font-semibold text-foreground mb-6">What We Look For</h2>
              <ul className="space-y-4">
                {requirements.map((r, i) => <li key={i} className="flex items-start gap-3"><CheckCircle className="w-5 h-5 text-primary flex-shrink-0 mt-0.5" /><span className="text-foreground">{r}</span></li>)}
              </ul>
            </ScrollReveal>
            <ScrollReveal delay={200}>
              <div className="p-8 rounded-2xl bg-primary/5 border border-primary/20">
                <Briefcase className="w-12 h-12 text-primary mb-4" />
                <h3 className="font-display text-xl font-semibold text-foreground mb-4">Ready to Apply?</h3>
                <p className="text-muted-foreground mb-4">If you meet these qualifications, we'd love to hear from you.</p>
                <div className="flex items-start gap-3 mb-6">
                  <Checkbox id="terms" checked={acceptedTerms} onCheckedChange={(c) => setAcceptedTerms(c === true)} className="mt-1" />
                  <Label htmlFor="terms" className="text-sm text-muted-foreground">I agree to the <Link to="/terms" className="text-primary hover:underline">Terms & Conditions</Link></Label>
                </div>
                <Link to="/psychologist-portal"><Button variant="hero" className="w-full" disabled={!acceptedTerms}>Access Psychologist Portal<ArrowRight className="w-4 h-4" /></Button></Link>
              </div>
            </ScrollReveal>
          </div>
        </div>
      </section>

      <section className="py-20 md:py-28">
        <div className="container mx-auto px-4">
          <ScrollReveal><div className="text-center mb-16"><h2 className="font-display text-3xl font-semibold text-foreground mb-4">Open Positions</h2></div></ScrollReveal>
          <div className="max-w-3xl mx-auto space-y-4">
            {openPositions.map((p, i) => (
              <ScrollReveal key={i} delay={i * 100}>
                <div className="p-6 rounded-xl bg-card border border-border card-hover">
                  <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div>
                      <h3 className="font-semibold text-foreground text-lg mb-1">{p.title}</h3>
                      <p className="text-sm text-primary mb-2">{p.type} • {p.location}</p>
                      <p className="text-sm text-muted-foreground">{p.description}</p>
                    </div>
                    <Button variant="outline" size="sm" className="flex-shrink-0">Apply Now<ArrowRight className="w-4 h-4" /></Button>
                  </div>
                </div>
              </ScrollReveal>
            ))}
          </div>
        </div>
      </section>
    </Layout>
  );
};

export default Careers;
