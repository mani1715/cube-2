import { Layout } from "@/components/layout/Layout";
import { Button } from "@/components/ui/button";
import { ScrollReveal } from "@/components/ui/scroll-reveal";
import { Link } from "react-router-dom";
import { Users, Target, Heart, Award, ArrowRight, Linkedin } from "lucide-react";
import aboutBg from "@/assets/bg-about.jpg";
import ImpactStats from "@/components/ImpactStats";
import Testimonials from "@/components/Testimonials";

const values = [
  {
    icon: Heart,
    title: "Compassion",
    description: "We approach every interaction with empathy and genuine care for your well-being.",
  },
  {
    icon: Users,
    title: "Community",
    description: "Building connections that foster healing and mutual support among individuals.",
  },
  {
    icon: Target,
    title: "Excellence",
    description: "Delivering the highest quality mental health care through evidence-based practices.",
  },
  {
    icon: Award,
    title: "Integrity",
    description: "Maintaining the highest ethical standards in all our professional relationships.",
  },
];

const team = [
  {
    name: "Zahira Shaik",
    role: "Founder and Writer",
    bio: "Passionate about mental health advocacy and creating meaningful content that inspires healing.",
    linkedin: "https://linkedin.com/in/zahira-shaik",
  },
  {
    name: "Mohan Gola",
    role: "Financial Advisor",
    bio: "Ensuring sustainable growth and financial stability for our non-profit mission.",
    linkedin: "https://linkedin.com/in/mohan-gola",
  },
  {
    name: "Abhishek K",
    role: "CTO",
    bio: "Building technology solutions that make mental health support accessible to everyone.",
    linkedin: "https://linkedin.com/in/abhishek-k",
  },
  {
    name: "V",
    role: "Mentor",
    bio: "Guiding our team with wisdom and experience in community-driven mental health initiatives.",
    linkedin: "https://linkedin.com/in/v-mentor",
  },
];

const events = [
  "Panel Discussions with Expert Psychologists",
  "Professional Meetups for Mental Health Practitioners",
  "Educational Seminars and Workshops",
  "Open Circle Conversations",
  "Collaborative Book Writing Projects",
  "Virtual Gaming Nights for Community Building",
];

