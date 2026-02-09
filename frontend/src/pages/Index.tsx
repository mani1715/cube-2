import { Link } from "react-router-dom";
import { Layout } from "@/components/layout/Layout";
import { Button } from "@/components/ui/button";
import { ScrollReveal } from "@/components/ui/scroll-reveal";
import { ArrowRight, Users, Calendar, BookOpen, Shield, Sparkles, Heart } from "lucide-react";
import heroBg from "@/assets/bg-home-hero.jpg";
import SEO from "@/components/SEO";
import ImpactStats from "@/components/ImpactStats";
import Testimonials from "@/components/Testimonials";
import PrivacyHighlights from "@/components/PrivacyHighlights";

const features = [
  {
    icon: Users,
    title: "1:1 Therapy",
    description: "Personal sessions with licensed psychologists tailored to your needs.",
  },
  {
    icon: Calendar,
    title: "Group Sessions",
    description: "Connect with others in guided group therapy environments.",
  },
  {
    icon: BookOpen,
    title: "Premium Articles",
    description: "Expert insights and resources from our mental health events.",
  },
  {
    icon: Shield,
    title: "Safe Space",
    description: "Confidential and judgment-free support for your journey.",
  },
];

const stats = [
  { value: "5,000+", label: "Lives Impacted" },
  { value: "50+", label: "Expert Psychologists" },
  { value: "200+", label: "Events Hosted" },
  { value: "98%", label: "Client Satisfaction" },
];

