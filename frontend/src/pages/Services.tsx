import { Layout } from "@/components/layout/Layout";
import { Button } from "@/components/ui/button";
import { ScrollReveal } from "@/components/ui/scroll-reveal";
import { Link } from "react-router-dom";
import { User, Users, BookOpen, Check, ArrowRight, Clock, Video, Shield, Heart, HandHeart, Sparkles } from "lucide-react";
import servicesBg from "@/assets/bg-services.jpg";
import individualBg from "@/assets/bg-therapy-individual.jpg";
import groupBg from "@/assets/bg-group-therapy.jpg";
import TrustBadge from "@/components/TrustBadge";
import PrivacyHighlights from "@/components/PrivacyHighlights";

const services = [
  {
    id: "individual",
    icon: User,
    title: "1:1 Therapy Sessions",
    tagline: "Personalized support for your unique journey",
    description: "Our one-on-one therapy sessions provide a safe, confidential space where you can explore your thoughts, feelings, and challenges with a compassionate, licensed psychologist. Every session is tailored to your individual needs.",
    image: individualBg,
    whatIncludes: [
      "50-minute sessions with licensed mental health professionals",
      "Personalized treatment approaches based on your needs",
      "Flexible scheduling including evenings and weekends",
      "Both in-person and secure virtual session options",
      "Ongoing progress tracking and collaborative goal setting",
      "Complete confidentiality in a judgment-free environment",
    ],
    whoIsItFor: "Individuals experiencing anxiety, depression, stress, grief, relationship challenges, life transitions, or anyone seeking personal growth and self-understanding.",
    howItWorks: "After an initial consultation, you'll be matched with a psychologist who specializes in your area of concern. Sessions are scheduled at your convenience, and your therapist will work with you to develop a personalized plan for healing and growth.",
    whatToExpect: "A warm, welcoming environment where you can share openly without fear of judgment. Your therapist will listen deeply, offer evidence-based strategies, and support you every step of the way.",
  },
  {
    id: "group",
    icon: Users,
    title: "Group Therapy",
    tagline: "Healing together, growing stronger",
    description: "Group therapy offers a unique opportunity to connect with others who share similar experiences. Facilitated by experienced therapists, these sessions foster community, mutual support, and shared healing.",
    image: groupBg,
    whatIncludes: [
      "Small, intimate groups of 6-10 participants",
      "Topic-focused sessions addressing specific challenges",
      "Facilitation by experienced, empathetic therapists",
      "Weekly or bi-weekly meeting options",
      "Safe space to share and learn from others' experiences",
      "Building lasting connections and support networks",
    ],
    whoIsItFor: "Individuals who find strength in community, those experiencing grief, anxiety, depression, or life transitions, and anyone who values shared experiences and peer support.",
    howItWorks: "After a brief screening to ensure group fit, you'll join a carefully curated group addressing your specific area of concern. Sessions are structured yet flexible, allowing for both guided discussion and organic connection.",
    whatToExpect: "A supportive circle where you're never alone. You'll discover that others share your struggles, gain new perspectives, and build meaningful relationships with fellow participants.",
  },
  {
    id: "articles",
    icon: BookOpen,
    title: "Resources & Articles",
    tagline: "Knowledge for your mental wellness journey",
    description: "Access our curated library of expert-written articles, guides, and resources designed to support your mental health education and self-care practices between sessions.",
    whatIncludes: [
      "Expert-written mental health articles and guides",
      "Summaries and insights from our workshops and events",
      "Downloadable self-help worksheets and exercises",
      "Guided meditation and mindfulness resources",
      "Educational content on various mental health topics",
      "Practical tips for daily emotional wellness",
    ],
    whoIsItFor: "Anyone seeking to deepen their understanding of mental health, individuals between therapy sessions, caregivers supporting loved ones, and those curious about emotional wellness.",
    howItWorks: "Browse our resource library at any time. New content is added regularly based on community needs, current research, and feedback from our therapeutic community.",
    whatToExpect: "Accessible, compassionate, and evidence-based content that empowers you to take an active role in your mental wellness journey.",
  },
];