const About = () => {
  return (
    <Layout>
      {/* Hero Section */}
      <section className="relative py-20 md:py-28 overflow-hidden">
        <div 
          className="absolute inset-0 bg-cover bg-center"
          style={{ backgroundImage: `url(${aboutBg})` }}
        />
        <div className="absolute inset-0 bg-gradient-to-r from-background/95 via-background/80 to-background/60" />
        <div className="container mx-auto px-4 relative z-10">
          <div className="max-w-3xl mx-auto text-center">
            <h1 className="font-display text-4xl md:text-5xl font-semibold text-foreground mb-6 animate-fade-up opacity-0" style={{ animationDelay: "0s", animationFillMode: "forwards" }}>
              About A-Cube
            </h1>
            <p className="text-lg text-muted-foreground animate-fade-up opacity-0" style={{ animationDelay: "0.1s", animationFillMode: "forwards" }}>
              We are a dedicated team of mental health professionals committed to making quality psychological care accessible to everyone. Our mission is to destigmatize mental health and create a world where seeking help is celebrated.
            </p>
          </div>
        </div>
      </section>

      {/* Mission Section */}
      <section className="py-20 md:py-28">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <ScrollReveal>
              <div>
                <h2 className="font-display text-3xl md:text-4xl font-semibold text-foreground mb-6">
                  Our Mission
                </h2>
                <p className="text-muted-foreground mb-6 leading-relaxed">
                  At A-Cube, we believe that mental wellness is fundamental to living a fulfilling life. Our mission is to provide compassionate, accessible, and evidence-based mental health services that empower individuals to overcome challenges and thrive.
                </p>
                <p className="text-muted-foreground mb-8 leading-relaxed">
                  Founded in 2018, we have grown from a small practice to a comprehensive mental health platform, serving thousands of individuals through therapy, community events, and educational resources.
                </p>
                <Link to="/services">
                  <Button variant="hero">
                    Explore Our Services
                    <ArrowRight className="w-5 h-5" />
                  </Button>
                </Link>
              </div>
            </ScrollReveal>
            <div className="grid grid-cols-2 gap-4">
              {values.map((value, index) => (
                <ScrollReveal key={index} delay={index * 80}>
                  <div className="p-6 rounded-2xl bg-card border border-border card-hover h-full">
                    <div className="w-12 h-12 rounded-xl bg-accent flex items-center justify-center mb-4">
                      <value.icon className="w-5 h-5 text-primary" />
                    </div>
                    <h3 className="font-semibold text-foreground mb-2">{value.title}</h3>
                    <p className="text-sm text-muted-foreground">{value.description}</p>
                  </div>
                </ScrollReveal>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Team Section */}
      <section className="py-20 md:py-28 bg-card border-y border-border">
        <div className="container mx-auto px-4">
          <ScrollReveal>
            <div className="text-center mb-16">
              <h2 className="font-display text-3xl md:text-4xl font-semibold text-foreground mb-4">
                Meet Our Team
              </h2>
              <p className="text-muted-foreground max-w-2xl mx-auto">
                Our team of licensed professionals brings decades of combined experience in mental health care.
              </p>
            </div>
          </ScrollReveal>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {team.map((member, index) => (
              <ScrollReveal key={index} delay={index * 80}>
                <div className="group p-6 rounded-2xl bg-background border border-border text-center card-hover h-full">
                  <div className="w-20 h-20 rounded-full bg-accent mx-auto mb-4 flex items-center justify-center overflow-hidden group-hover:ring-2 group-hover:ring-primary/30 transition-all duration-300">
                    <span className="font-display text-2xl text-primary">
                      {member.name.split(" ").map(n => n[0]).join("")}
                    </span>
                  </div>
                  <h3 className="font-semibold text-foreground mb-1">{member.name}</h3>
                  <p className="text-sm text-primary mb-2">{member.role}</p>
                  <a 
                    href={member.linkedin} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-primary/10 text-primary hover:bg-primary hover:text-primary-foreground transition-all duration-300 mb-3"
                  >
                    <Linkedin className="w-4 h-4" />
                  </a>
                  <p className="text-sm text-muted-foreground">{member.bio}</p>
                </div>
              </ScrollReveal>
            ))}
          </div>
        </div>
      </section>

      {/* Events We Conduct */}
      <section className="py-20 md:py-28">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto">
            <ScrollReveal>
              <div className="text-center mb-12">
                <h2 className="font-display text-3xl md:text-4xl font-semibold text-foreground mb-4">
                  Events We Conduct
                </h2>
                <p className="text-muted-foreground">
                  We organize a variety of events to educate, connect, and support mental health awareness.
                </p>
              </div>
            </ScrollReveal>

            <div className="grid md:grid-cols-2 gap-4">
              {events.map((event, index) => (
                <ScrollReveal key={index} delay={index * 60}>
                  <div className="flex items-center gap-4 p-5 rounded-xl bg-card border border-border card-hover">
                    <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                      <span className="text-primary font-semibold">{index + 1}</span>
                    </div>
                    <span className="text-foreground">{event}</span>
                  </div>
                </ScrollReveal>
              ))}
            </div>

            <ScrollReveal delay={400}>
              <div className="text-center mt-12">
                <Link to="/events">
                  <Button variant="outline" size="lg">
                    View All Events
                    <ArrowRight className="w-5 h-5" />
                  </Button>
                </Link>
              </div>
            </ScrollReveal>
          </div>
        </div>
      </section>

      {/* Impact Stats - Phase 10.1 */}
      <ImpactStats />

      {/* Testimonials - Phase 10.1 */}
      <Testimonials />
    </Layout>
  );
};

export default About;