const Index = () => {
  return (
    <Layout>
      <SEO 
        title="Home"
        description="A-Cube Mental Health Platform - Professional therapy services, licensed psychologists, and wellness programs. Book your therapy session today and start your journey to mental wellness."
        keywords={['mental health services', 'online therapy', 'licensed psychologists', 'counseling', 'therapy sessions', 'mental wellness', 'group therapy', 'individual therapy']}
      />
      {/* Main Content */}
      <main id="main-content">
        {/* Hero Section */}
        <section 
          className="relative min-h-[90vh] flex items-center overflow-hidden"
          aria-labelledby="hero-heading"
        >
          <div 
            className="absolute inset-0 bg-cover bg-center"
            style={{ backgroundImage: `url(${heroBg})` }}
            role="img"
            aria-label="Background image showing peaceful mental wellness"
          />
          <div className="absolute inset-0 bg-gradient-to-br from-background/90 via-background/70 to-transparent" />
          
          <div className="container mx-auto px-4 relative z-10">
            <div className="max-w-3xl">
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full gradient-accent text-primary text-sm font-medium mb-6 animate-fade-up opacity-0" style={{ animationDelay: "0s", animationFillMode: "forwards" }}>
                <Sparkles className="w-4 h-4" aria-hidden="true" />
                Compassionate Mental Health Care
              </div>
              
              <h1 
                id="hero-heading"
                className="font-display text-4xl md:text-5xl lg:text-6xl font-semibold text-foreground mb-6 animate-fade-up opacity-0" 
                style={{ animationDelay: "0.1s", animationFillMode: "forwards" }}
              >
                Your Journey to
                <span className="text-gradient block mt-2">Mental Wellness</span>
                Starts Here
              </h1>
              
              <p className="text-lg md:text-xl text-muted-foreground mb-8 max-w-2xl animate-fade-up opacity-0" style={{ animationDelay: "0.2s", animationFillMode: "forwards" }}>
                We provide compassionate therapy, transformative events, and a supportive community to help you thrive. Take the first step towards a healthier mind.
              </p>
              
              <div className="flex flex-wrap gap-4 animate-fade-up opacity-0" style={{ animationDelay: "0.3s", animationFillMode: "forwards" }}>
                <Link to="/services">
                  <Button variant="hero" size="lg" aria-label="Explore our therapy services">
                    Explore Services
                    <ArrowRight className="w-5 h-5" aria-hidden="true" />
                  </Button>
                </Link>
                <Link to="/events">
                  <Button variant="outline" size="lg" aria-label="View upcoming events">
                    Upcoming Events
                  </Button>
                </Link>
              </div>
            </div>
          </div>

          {/* Floating decorative elements */}
          <div className="absolute right-10 top-1/4 w-32 h-32 rounded-full bg-primary/10 blur-3xl animate-float" aria-hidden="true" />
          <div className="absolute right-1/4 bottom-1/4 w-48 h-48 rounded-full bg-accent/40 blur-3xl animate-float" style={{ animationDelay: "2s" }} aria-hidden="true" />
        </section>

        {/* Stats Section */}
        <section 
          className="py-16 gradient-card border-y border-border"
          aria-labelledby="stats-heading"
        >
          <h2 id="stats-heading" className="sr-only">Our Impact Statistics</h2>
          <div className="container mx-auto px-4">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <ScrollReveal key={index} delay={index * 100}>
                <div className="text-center">
                  <div className="font-display text-3xl md:text-4xl font-semibold text-gradient mb-2">
                    {stat.value}
                  </div>
                  <div className="text-muted-foreground text-sm">{stat.label}</div>
                </div>
              </ScrollReveal>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section 
        className="py-20 md:py-28"
        aria-labelledby="features-heading"
      >
        <div className="container mx-auto px-4">
          <ScrollReveal>
            <div className="text-center mb-16">
              <h2 
                id="features-heading"
                className="font-display text-3xl md:text-4xl font-semibold text-foreground mb-4"
              >
                How We Support You
              </h2>
              <p className="text-muted-foreground max-w-2xl mx-auto">
                Our comprehensive approach to mental wellness combines professional therapy, community support, and educational resources.
              </p>
            </div>
          </ScrollReveal>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, index) => (
              <ScrollReveal key={index} delay={index * 100}>
                <article className="group p-8 rounded-2xl gradient-card border border-border card-hover h-full">
                  <div className="w-14 h-14 rounded-xl gradient-accent flex items-center justify-center mb-6 group-hover:gradient-primary group-hover:scale-110 transition-all duration-300">
                    <feature.icon className="w-6 h-6 text-primary group-hover:text-primary-foreground transition-colors" aria-hidden="true" />
                  </div>
                  <h3 className="font-display text-xl font-semibold text-foreground mb-3">
                    {feature.title}
                  </h3>
                  <p className="text-muted-foreground text-sm leading-relaxed">
                    {feature.description}
                  </p>
                </article>
              </ScrollReveal>
            ))}
          </div>
        </div>
      </section>

      {/* Impact Stats Section - Phase 10.1 */}
      <ImpactStats />

      {/* Testimonials Section - Phase 10.1 */}
      <Testimonials />

      {/* Privacy & Ethics Highlights - Phase 10.1 */}
      <PrivacyHighlights />

      {/* CTA Section */}
      <section 
        className="py-20 md:py-28 gradient-cta relative overflow-hidden"
        aria-labelledby="cta-heading"
      >
        {/* Decorative background */}
        <div className="absolute inset-0 opacity-15" aria-hidden="true">
          <div className="absolute top-0 left-0 w-64 h-64 rounded-full bg-white blur-3xl" />
          <div className="absolute bottom-0 right-0 w-96 h-96 rounded-full bg-white blur-3xl" />
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-72 h-72 rounded-full bg-white/50 blur-3xl" />
        </div>
        
        <div className="container mx-auto px-4 text-center relative z-10">
          <ScrollReveal>
            <Heart className="w-12 h-12 text-primary-foreground/80 mx-auto mb-6 animate-float" aria-hidden="true" />
            <h2 
              id="cta-heading"
              className="font-display text-3xl md:text-4xl font-semibold text-primary-foreground mb-4"
            >
              Ready to Begin Your Healing Journey?
            </h2>
            <p className="text-primary-foreground/80 max-w-2xl mx-auto mb-8">
              Join thousands who have found support, growth, and healing with A-Cube. Your well-being matters.
            </p>
            <div className="flex flex-wrap justify-center gap-4">
              <Link to="/book-session">
                <Button 
                  variant="secondary" 
                  size="lg" 
                  className="shadow-elevated hover:shadow-soft"
                  aria-label="Book a therapy session"
                >
                  Book a Session
                  <ArrowRight className="w-5 h-5" aria-hidden="true" />
                </Button>
              </Link>
              <Link to="/volunteer">
                <Button 
                  variant="ghost" 
                  size="lg" 
                  className="text-primary-foreground border-2 border-primary-foreground/30 hover:bg-primary-foreground/10"
                  aria-label="Volunteer with us"
                >
                  Volunteer With Us
                </Button>
              </Link>
            </div>
          </ScrollReveal>
        </div>
      </section>
    </Layout>
  );
};

export default Index;
