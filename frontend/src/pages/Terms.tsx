import { Layout } from "@/components/layout/Layout";
import { ScrollArea } from "@/components/ui/scroll-area";
import { FileText, Shield, Users, AlertCircle, Scale, Mail } from "lucide-react";
import contactBg from "@/assets/bg-contact.jpg";

const sections = [
  {
    id: "acceptance",
    icon: FileText,
    title: "1. Acceptance of Terms",
    content: `By accessing and using the A-Cube platform ("Service"), you agree to be bound by these Terms and Conditions ("Terms"). If you disagree with any part of these terms, you may not access the Service.

These Terms apply to all visitors, users, and others who access or use the Service, including but not limited to clients seeking mental health services, psychologists providing services, volunteers, and general visitors.

By creating an account or using our services, you confirm that you are at least 18 years of age or have obtained parental/guardian consent where applicable.`
  },
  {
    id: "services",
    icon: Users,
    title: "2. Description of Services",
    content: `A-Cube provides a platform connecting individuals with licensed mental health professionals for therapy services, including:

• One-on-one therapy sessions (in-person and telehealth)
• Group therapy sessions
• Mental health events and workshops
• Educational articles and resources
• Community support programs

Our services are designed to support mental wellness but are not intended to replace emergency mental health services. If you are experiencing a mental health emergency, please contact your local emergency services or crisis hotline immediately.`
  },
  {
    id: "user-accounts",
    icon: Shield,
    title: "3. User Accounts and Responsibilities",
    content: `When you create an account with us, you must provide accurate, complete, and current information. Failure to do so constitutes a breach of the Terms.

You are responsible for:
• Maintaining the confidentiality of your account credentials
• All activities that occur under your account
• Notifying us immediately of any unauthorized use
• Ensuring your contact information is up to date

We reserve the right to suspend or terminate accounts that violate these Terms or engage in fraudulent, abusive, or illegal activity.`
  },
  {
    id: "privacy",
    icon: AlertCircle,
    title: "4. Privacy and Confidentiality",
    content: `Your privacy is of utmost importance to us. Our Privacy Policy, which is incorporated into these Terms by reference, describes how we collect, use, and protect your personal information.

For therapy services:
• All sessions are confidential as required by applicable laws and professional ethics
• Psychologists are bound by professional confidentiality standards
• We employ industry-standard security measures to protect your data
• Session recordings, if any, require explicit consent

Exceptions to confidentiality may apply as required by law, including mandatory reporting requirements for harm to self or others.`
  },
  {
    id: "payments",
    icon: Scale,
    title: "5. Payments and Refunds",
    content: `Payment terms for services:
• Fees are displayed before booking and are subject to change
• Payment is required at the time of booking unless otherwise arranged
• We accept major credit cards and other payment methods as indicated
• Subscription services are billed according to the selected plan

Cancellation and refund policy:
• Sessions may be cancelled up to 24 hours before the scheduled time for a full refund
• Late cancellations (less than 24 hours) may incur a cancellation fee
• No-shows are charged the full session fee
• Refunds are processed within 5-10 business days`
  },
  {
    id: "psychologists",
    icon: Users,
    title: "6. Psychologist Terms",
    content: `Psychologists using our platform agree to:
• Maintain current and valid licensure in their practicing jurisdiction
• Adhere to professional ethical standards and codes of conduct
• Provide accurate information about their qualifications and experience
• Maintain professional liability insurance
• Comply with all applicable laws and regulations

A-Cube serves as a platform connecting clients with independent psychologists. Psychologists are independent contractors, not employees of A-Cube.`
  },
  {
    id: "volunteers",
    icon: Users,
    title: "7. Volunteer Terms",
    content: `Volunteers participating in A-Cube programs agree to:
• Complete required training and background checks
• Maintain confidentiality of all sensitive information
• Follow organizational policies and procedures
• Represent A-Cube professionally in all activities
• Immediately report any concerns or incidents

Volunteer participation is at-will and may be terminated by either party at any time.`
  },
  {
    id: "intellectual-property",
    icon: FileText,
    title: "8. Intellectual Property",
    content: `The Service and its original content, features, and functionality are owned by A-Cube and are protected by international copyright, trademark, patent, trade secret, and other intellectual property laws.

You may not:
• Copy, modify, or distribute our content without permission
• Use our trademarks or branding without authorization
• Reverse engineer or attempt to extract source code
• Create derivative works based on our content`
  },
  {
    id: "limitation",
    icon: AlertCircle,
    title: "9. Limitation of Liability",
    content: `To the maximum extent permitted by law, A-Cube shall not be liable for any indirect, incidental, special, consequential, or punitive damages resulting from:

• Your use or inability to use the Service
• Any unauthorized access to your data
• Any interruption or cessation of the Service
• Any errors or omissions in content

Our total liability for any claims arising from these Terms or your use of the Service shall not exceed the amount you paid to us in the twelve months preceding the claim.`
  },
  {
    id: "modifications",
    icon: FileText,
    title: "10. Modifications to Terms",
    content: `We reserve the right to modify these Terms at any time. When we make changes, we will:

• Update the "Last Updated" date at the top of these Terms
• Notify registered users via email for material changes
• Post a notice on our platform

Your continued use of the Service after changes become effective constitutes acceptance of the revised Terms.`
  },
  {
    id: "contact",
    icon: Mail,
    title: "11. Contact Information",
    content: `If you have any questions about these Terms and Conditions, please contact us:

A-Cube
123 Wellness Street
San Francisco, CA 94102

Email: legal@a-cube.com
Phone: +1 (234) 567-890

For mental health emergencies, please contact your local emergency services or the National Suicide Prevention Lifeline at 988.`
  }
];