const missionValues = [
  {
    icon: Heart,
    title: "Accessible Care",
    description: "We believe mental health support should be available to everyone, regardless of financial circumstances.",
  },
  {
    icon: HandHeart,
    title: "Community-Driven",
    description: "Our organization is built on the foundation of mutual support, compassion, and collective healing.",
  },
  {
    icon: Sparkles,
    title: "Evidence-Based",
    description: "All our services are grounded in proven therapeutic approaches and delivered by qualified professionals.",
  },
];

const benefits = [
  {
    icon: Clock,
    title: "Flexible Scheduling",
    description: "Sessions that fit your lifestyle with evening and weekend availability.",
  },
  {
    icon: Video,
    title: "Virtual Options",
    description: "Connect from anywhere with secure, private video therapy sessions.",
  },
  {
    icon: Shield,
    title: "Complete Privacy",
    description: "Your confidentiality is protected with strict ethical practices.",
  },
];

const Services = () => {
  return (
    <Layout>
      {/* Hero Section */}
      <section className="relative py-20 md:py-28 overflow-hidden">
        <div 
          className="absolute inset-0 bg-cover bg-center"
          style={{ backgroundImage: `url(${servicesBg})` }}
        />
        <div className="absolute inset-0 bg-gradient-to-b from-background/90 via-background/70 to-background" />
        <div className="container mx-auto px-4 relative z-10">
          <div className="max-w-3xl mx-auto text-center">
            <h1 className="font-display text-4xl md:text-5xl font-semibold text-foreground mb-6 animate-fade-up opacity-0" style={{ animationDelay: "0s", animationFillMode: "forwards" }}>
              Our Services
            </h1>
            <p className="text-lg text-muted-foreground animate-fade-up opacity-0" style={{ animationDelay: "0.1s", animationFillMode: "forwards" }}>
              As a non-profit organization, we are committed to providing compassionate, accessible mental health support to everyone in our community. Our services are designed to meet you where you are on your wellness journey.
            </p>
          </div>
        </div>
      </section>

      {/* Mission Statement */}
      <section className="py-16 bg-card border-y border-border">
        <div className="container mx-auto px-4">
          <ScrollReveal>
            <div className="max-w-3xl mx-auto text-center">
              <h2 className="font-display text-2xl md:text-3xl font-semibold text-foreground mb-4">
                Our Mission
              </h2>
              <p className="text-muted-foreground leading-relaxed">
                A-Cube is dedicated to breaking down barriers to mental health care. We believe that everyone deserves access to quality psychological support, and we work tirelessly to make that vision a reality. Through the generosity of our supporters and the dedication of our team, we provide services that prioritize healing over profit.
              </p>
            </div>
          </ScrollReveal>

          <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto mt-12">
            {missionValues.map((value, index) => (
              <ScrollReveal key={index} delay={index * 100}>
                <div className="text-center">
                  <div className="w-16 h-16 rounded-2xl bg-accent flex items-center justify-center mx-auto mb-4">
                    <value.icon className="w-7 h-7 text-primary" />
                  </div>
                  <h3 className="font-semibold text-foreground mb-2">{value.title}</h3>
                  <p className="text-sm text-muted-foreground">{value.description}</p>
                </div>
              </ScrollReveal>
            ))}
          </div>
        </div>
      </section>

      {/* Services Detailed Sections */}
      <section className="py-20 md:py-28">
        <div className="container mx-auto px-4">
          <div className="space-y-24">
            {services.map((service, index) => (
              <ScrollReveal key={service.id}>
                <div className={`grid lg:grid-cols-2 gap-12 items-center ${index % 2 === 1 ? 'lg:flex-row-reverse' : ''}`}>
                  {/* Content Side */}
                  <div className={index % 2 === 1 ? 'lg:order-2' : ''}>
                    <div className="flex items-center gap-3 mb-4">
                      <div className="w-12 h-12 rounded-xl bg-accent flex items-center justify-center">
                        <service.icon className="w-5 h-5 text-primary" />
                      </div>
                      <span className="text-sm font-medium text-primary">{service.tagline}</span>
                    </div>
                    
                    <h2 className="font-display text-3xl md:text-4xl font-semibold text-foreground mb-4">
                      {service.title}
                    </h2>
                    
                    <p className="text-muted-foreground mb-8 leading-relaxed">
                      {service.description}
                    </p>

                    {/* What It Includes */}
                    <div className="mb-8">
                      <h3 className="font-semibold text-foreground mb-4">What It Includes</h3>
                      <ul className="space-y-3">
                        {service.whatIncludes.map((item, idx) => (
                          <li key={idx} className="flex items-start gap-3 text-sm">
                            <Check className="w-5 h-5 text-primary flex-shrink-0 mt-0.5" />
                            <span className="text-foreground">{item}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>

                  {/* Image/Info Side */}
                  <div className={`space-y-6 ${index % 2 === 1 ? 'lg:order-1' : ''}`}>
                    {service.image && (
                      <div className="rounded-2xl overflow-hidden shadow-elevated mb-6">
                        <img 
                          src={service.image} 
                          alt={service.title}
                          className="w-full h-64 object-cover"
                        />
                      </div>
                    )}
                    
                    <div className="p-6 rounded-2xl bg-card border border-border">
                      <h4 className="font-semibold text-foreground mb-2">Who Is It For?</h4>
                      <p className="text-sm text-muted-foreground mb-4">{service.whoIsItFor}</p>
                      
                      <h4 className="font-semibold text-foreground mb-2">How It Works</h4>
                      <p className="text-sm text-muted-foreground mb-4">{service.howItWorks}</p>
                      
                      <h4 className="font-semibold text-foreground mb-2">What to Expect</h4>
                      <p className="text-sm text-muted-foreground">{service.whatToExpect}</p>
                    </div>

                    <Link to={service.id === "articles" ? "/blogs" : "/book-session"}>
                      <Button variant="hero" className="w-full">
                        {service.id === "articles" ? "Explore Articles" : "Get Started"}
                        <ArrowRight className="w-4 h-4" />
                      </Button>
                    </Link>
                  </div>
                </div>
              </ScrollReveal>
            ))}
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="py-20 md:py-28 bg-card border-y border-border">
        <div className="container mx-auto px-4">
          <ScrollReveal>
            <div className="text-center mb-16">
              <h2 className="font-display text-3xl md:text-4xl font-semibold text-foreground mb-4">
                Why Choose A-Cube?
              </h2>
              <p className="text-muted-foreground max-w-2xl mx-auto">
                We prioritize your comfort, convenience, and healing above all else.
              </p>
            </div>
          </ScrollReveal>

          <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
            {benefits.map((benefit, index) => (
              <ScrollReveal key={index} delay={index * 100}>
                <div className="text-center">
                  <div className="w-16 h-16 rounded-2xl bg-accent flex items-center justify-center mx-auto mb-4">
                    <benefit.icon className="w-7 h-7 text-primary" />
                  </div>
                  <h3 className="font-semibold text-foreground mb-2">{benefit.title}</h3>
                  <p className="text-sm text-muted-foreground">{benefit.description}</p>
                </div>
              </ScrollReveal>
            ))}
          </div>

          {/* Trust Badges */}
          <ScrollReveal delay={300}>
            <div className="flex flex-wrap justify-center gap-3 mt-12">
              <TrustBadge type="licensed" size="md" />
              <TrustBadge type="verified" size="md" />
              <TrustBadge type="certified" size="md" />
            </div>
          </ScrollReveal>
        </div>
      </section>

      {/* Privacy & Ethics - Phase 10.1 */}
      <PrivacyHighlights />

      {/* CTA Section */}
      <section className="py-20 md:py-28">
        <div className="container mx-auto px-4 text-center">
          <ScrollReveal>
            <h2 className="font-display text-3xl md:text-4xl font-semibold text-foreground mb-4">
              Ready to Begin Your Healing Journey?
            </h2>
            <p className="text-muted-foreground max-w-2xl mx-auto mb-8">
              Reach out to our caring team for a free consultation. We're here to listen, understand your needs, and help you find the right support for your journey toward wellness.
            </p>
            <Link to="/book-session">
              <Button variant="hero" size="lg">
                Book a Session
                <ArrowRight className="w-5 h-5" />
              </Button>
            </Link>
          </ScrollReveal>
        </div>
      </section>
    </Layout>
  );
};

export default Services;
