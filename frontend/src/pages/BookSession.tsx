import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Layout } from "@/components/layout/Layout";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Label } from "@/components/ui/label";
import { ScrollReveal } from "@/components/ui/scroll-reveal";
import { 
  Form, 
  FormControl, 
  FormField, 
  FormItem, 
  FormLabel, 
  FormMessage,
  FormDescription 
} from "@/components/ui/form";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { ArrowRight, Heart, Shield, CheckCircle2, CreditCard } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import servicesBg from "@/assets/bg-services.jpg";
import { sessionAPI } from "@/lib/api";
import { useRazorpay } from "@/hooks/useRazorpay";

const concerns = [
  { id: "anxiety", label: "Anxiety or worry" },
  { id: "depression", label: "Feeling sad or hopeless" },
  { id: "stress", label: "Stress or burnout" },
  { id: "relationships", label: "Relationship challenges" },
  { id: "grief", label: "Grief or loss" },
  { id: "trauma", label: "Past trauma or difficult experiences" },
  { id: "selfEsteem", label: "Low self-esteem or confidence" },
  { id: "anger", label: "Anger or emotional regulation" },
  { id: "lifeTransitions", label: "Life transitions or changes" },
  { id: "other", label: "Other / Not sure" },
];

const formSchema = z.object({
  fullName: z.string().trim().min(2, "Please enter your full name").max(100, "Name must be less than 100 characters"),
  email: z.string().trim().email("Please enter a valid email address").max(255, "Email must be less than 255 characters"),
  phone: z.string().trim().min(10, "Please enter a valid phone number").max(15, "Phone number is too long"),
  age: z.string().min(1, "Please select your age group"),
  gender: z.string().min(1, "Please select your gender"),
  therapyType: z.enum(["individual", "group"], { required_error: "Please select a therapy type" }),
  concerns: z.array(z.string()).min(1, "Please select at least one concern"),
  currentFeelings: z.string().trim().min(10, "Please share a bit more about how you're feeling").max(1000, "Please keep your response under 1000 characters"),
  previousTherapy: z.string().min(1, "Please let us know about your previous therapy experience"),
  preferredTime: z.string().min(1, "Please select your preferred time"),
  additionalInfo: z.string().max(500, "Please keep additional information under 500 characters").optional(),
  consent: z.boolean().refine(val => val === true, "You must agree to continue"),
});

type FormData = z.infer<typeof formSchema>;

