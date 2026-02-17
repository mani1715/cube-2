import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { HelmetProvider } from "react-helmet-async";
import { ThemeProvider } from "./components/ThemeProvider";
import CookieConsent from "./components/CookieConsent";
import EnhancedPWAInstallPrompt from "./components/EnhancedPWAInstallPrompt";
import PWAUpdatePrompt from "./components/PWAUpdatePrompt";
import SkipNav from "./components/accessibility/SkipNav";
import EnhancedErrorBoundary from "./components/EnhancedErrorBoundary";
import { NetworkStatus } from "./components/ui/network-status";
import { MobileStickyCTA } from "./components/mobile/MobileStickyCTA";
import { lazy, Suspense } from "react";
import LoadingSpinner from "./components/LoadingSpinner";

// Eagerly load critical pages (Index page for initial load)
import Index from "./pages/Index";

// Lazy load all other pages for code splitting
const About = lazy(() => import("./pages/About"));
const Services = lazy(() => import("./pages/Services"));
const BookSession = lazy(() => import("./pages/BookSession"));
const Events = lazy(() => import("./pages/Events"));
const Blogs = lazy(() => import("./pages/Blogs"));
const Careers = lazy(() => import("./pages/Careers"));
const PsychologistPortal = lazy(() => import("./pages/PsychologistPortal"));
const Volunteer = lazy(() => import("./pages/Volunteer"));
const Privacy = lazy(() => import("./pages/Privacy"));
const Terms = lazy(() => import("./pages/Terms"));
const DataExport = lazy(() => import("./pages/DataExport"));
const AccountDeletion = lazy(() => import("./pages/AccountDeletion"));
const NotFound = lazy(() => import("./pages/NotFound"));
const Offline = lazy(() => import("./pages/Offline"));

// User imports - lazy loaded
import { UserProvider } from "./contexts/UserContext";
const UserLogin = lazy(() => import("./pages/UserLogin"));
const UserSignup = lazy(() => import("./pages/UserSignup"));
const UserDashboard = lazy(() => import("./pages/UserDashboard"));
const UserProfile = lazy(() => import("./pages/UserProfile"));
const PaymentSuccess = lazy(() => import("./pages/PaymentSuccess"));
const PaymentFailure = lazy(() => import("./pages/PaymentFailure"));

// Admin imports - lazy loaded for admin panel
import { AdminProvider } from "./contexts/AdminContext";
const AdminLayout = lazy(() => import("./admin/AdminLayout"));
const AdminDashboard = lazy(() => import("./admin/pages/AdminDashboard"));
const AdminSessions = lazy(() => import("./admin/pages/AdminSessions"));
const AdminEvents = lazy(() => import("./admin/pages/AdminEvents"));
const AdminBlogs = lazy(() => import("./admin/pages/AdminBlogs"));
const AdminPsychologists = lazy(() => import("./admin/pages/AdminPsychologists"));
const AdminVolunteers = lazy(() => import("./admin/pages/AdminVolunteers"));
const AdminJobs = lazy(() => import("./admin/pages/AdminJobs"));
const AdminContacts = lazy(() => import("./admin/pages/AdminContacts"));
const AdminSettings = lazy(() => import("./admin/pages/AdminSettings"));
const AdminLogs = lazy(() => import("./admin/pages/AdminLogs"));
const AdminErrors = lazy(() => import("./admin/pages/AdminErrors"));
const AdminLogin = lazy(() => import("./admin/AdminLogin"));
import AdminProtectedRoute from "./admin/AdminProtectedRoute";
import ErrorBoundary from "./admin/components/ErrorBoundary";

const queryClient = new QueryClient();

const App = () => (
  <HelmetProvider>
    <ThemeProvider
      attribute="class"
      defaultTheme="system"
      enableSystem
      disableTransitionOnChange={false}
    >
      <QueryClientProvider client={queryClient}>
        <TooltipProvider>
          <SkipNav />
          <NetworkStatus />
          <MobileStickyCTA showAfterScroll={400} dismissable={true} />
          <Toaster />
          <Sonner />
          <CookieConsent />
          <EnhancedPWAInstallPrompt />
          <PWAUpdatePrompt />
          <BrowserRouter>
            <UserProvider>
              <AdminProvider>
                <EnhancedErrorBoundary>
                  <Suspense fallback={<LoadingSpinner />}>
                    <Routes>
                    <Route path="/" element={<Index />} />
                    <Route path="/about" element={<About />} />
                    <Route path="/services" element={<Services />} />
                    <Route path="/book-session" element={<BookSession />} />
                    <Route path="/events" element={<Events />} />
                    <Route path="/blogs" element={<Blogs />} />
                    <Route path="/careers" element={<Careers />} />
                    <Route path="/psychologist-portal" element={<PsychologistPortal />} />
                    <Route path="/volunteer" element={<Volunteer />} />
                    <Route path="/privacy" element={<Privacy />} />
                    <Route path="/terms" element={<Terms />} />
                    <Route path="/data-export" element={<DataExport />} />
                    <Route path="/account-deletion" element={<AccountDeletion />} />
                    <Route path="/offline" element={<Offline />} />
            
                    {/* User Authentication Routes (Public) */}
                    <Route path="/login" element={<UserLogin />} />
                    <Route path="/signup" element={<UserSignup />} />
                    
                    {/* User Dashboard Routes (Public - Auth handled inside) */}
                    <Route path="/user/dashboard" element={<UserDashboard />} />
                    <Route path="/user/profile" element={<UserProfile />} />
                    
                    {/* Payment Routes (Public) */}
                    <Route path="/payment/success" element={<PaymentSuccess />} />
                    <Route path="/payment/failure" element={<PaymentFailure />} />
                    
                    {/* Admin Login Route (Public) */}
                    <Route path="/admin/login" element={<AdminLogin />} />
                    
                    {/* Protected Admin Routes */}
                    <Route element={<AdminProtectedRoute />}>
                      <Route path="/admin" element={<AdminLayout />}>
                        <Route index element={<ErrorBoundary><AdminDashboard /></ErrorBoundary>} />
                        <Route path="sessions" element={<ErrorBoundary><AdminSessions /></ErrorBoundary>} />
                        <Route path="events" element={<ErrorBoundary><AdminEvents /></ErrorBoundary>} />
                        <Route path="blogs" element={<ErrorBoundary><AdminBlogs /></ErrorBoundary>} />
                        <Route path="psychologists" element={<ErrorBoundary><AdminPsychologists /></ErrorBoundary>} />
                        <Route path="volunteers" element={<ErrorBoundary><AdminVolunteers /></ErrorBoundary>} />
                        <Route path="jobs" element={<ErrorBoundary><AdminJobs /></ErrorBoundary>} />
                        <Route path="contacts" element={<ErrorBoundary><AdminContacts /></ErrorBoundary>} />
                        <Route path="logs" element={<ErrorBoundary><AdminLogs /></ErrorBoundary>} />
                        <Route path="errors" element={<ErrorBoundary><AdminErrors /></ErrorBoundary>} />
                        <Route path="settings" element={<ErrorBoundary><AdminSettings /></ErrorBoundary>} />
                      </Route>
                    </Route>
                    
                    {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
                    <Route path="*" element={<NotFound />} />
                  </Routes>
                </Suspense>
              </EnhancedErrorBoundary>
            </AdminProvider>
          </UserProvider>
        </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
  </ThemeProvider>
  </HelmetProvider>
);

export default App;
