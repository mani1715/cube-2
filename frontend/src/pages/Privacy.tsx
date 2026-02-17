import { Layout } from "@/components/layout/Layout";
import { ScrollReveal } from "@/components/ui/scroll-reveal";
import contactBg from "@/assets/bg-contact.jpg";
import SEO from "@/components/SEO";
import { Link } from "react-router-dom";

const Privacy = () => {
  return (
    <Layout>
      <SEO 
        title="Privacy Policy"
        description="A-Cube Privacy Policy - Learn how we protect your personal information, therapy session confidentiality, and data security practices."
        keywords={['privacy policy', 'data protection', 'confidentiality', 'GDPR', 'data security', 'therapy privacy']}
      />
      <section className="relative py-20 md:py-28 overflow-hidden">
        <div 
          className="absolute inset-0 bg-cover bg-center"
          style={{ backgroundImage: `url(${contactBg})` }}
        />
        <div className="absolute inset-0 bg-gradient-to-br from-background/95 via-background/80 to-background/70" />
        <div className="container mx-auto px-4 relative z-10">
          <div className="max-w-3xl mx-auto text-center">
            <h1 className="font-display text-4xl md:text-5xl font-semibold text-foreground mb-6 animate-fade-up opacity-0" style={{ animationDelay: "0s", animationFillMode: "forwards" }}>
              Privacy Policy
            </h1>
            <p className="text-muted-foreground animate-fade-up opacity-0" style={{ animationDelay: "0.1s", animationFillMode: "forwards" }}>
              Last updated: December 31, 2024
            </p>
          </div>
        </div>
      </section>

      <section className="py-16 md:py-24">
        <div className="container mx-auto px-4">
          <div className="max-w-3xl mx-auto">
            <div className="prose prose-lg max-w-none space-y-8">
              {[
                { title: "Introduction", content: "At A-Cube, we are committed to protecting your privacy and ensuring the security of your personal information. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our services, website, and applications." },
                { title: "Information We Collect", content: null, list: ["Personal Information: We may collect personal information such as your name, email address, phone number, and payment information.", "Health Information: In the course of providing therapy services, we may collect sensitive health information treated with the highest level of confidentiality.", "Usage Data: We automatically collect certain information about your device and usage patterns."] },
                { title: "How We Use Your Information", content: null, bullets: ["To provide and maintain our therapy and mental health services", "To process transactions and send related information", "To send you updates about events, services, and resources", "To respond to your inquiries and provide customer support", "To improve our services and develop new features", "To comply with legal obligations"] },
                { title: "Data Security", content: "We implement appropriate technical and organizational measures to protect your personal information against unauthorized access, alteration, disclosure, or destruction. All therapy sessions and communications are encrypted." },
                { title: "Confidentiality of Therapy Sessions", content: "All therapy sessions are strictly confidential. We do not share information about your therapy sessions with third parties except as required by law or with your explicit written consent." },
                { title: "Your Rights", content: null, bullets: ["Access and receive a copy of your personal data", "Request correction of inaccurate personal data", "Request deletion of your personal data", "Object to processing of your personal data", "Request restriction of processing", "Data portability rights"] },
                { title: "Cookies and Tracking", content: "We use cookies and similar tracking technologies to enhance your experience on our website. You can control cookie preferences through your browser settings." },
                { title: "Third-Party Services", content: "We may use third-party services for payment processing, video conferencing, and analytics. These services have their own privacy policies." },
              ].map((section, index) => (
                <ScrollReveal key={index} delay={index * 60}>
                  <div className="p-6 rounded-2xl bg-card border border-border">
                    <h2 className="font-display text-xl font-semibold text-foreground mb-4">{section.title}</h2>
                    {section.content && <p className="text-muted-foreground leading-relaxed">{section.content}</p>}
                    {section.list && <div className="space-y-2 text-muted-foreground">{section.list.map((item, i) => <p key={i}><strong className="text-foreground">{item.split(":")[0]}:</strong>{item.split(":").slice(1).join(":")}</p>)}</div>}
                    {section.bullets && <ul className="list-disc pl-6 space-y-2 text-muted-foreground">{section.bullets.map((item, i) => <li key={i}>{item}</li>)}</ul>}
                  </div>
                </ScrollReveal>
              ))}

              <ScrollReveal delay={500}>
                <div className="p-6 rounded-2xl bg-primary/5 border border-primary/20">
                  <h2 className="font-display text-xl font-semibold text-foreground mb-4">Your Data Rights</h2>
                  <p className="text-muted-foreground mb-4">
                    You have the right to access, modify, or delete your personal data. You can also request a complete export of your data.
                  </p>
                  <div className="flex flex-wrap gap-3 mb-6">
                    <Link 
                      to="/data-export" 
                      className="inline-flex items-center px-4 py-2 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 transition-colors font-medium"
                    >
                      Request Data Export
                    </Link>
                    <Link 
                      to="/account-deletion" 
                      className="inline-flex items-center px-4 py-2 rounded-lg border border-destructive text-destructive hover:bg-destructive/10 transition-colors font-medium"
                    >
                      Request Account Deletion
                    </Link>
                  </div>
                  <h2 className="font-display text-xl font-semibold text-foreground mb-4 mt-6">Contact Us</h2>
                  <p className="text-muted-foreground mb-4">If you have any questions about this Privacy Policy, please contact us:</p>
                  <div className="space-y-1">
                    <p className="text-foreground font-medium">A-Cube Privacy Team</p>
                    <p className="text-muted-foreground">Email: privacy@a-cube.com</p>
                    <p className="text-muted-foreground">Phone: +1 (234) 567-890</p>
                    <p className="text-muted-foreground">Address: 123 Wellness Street, San Francisco, CA 94102</p>
                  </div>
                </div>
              </ScrollReveal>
            </div>
          </div>
        </div>
      </section>
    </Layout>
  );
};

export default Privacy;