const Terms = () => {
  return (
    <Layout>
      {/* Hero Section */}
      <section className="relative py-16 md:py-24 overflow-hidden">
        <div 
          className="absolute inset-0 bg-cover bg-center"
          style={{ backgroundImage: `url(${contactBg})` }}
        />
        <div className="absolute inset-0 bg-gradient-to-br from-background/95 via-background/80 to-background/70" />
        <div className="container mx-auto px-4 relative z-10">
          <div className="max-w-3xl mx-auto text-center">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 text-primary text-sm font-medium mb-6 animate-fade-up opacity-0" style={{ animationDelay: "0s", animationFillMode: "forwards" }}>
              <Scale className="w-4 h-4" />
              Legal
            </div>
            <h1 className="font-display text-4xl md:text-5xl font-semibold text-foreground mb-6 animate-fade-up opacity-0" style={{ animationDelay: "0.1s", animationFillMode: "forwards" }}>
              Terms & Conditions
            </h1>
            <p className="text-lg text-muted-foreground animate-fade-up opacity-0" style={{ animationDelay: "0.2s", animationFillMode: "forwards" }}>
              Please read these terms carefully before using our services. Last updated: December 31, 2024.
            </p>
          </div>
        </div>
      </section>

      {/* Terms Content */}
      <section className="py-16 md:py-24">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto">
            {/* Quick Navigation */}
            <div className="mb-12 p-6 rounded-2xl bg-card border border-border">
              <h2 className="font-semibold text-foreground mb-4">Quick Navigation</h2>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                {sections.map((section) => (
                  <a
                    key={section.id}
                    href={`#${section.id}`}
                    className="text-sm text-muted-foreground hover:text-primary transition-colors py-1"
                  >
                    {section.title}
                  </a>
                ))}
              </div>
            </div>

            {/* Terms Sections */}
            <ScrollArea className="h-auto">
              <div className="space-y-12">
                {sections.map((section, index) => (
                  <div
                    key={section.id}
                    id={section.id}
                    className="scroll-mt-24 animate-fade-up opacity-0"
                    style={{ animationDelay: `${0.1 * index}s`, animationFillMode: "forwards" }}
                  >
                    <div className="flex items-start gap-4 mb-4">
                      <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
                        <section.icon className="w-5 h-5 text-primary" />
                      </div>
                      <h2 className="font-display text-xl md:text-2xl font-semibold text-foreground">
                        {section.title}
                      </h2>
                    </div>
                    <div className="pl-14">
                      <div className="prose prose-sm max-w-none text-muted-foreground whitespace-pre-line leading-relaxed">
                        {section.content}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </ScrollArea>

            {/* Agreement Notice */}
            <div className="mt-12 p-6 rounded-2xl bg-primary/5 border border-primary/20">
              <p className="text-sm text-foreground">
                <strong>By using A-Cube services, you acknowledge that you have read, understood, and agree to be bound by these Terms and Conditions.</strong> If you have any questions or concerns, please contact us before using our services.
              </p>
            </div>
          </div>
        </div>
      </section>
    </Layout>
  );
};

export default Terms;
