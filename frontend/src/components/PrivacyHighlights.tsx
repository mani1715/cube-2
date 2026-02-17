import { ScrollReveal } from "@/components/ui/scroll-reveal";
import { Shield, Lock, Eye, UserCheck, FileCheck, Heart } from "lucide-react";
import { Card } from "@/components/ui/card";

interface HighlightItem {
  icon: React.ElementType;
  title: string;
  description: string;
}

const highlights: HighlightItem[] = [
  {
    icon: Lock,
    title: "Complete Confidentiality",
    description: "Your sessions and personal information are protected with end-to-end encryption and strict privacy protocols.",
  },
  {
    icon: UserCheck,
    title: "Ethical Standards",
    description: "All our professionals adhere to strict ethical guidelines and codes of conduct set by regulatory bodies.",
  },
  {
    icon: Shield,
    title: "Safe & Secure Platform",
    description: "Our platform is built with industry-leading security measures to ensure your data is always protected.",
  },
  {
    icon: Eye,
    title: "No Judgment Zone",
    description: "We provide a welcoming, non-judgmental space where you can express yourself freely without fear.",
  },
  {
    icon: FileCheck,
    title: "GDPR Compliant",
    description: "We follow international data protection standards and give you full control over your personal data.",
  },
  {
    icon: Heart,
    title: "Client-Centered Care",
    description: "Your well-being is our priority. We tailor our approach to your unique needs and preferences.",
  },
];

const PrivacyHighlights = () => {
  return (
    <section className="py-20 md:py-28">
      <div className="container mx-auto px-4">
        <ScrollReveal>
          <div className="text-center mb-16">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full gradient-accent text-primary text-sm font-medium mb-4">
              <Shield className="w-4 h-4" />
              Your Privacy & Safety
            </div>
            <h2 className="font-display text-3xl md:text-4xl font-semibold text-foreground mb-4">
              Built on Trust & Ethics
            </h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              We take your privacy seriously. Our commitment to confidentiality, security, and ethical care ensures you can focus on your healing journey with peace of mind.
            </p>
          </div>
        </ScrollReveal>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {highlights.map((item, index) => (
            <ScrollReveal key={index} delay={index * 100}>
              <Card className="p-6 gradient-card border border-border hover:shadow-soft transition-all duration-300 group">
                {/* Icon */}
                <div className="w-12 h-12 rounded-xl gradient-accent flex items-center justify-center mb-4 group-hover:gradient-primary group-hover:scale-110 transition-all duration-300">
                  <item.icon className="w-6 h-6 text-primary group-hover:text-primary-foreground transition-colors" />
                </div>

                {/* Title */}
                <h3 className="font-display text-lg font-semibold text-foreground mb-2">
                  {item.title}
                </h3>

                {/* Description */}
                <p className="text-sm text-muted-foreground leading-relaxed">
                  {item.description}
                </p>
              </Card>
            </ScrollReveal>
          ))}
        </div>

        {/* Additional Info */}
        <ScrollReveal delay={200}>
          <div className="mt-12 text-center max-w-3xl mx-auto">
            <div className="p-6 rounded-2xl gradient-card border border-border">
              <p className="text-muted-foreground text-sm leading-relaxed">
                <strong className="text-foreground">Our Promise:</strong> We maintain the highest standards of confidentiality and will never share your information without your explicit consent, except where required by law. Your trust is the foundation of our work.
              </p>
            </div>
          </div>
        </ScrollReveal>
      </div>
    </section>
  );
};

export default PrivacyHighlights;
