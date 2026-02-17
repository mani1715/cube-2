import { Link } from "react-router-dom";
import { Heart, Mail, Phone, MapPin, Instagram, Linkedin } from "lucide-react";
import { forwardRef } from "react";

export const Footer = forwardRef<HTMLElement>((_, ref) => {
  return (
    <footer 
      ref={ref} 
      className="gradient-card border-t border-border"
      role="contentinfo"
      aria-label="Site footer"
    >
      {/* Contact Section */}
      <section 
        id="contact" 
        className="py-16 md:py-24"
        aria-labelledby="contact-heading"
      >
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 
              id="contact-heading"
              className="font-display text-3xl md:text-4xl font-semibold text-foreground mb-4"
            >
              Get in Touch
            </h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              We're here to support you on your mental health journey. Reach out to us anytime.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
            <div className="group flex flex-col items-center text-center p-6 rounded-2xl gradient-warm shadow-soft hover:shadow-elevated transition-all duration-300 hover:-translate-y-1">
              <div className="w-12 h-12 rounded-full gradient-accent flex items-center justify-center mb-4 group-hover:gradient-primary group-hover:scale-110 transition-all duration-300">
                <Mail className="w-5 h-5 text-primary group-hover:text-primary-foreground transition-colors" aria-hidden="true" />
              </div>
              <h3 className="font-semibold text-foreground mb-2">Email Us</h3>
              <a 
                href="mailto:asmho2728@gmail.com" 
                className="text-muted-foreground hover:text-primary transition-colors"
                aria-label="Email us at asmho2728@gmail.com"
              >
                asmho2728@gmail.com
              </a>
            </div>

            <div className="group flex flex-col items-center text-center p-6 rounded-2xl gradient-warm shadow-soft hover:shadow-elevated transition-all duration-300 hover:-translate-y-1">
              <div className="w-12 h-12 rounded-full gradient-accent flex items-center justify-center mb-4 group-hover:gradient-primary group-hover:scale-110 transition-all duration-300">
                <Phone className="w-5 h-5 text-primary group-hover:text-primary-foreground transition-colors" aria-hidden="true" />
              </div>
              <h3 className="font-semibold text-foreground mb-2">Call Us</h3>
              <a 
                href="tel:+917893982875" 
                className="text-muted-foreground hover:text-primary transition-colors"
                aria-label="Call us at +91 7893982875"
              >
                +91 7893982875
              </a>
            </div>

            <div className="group flex flex-col items-center text-center p-6 rounded-2xl gradient-warm shadow-soft hover:shadow-elevated transition-all duration-300 hover:-translate-y-1">
              <div className="w-12 h-12 rounded-full gradient-accent flex items-center justify-center mb-4 group-hover:gradient-primary group-hover:scale-110 transition-all duration-300">
                <MapPin className="w-5 h-5 text-primary group-hover:text-primary-foreground transition-colors" aria-hidden="true" />
              </div>
              <h3 className="font-semibold text-foreground mb-2">Visit Us</h3>
              <p className="text-muted-foreground">
                Bangalore, India
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Social Media & Links */}
      <div className="border-t border-border py-12">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-4 gap-8">
            <div className="md:col-span-1">
              <Link 
                to="/" 
                className="flex items-center gap-2 mb-4 group"
                aria-label="A-Cube home page"
              >
                <div className="w-10 h-10 rounded-full gradient-primary flex items-center justify-center group-hover:scale-105 transition-transform shadow-soft">
                  <Heart className="w-5 h-5 text-primary-foreground" aria-hidden="true" />
                </div>
                <span className="font-display text-xl font-semibold text-foreground">
                  A-Cube
                </span>
              </Link>
              <p className="text-muted-foreground text-sm mb-6">
                Supporting mental wellness through compassionate care and community.
              </p>
              <div className="flex gap-3" role="list" aria-label="Social media links">
                <a
                  href="https://www.instagram.com/a_cubewellbeing/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="w-10 h-10 rounded-full bg-muted flex items-center justify-center text-muted-foreground hover:bg-gradient-to-r hover:from-primary hover:to-primary/80 hover:text-primary-foreground transition-all duration-300 hover:scale-110 touch-target"
                  aria-label="Follow us on Instagram (opens in new tab)"
                  role="listitem"
                >
                  <Instagram className="w-4 h-4" aria-hidden="true" />
                </a>
                <a
                  href="https://www.linkedin.com/company/aasiya-mental-health-organization/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="w-10 h-10 rounded-full bg-muted flex items-center justify-center text-muted-foreground hover:bg-gradient-to-r hover:from-primary hover:to-primary/80 hover:text-primary-foreground transition-all duration-300 hover:scale-110 touch-target"
                  aria-label="Connect with us on LinkedIn (opens in new tab)"
                  role="listitem"
                >
                  <Linkedin className="w-4 h-4" aria-hidden="true" />
                </a>
              </div>
            </div>

            <div>
              <h4 className="font-semibold text-foreground mb-4">Services</h4>
              <nav aria-label="Services navigation">
                <ul className="space-y-2">
                  <li><Link to="/services" className="text-sm text-muted-foreground hover:text-primary transition-colors">1:1 Therapy</Link></li>
                  <li><Link to="/services" className="text-sm text-muted-foreground hover:text-primary transition-colors">Group Therapy</Link></li>
                  <li><Link to="/blogs" className="text-sm text-muted-foreground hover:text-primary transition-colors">Premium Articles</Link></li>
                </ul>
              </nav>
            </div>

            <div>
              <h4 className="font-semibold text-foreground mb-4">Company</h4>
              <nav aria-label="Company navigation">
                <ul className="space-y-2">
                  <li><Link to="/about" className="text-sm text-muted-foreground hover:text-primary transition-colors">About Us</Link></li>
                  <li><Link to="/careers" className="text-sm text-muted-foreground hover:text-primary transition-colors">Careers</Link></li>
                  <li><Link to="/volunteer" className="text-sm text-muted-foreground hover:text-primary transition-colors">Volunteer</Link></li>
                  <li><Link to="/blogs" className="text-sm text-muted-foreground hover:text-primary transition-colors">Blog</Link></li>
                </ul>
              </nav>
            </div>

            <div>
              <h4 className="font-semibold text-foreground mb-4">Legal</h4>
              <nav aria-label="Legal navigation">
                <ul className="space-y-2">
                  <li><Link to="/privacy" className="text-sm text-muted-foreground hover:text-primary transition-colors">Privacy Policy</Link></li>
                  <li><Link to="/terms" className="text-sm text-muted-foreground hover:text-primary transition-colors">Terms & Conditions</Link></li>
                </ul>
              </nav>
            </div>
          </div>

          <div className="border-t border-border mt-12 pt-8 text-center">
            <p className="text-sm text-muted-foreground" role="contentinfo">
              © {new Date().getFullYear()} A-Cube. All rights reserved.
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
});

Footer.displayName = "Footer";