const BookSession = () => {
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [sessionId, setSessionId] = useState<string>("");
  const [sessionData, setSessionData] = useState<any>(null);
  const { toast } = useToast();
  const { openPayment, isLoading: isPaymentLoading } = useRazorpay();
  
  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      fullName: "",
      email: "",
      phone: "",
      age: "",
      gender: "",
      therapyType: undefined,
      concerns: [],
      currentFeelings: "",
      previousTherapy: "",
      preferredTime: "",
      additionalInfo: "",
      consent: false,
    },
  });

  const onSubmit = async (data: FormData) => {
    try {
      // Transform data to match backend API
      const bookingData = {
        full_name: data.fullName,
        email: data.email,
        phone: data.phone,
        age: data.age,
        gender: data.gender,
        therapy_type: data.therapyType,
        concerns: data.concerns,
        current_feelings: data.currentFeelings,
        previous_therapy: data.previousTherapy,
        preferred_time: data.preferredTime,
        additional_info: data.additionalInfo || "",
        consent: data.consent
      };

      const response = await sessionAPI.bookSession(bookingData);
      
      setSessionId(response.id);
      setSessionData({ ...bookingData, ...response });
      setIsSubmitted(true);
      toast({
        title: "Request Submitted",
        description: "Thank you for reaching out. Our team will contact you within 24-48 hours.",
      });
    } catch (error) {
      console.error("Error booking session:", error);
      toast({
        title: "Submission Failed",
        description: "There was an error submitting your request. Please try again.",
        variant: "destructive",
      });
    }
  };

  const handlePayNow = () => {
    if (!sessionId || !sessionData) return;

    openPayment({
      amount: 499, // Session booking fee in INR
      item_type: 'session',
      item_id: sessionId,
      item_name: 'Therapy Session Booking',
      user_email: sessionData.email,
      user_name: sessionData.full_name,
      user_phone: sessionData.phone,
      onSuccess: (transactionId) => {
        console.log('Payment successful:', transactionId);
        // You can redirect to payment success page or update UI
      },
      onFailure: (error) => {
        console.error('Payment failed:', error);
      },
    });
  };

  if (isSubmitted) {
    return (
      <Layout>
        <section className="relative py-20 md:py-28 min-h-[80vh] flex items-center">
          <div 
            className="absolute inset-0 bg-cover bg-center"
            style={{ backgroundImage: `url(${servicesBg})` }}
          />
          <div className="absolute inset-0 bg-gradient-to-b from-background/95 via-background/85 to-background" />
          <div className="container mx-auto px-4 relative z-10">
            <div className="max-w-2xl mx-auto text-center">
              <div className="w-20 h-20 rounded-full bg-primary/10 flex items-center justify-center mx-auto mb-6">
                <CheckCircle2 className="w-10 h-10 text-primary" />
              </div>
              <h1 className="font-display text-3xl md:text-4xl font-semibold text-foreground mb-4">
                Thank You for Reaching Out
              </h1>
              <p className="text-muted-foreground mb-6 leading-relaxed">
                Your request has been received. Our caring team will review your information and connect you with a therapist who best matches your needs. You'll hear from us within <strong>24-48 hours</strong>.
              </p>
              <p className="text-sm text-muted-foreground mb-8">
                Taking this step takes courage. We're honored to be part of your healing journey.
              </p>
              
              {/* Payment Option */}
              <div className="bg-accent/50 rounded-xl p-6 mb-8">
                <h3 className="font-semibold text-lg mb-2">Complete Your Booking</h3>
                <p className="text-sm text-muted-foreground mb-4">
                  Pay ₹499 now to secure your session slot instantly.
                </p>
                <Button 
                  variant="hero" 
                  size="lg"
                  onClick={handlePayNow}
                  disabled={isPaymentLoading}
                  className="w-full sm:w-auto"
                >
                  <CreditCard className="w-4 h-4" />
                  {isPaymentLoading ? "Processing..." : "Pay Now ₹499"}
                </Button>
              </div>

              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Button variant="outline" onClick={() => window.location.href = "/"}>
                  Return Home
                  <ArrowRight className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </div>
        </section>
      </Layout>
    );
  }

  return (
    <Layout>
      {/* Hero Section */}
      <section className="relative py-16 md:py-20 overflow-hidden">
        <div 
          className="absolute inset-0 bg-cover bg-center"
          style={{ backgroundImage: `url(${servicesBg})` }}
        />
        <div className="absolute inset-0 bg-gradient-to-b from-background/95 via-background/85 to-background" />
        <div className="container mx-auto px-4 relative z-10">
          <div className="max-w-3xl mx-auto text-center">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-accent text-primary text-sm font-medium mb-4">
              <Heart className="w-4 h-4" />
              Begin Your Healing Journey
            </div>
            <h1 className="font-display text-3xl md:text-4xl font-semibold text-foreground mb-4">
              Book a Session
            </h1>
            <p className="text-muted-foreground leading-relaxed">
              We're here to listen and support you. Please share a little about yourself so we can match you with the right therapist. Everything you share is completely confidential.
            </p>
          </div>
        </div>
      </section>

      {/* Trust Indicators */}
      <section className="py-8 bg-card border-y border-border">
        <div className="container mx-auto px-4">
          <div className="flex flex-wrap justify-center gap-8 text-sm text-muted-foreground">
            <div className="flex items-center gap-2">
              <Shield className="w-4 h-4 text-primary" />
              <span>100% Confidential</span>
            </div>
            <div className="flex items-center gap-2">
              <Heart className="w-4 h-4 text-primary" />
              <span>Non-Judgmental Support</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-primary" />
              <span>Licensed Professionals</span>
            </div>
          </div>
        </div>
      </section>

      {/* Form Section */}
      <section className="py-16 md:py-20">
        <div className="container mx-auto px-4">
          <div className="max-w-3xl mx-auto">
            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-10">
                
                {/* Personal Information */}
                <ScrollReveal>
                  <div className="p-6 md:p-8 rounded-2xl bg-card border border-border">
                    <h2 className="font-display text-xl font-semibold text-foreground mb-6">
                      About You
                    </h2>
                    <div className="grid md:grid-cols-2 gap-6">
                      <FormField
                        control={form.control}
                        name="fullName"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Full Name *</FormLabel>
                            <FormControl>
                              <Input placeholder="Your full name" {...field} />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                      <FormField
                        control={form.control}
                        name="email"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Email Address *</FormLabel>
                            <FormControl>
                              <Input type="email" placeholder="your@email.com" {...field} />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                      <FormField
                        control={form.control}
                        name="phone"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Phone Number *</FormLabel>
                            <FormControl>
                              <Input type="tel" placeholder="+91 98765 43210" {...field} />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                      <FormField
                        control={form.control}
                        name="age"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Age Group *</FormLabel>
                            <Select onValueChange={field.onChange} defaultValue={field.value}>
                              <FormControl>
                                <SelectTrigger>
                                  <SelectValue placeholder="Select your age group" />
                                </SelectTrigger>
                              </FormControl>
                              <SelectContent>
                                <SelectItem value="under18">Under 18</SelectItem>
                                <SelectItem value="18-24">18-24</SelectItem>
                                <SelectItem value="25-34">25-34</SelectItem>
                                <SelectItem value="35-44">35-44</SelectItem>
                                <SelectItem value="45-54">45-54</SelectItem>
                                <SelectItem value="55+">55+</SelectItem>
                              </SelectContent>
                            </Select>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                      <FormField
                        control={form.control}
                        name="gender"
                        render={({ field }) => (
                          <FormItem className="md:col-span-2">
                            <FormLabel>How do you identify? *</FormLabel>
                            <Select onValueChange={field.onChange} defaultValue={field.value}>
                              <FormControl>
                                <SelectTrigger>
                                  <SelectValue placeholder="Select your gender" />
                                </SelectTrigger>
                              </FormControl>
                              <SelectContent>
                                <SelectItem value="female">Female</SelectItem>
                                <SelectItem value="male">Male</SelectItem>
                                <SelectItem value="nonbinary">Non-binary</SelectItem>
                                <SelectItem value="other">Other</SelectItem>
                                <SelectItem value="prefer-not">Prefer not to say</SelectItem>
                              </SelectContent>
                            </Select>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                    </div>
                  </div>
                </ScrollReveal>

                {/* Therapy Type */}
                <ScrollReveal delay={100}>
                  <div className="p-6 md:p-8 rounded-2xl bg-card border border-border">
                    <h2 className="font-display text-xl font-semibold text-foreground mb-2">
                      Type of Support
                    </h2>
                    <p className="text-sm text-muted-foreground mb-6">
                      Which type of therapy would you prefer?
                    </p>
                    <FormField
                      control={form.control}
                      name="therapyType"
                      render={({ field }) => (
                        <FormItem>
                          <FormControl>
                            <RadioGroup
                              onValueChange={field.onChange}
                              defaultValue={field.value}
                              className="grid md:grid-cols-2 gap-4"
                            >
                              <div className={`relative flex items-start p-6 rounded-xl border-2 cursor-pointer transition-all ${field.value === "individual" ? "border-primary bg-accent" : "border-border hover:border-primary/50"}`}>
                                <RadioGroupItem value="individual" id="individual" className="mt-1" />
                                <Label htmlFor="individual" className="ml-3 cursor-pointer">
                                  <span className="font-semibold text-foreground block mb-1">1:1 Therapy</span>
                                  <span className="text-sm text-muted-foreground">
                                    Private, personalized sessions with a dedicated therapist focused entirely on your needs.
                                  </span>
                                </Label>
                              </div>
                              <div className={`relative flex items-start p-6 rounded-xl border-2 cursor-pointer transition-all ${field.value === "group" ? "border-primary bg-accent" : "border-border hover:border-primary/50"}`}>
                                <RadioGroupItem value="group" id="group" className="mt-1" />
                                <Label htmlFor="group" className="ml-3 cursor-pointer">
                                  <span className="font-semibold text-foreground block mb-1">Group Therapy</span>
                                  <span className="text-sm text-muted-foreground">
                                    Connect with others who share similar experiences in a supportive, facilitated group setting.
                                  </span>
                                </Label>
                              </div>
                            </RadioGroup>
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
                </ScrollReveal>

                {/* Concerns */}
                <ScrollReveal delay={150}>
                  <div className="p-6 md:p-8 rounded-2xl bg-card border border-border">
                    <h2 className="font-display text-xl font-semibold text-foreground mb-2">
                      What's on Your Mind?
                    </h2>
                    <p className="text-sm text-muted-foreground mb-6">
                      Select any areas you'd like to explore (you can choose multiple):
                    </p>
                    <FormField
                      control={form.control}
                      name="concerns"
                      render={() => (
                        <FormItem>
                          <div className="grid sm:grid-cols-2 gap-3">
                            {concerns.map((concern) => (
                              <FormField
                                key={concern.id}
                                control={form.control}
                                name="concerns"
                                render={({ field }) => (
                                  <FormItem className="flex items-center space-x-3 space-y-0">
                                    <FormControl>
                                      <Checkbox
                                        checked={field.value?.includes(concern.id)}
                                        onCheckedChange={(checked) => {
                                          return checked
                                            ? field.onChange([...field.value, concern.id])
                                            : field.onChange(field.value?.filter((value) => value !== concern.id));
                                        }}
                                      />
                                    </FormControl>
                                    <FormLabel className="text-sm font-normal cursor-pointer">
                                      {concern.label}
                                    </FormLabel>
                                  </FormItem>
                                )}
                              />
                            ))}
                          </div>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
                </ScrollReveal>

                {/* Current Feelings */}
                <ScrollReveal delay={200}>
                  <div className="p-6 md:p-8 rounded-2xl bg-card border border-border">
                    <h2 className="font-display text-xl font-semibold text-foreground mb-2">
                      How Are You Feeling Right Now?
                    </h2>
                    <p className="text-sm text-muted-foreground mb-6">
                      In your own words, share what brought you here today. There's no right or wrong answer — just be honest.
                    </p>
                    <FormField
                      control={form.control}
                      name="currentFeelings"
                      render={({ field }) => (
                        <FormItem>
                          <FormControl>
                            <Textarea 
                              placeholder="I've been feeling... / Lately, I've noticed... / I'm struggling with..."
                              className="min-h-[120px] resize-none"
                              {...field}
                            />
                          </FormControl>
                          <FormDescription>
                            This helps us understand your needs better and match you with the right support.
                          </FormDescription>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
                </ScrollReveal>

                {/* Previous Therapy & Preferences */}
                <ScrollReveal delay={250}>
                  <div className="p-6 md:p-8 rounded-2xl bg-card border border-border">
                    <h2 className="font-display text-xl font-semibold text-foreground mb-6">
                      A Few More Details
                    </h2>
                    <div className="space-y-6">
                      <FormField
                        control={form.control}
                        name="previousTherapy"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Have you been to therapy before? *</FormLabel>
                            <Select onValueChange={field.onChange} defaultValue={field.value}>
                              <FormControl>
                                <SelectTrigger>
                                  <SelectValue placeholder="Select an option" />
                                </SelectTrigger>
                              </FormControl>
                              <SelectContent>
                                <SelectItem value="never">No, this is my first time</SelectItem>
                                <SelectItem value="past">Yes, in the past</SelectItem>
                                <SelectItem value="current">Yes, I'm currently in therapy</SelectItem>
                              </SelectContent>
                            </Select>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                      <FormField
                        control={form.control}
                        name="preferredTime"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>When would you prefer sessions? *</FormLabel>
                            <Select onValueChange={field.onChange} defaultValue={field.value}>
                              <FormControl>
                                <SelectTrigger>
                                  <SelectValue placeholder="Select preferred time" />
                                </SelectTrigger>
                              </FormControl>
                              <SelectContent>
                                <SelectItem value="morning">Mornings (9 AM - 12 PM)</SelectItem>
                                <SelectItem value="afternoon">Afternoons (12 PM - 5 PM)</SelectItem>
                                <SelectItem value="evening">Evenings (5 PM - 9 PM)</SelectItem>
                                <SelectItem value="weekend">Weekends only</SelectItem>
                                <SelectItem value="flexible">I'm flexible</SelectItem>
                              </SelectContent>
                            </Select>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                      <FormField
                        control={form.control}
                        name="additionalInfo"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Anything else you'd like us to know?</FormLabel>
                            <FormControl>
                              <Textarea 
                                placeholder="Any preferences, accessibility needs, or other information..."
                                className="min-h-[80px] resize-none"
                                {...field}
                              />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                    </div>
                  </div>
                </ScrollReveal>

                {/* Consent & Submit */}
                <ScrollReveal delay={300}>
                  <div className="p-6 md:p-8 rounded-2xl bg-card border border-border">
                    <FormField
                      control={form.control}
                      name="consent"
                      render={({ field }) => (
                        <FormItem className="flex items-start space-x-3 space-y-0">
                          <FormControl>
                            <Checkbox
                              checked={field.value}
                              onCheckedChange={field.onChange}
                            />
                          </FormControl>
                          <div className="space-y-1 leading-none">
                            <FormLabel className="text-sm font-normal">
                              I understand that my information will be kept confidential and used only to match me with appropriate support. I consent to being contacted by A-Cube regarding my therapy request. *
                            </FormLabel>
                            <FormMessage />
                          </div>
                        </FormItem>
                      )}
                    />
                    
                    <div className="mt-8 text-center">
                      <Button type="submit" variant="hero" size="lg" className="min-w-[200px]">
                        Submit Request
                        <ArrowRight className="w-5 h-5" />
                      </Button>
                      <p className="text-xs text-muted-foreground mt-4">
                        Our team will reach out within 24-48 hours to discuss next steps.
                      </p>
                    </div>
                  </div>
                </ScrollReveal>

              </form>
            </Form>
          </div>
        </div>
      </section>
    </Layout>
  );
};

export default BookSession;
