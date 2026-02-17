import { ScrollReveal } from "@/components/ui/scroll-reveal";
import { TrendingUp, Users, Award, Heart, CheckCircle, Calendar } from "lucide-react";
import { Card } from "@/components/ui/card";

interface StatItem {
  icon: React.ElementType;
  value: string;
  label: string;
  description: string;
  color: string;
}

const impactStats: StatItem[] = [
  {
    icon: Users,
    value: "5,000+",
    label: "Lives Impacted",
    description: "Individuals supported on their mental wellness journey",
    color: "text-primary",
  },
  {
    icon: Award,
    value: "50+",
    label: "Expert Psychologists",
    description: "Licensed and certified mental health professionals",
    color: "text-primary",
  },
  {
    icon: Calendar,
    value: "10,000+",
    label: "Sessions Conducted",
    description: "One-on-one and group therapy sessions completed",
    color: "text-primary",
  },
  {
    icon: Heart,
    value: "200+",
    label: "Events Hosted",
    description: "Workshops, seminars, and community gatherings",
    color: "text-primary",
  },
  {
    icon: CheckCircle,
    value: "98%",
    label: "Client Satisfaction",
    description: "Clients reporting positive outcomes and progress",
    color: "text-primary",
  },
  {
    icon: TrendingUp,
    value: "4.9/5",
    label: "Average Rating",
    description: "Based on verified client feedback and reviews",
    color: "text-primary",
  },
];

const ImpactStats = () => {
  return (
    <section className="py-20 md:py-28 gradient-warm relative overflow-hidden">
      {/* Decorative elements */}
      <div className="absolute top-0 right-0 w-64 h-64 rounded-full bg-primary/5 blur-3xl" />
      <div className="absolute bottom-0 left-0 w-96 h-96 rounded-full bg-accent/30 blur-3xl" />

      <div className="container mx-auto px-4 relative z-10">
        <ScrollReveal>
          <div className="text-center mb-16">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full gradient-accent text-primary text-sm font-medium mb-4">
              <TrendingUp className="w-4 h-4" />
              Our Impact
            </div>
            <h2 className="font-display text-3xl md:text-4xl font-semibold text-foreground mb-4">
              Why Choose A-Cube?
            </h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              Trusted by thousands for compassionate, professional mental health care. Our commitment to excellence drives everything we do.
            </p>
          </div>
        </ScrollReveal>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {impactStats.map((stat, index) => (
            <ScrollReveal key={index} delay={index * 100}>
              <Card className="p-8 gradient-card border border-border hover:shadow-elevated transition-all duration-300 group relative overflow-hidden">
                {/* Hover gradient effect */}
                <div className="absolute inset-0 bg-gradient-to-br from-primary/0 to-primary/0 group-hover:from-primary/5 group-hover:to-transparent transition-all duration-300" />

                <div className="relative z-10">
                  {/* Icon */}
                  <div className="w-12 h-12 rounded-xl gradient-accent flex items-center justify-center mb-4 group-hover:gradient-primary group-hover:scale-110 transition-all duration-300">
                    <stat.icon className={`w-6 h-6 ${stat.color} group-hover:text-primary-foreground transition-colors`} />
                  </div>

                  {/* Value */}
                  <div className="font-display text-4xl font-semibold text-gradient mb-2">
                    {stat.value}
                  </div>

                  {/* Label */}
                  <div className="font-semibold text-foreground mb-2">
                    {stat.label}
                  </div>

                  {/* Description */}
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    {stat.description}
                  </p>
                </div>
              </Card>
            </ScrollReveal>
          ))}
        </div>

        {/* Additional credibility note */}
        <ScrollReveal delay={200}>
          <div className="mt-12 text-center">
            <p className="text-sm text-muted-foreground max-w-3xl mx-auto">
              All statistics are based on verified data and updated regularly. Our commitment to transparency ensures you can trust the quality of care we provide.
            </p>
          </div>
        </ScrollReveal>
      </div>
    </section>
  );
};

export default ImpactStats;
