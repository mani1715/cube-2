import { ScrollReveal } from "@/components/ui/scroll-reveal";
import { Quote, Star } from "lucide-react";
import { Card } from "@/components/ui/card";

interface Testimonial {
  id: number;
  name: string;
  role: string;
  content: string;
  rating: number;
  image?: string;
}

const testimonials: Testimonial[] = [
  {
    id: 1,
    name: "Sarah Johnson",
    role: "Individual Therapy Client",
    content: "A-Cube has been a game-changer for my mental health journey. The therapists are compassionate, professional, and truly care about my well-being. I feel heard and supported every session.",
    rating: 5,
  },
  {
    id: 2,
    name: "Michael Chen",
    role: "Group Therapy Participant",
    content: "The group sessions provided a safe space where I could connect with others facing similar challenges. The guidance from the facilitators was exceptional, and I've made meaningful progress.",
    rating: 5,
  },
  {
    id: 3,
    name: "Priya Sharma",
    role: "Anxiety & Stress Management",
    content: "I was hesitant to start therapy, but A-Cube made the process so comfortable. The online booking was easy, and my therapist's approach has helped me develop effective coping strategies.",
    rating: 5,
  },
  {
    id: 4,
    name: "David Martinez",
    role: "Corporate Wellness Program",
    content: "Our company partnered with A-Cube for employee mental health support. The feedback has been overwhelmingly positive. Professional, confidential, and impactful.",
    rating: 5,
  },
  {
    id: 5,
    name: "Aisha Patel",
    role: "Young Adult Counseling",
    content: "As a young adult dealing with life transitions, A-Cube helped me navigate uncertainty with confidence. The therapists understand the unique challenges we face today.",
    rating: 5,
  },
  {
    id: 6,
    name: "James Wilson",
    role: "Couples Therapy",
    content: "My partner and I found clarity and understanding through A-Cube's couples counseling. The therapist created a balanced, non-judgmental space for us to grow together.",
    rating: 5,
  },
];

const Testimonials = () => {
  return (
    <section className="py-20 md:py-28 bg-muted/30">
      <div className="container mx-auto px-4">
        <ScrollReveal>
          <div className="text-center mb-16">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 text-primary text-sm font-medium mb-4">
              <Quote className="w-4 h-4" />
              Testimonials
            </div>
            <h2 className="font-display text-3xl md:text-4xl font-semibold text-foreground mb-4">
              Stories of Healing & Growth
            </h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              Real experiences from individuals who have found support, clarity, and transformation through A-Cube.
            </p>
          </div>
        </ScrollReveal>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {testimonials.map((testimonial, index) => (
            <ScrollReveal key={testimonial.id} delay={index * 100}>
              <Card className="p-6 h-full gradient-card border border-border hover:shadow-elevated transition-all duration-300 group">
                {/* Rating Stars */}
                <div className="flex gap-1 mb-4">
                  {[...Array(testimonial.rating)].map((_, i) => (
                    <Star
                      key={i}
                      className="w-4 h-4 fill-primary text-primary"
                    />
                  ))}
                </div>

                {/* Quote Icon */}
                <Quote className="w-8 h-8 text-primary/20 mb-4 group-hover:text-primary/40 transition-colors" />

                {/* Content */}
                <p className="text-muted-foreground text-sm leading-relaxed mb-6 line-clamp-5">
                  "{testimonial.content}"
                </p>

                {/* Author Info */}
                <div className="mt-auto pt-4 border-t border-border">
                  <div className="flex items-center gap-3">
                    {/* Avatar Placeholder */}
                    <div className="w-10 h-10 rounded-full gradient-primary flex items-center justify-center text-primary-foreground font-semibold text-sm">
                      {testimonial.name.charAt(0)}
                    </div>
                    <div>
                      <div className="font-semibold text-foreground text-sm">
                        {testimonial.name}
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {testimonial.role}
                      </div>
                    </div>
                  </div>
                </div>
              </Card>
            </ScrollReveal>
          ))}
        </div>

        {/* Trust Badge */}
        <ScrollReveal delay={200}>
          <div className="text-center mt-12">
            <p className="text-sm text-muted-foreground">
              All testimonials are from verified clients. Names have been changed to protect privacy.
            </p>
          </div>
        </ScrollReveal>
      </div>
    </section>
  );
};

export default Testimonials;
