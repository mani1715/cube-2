import React, { useState, useEffect } from 'react';
import { Navbar } from '@/components/layout/Navbar';
import { useUser } from '@/contexts/UserContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Calendar, CreditCard, Heart, BookOpen, Loader2, ExternalLink } from 'lucide-react';
import { dashboardAPI } from '@/lib/phase12Api';
import { toast } from 'sonner';
import SEO from '@/components/SEO';
import { useNavigate } from 'react-router-dom';

const UserDashboard = () => {
  const { user, accessToken, isAuthenticated } = useUser();
  const navigate = useNavigate();
  const [stats, setStats] = useState<any>(null);
  const [sessions, setSessions] = useState<any[]>([]);
  const [events, setEvents] = useState<any[]>([]);
  const [payments, setPayments] = useState<any[]>([]);
  const [savedBlogs, setSavedBlogs] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  // Redirect if not authenticated
  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
    }
  }, [isAuthenticated, navigate]);

  // Fetch dashboard data
  useEffect(() => {
    if (!accessToken) return;

    const fetchDashboardData = async () => {
      setIsLoading(true);
      try {
        // Fetch overview stats
        const overviewResponse = await dashboardAPI.getOverview(accessToken);
        if (overviewResponse.success) {
          setStats(overviewResponse.overview);
        }
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error);
        toast.error('Failed to load dashboard data');
      } finally {
        setIsLoading(false);
      }
    };

    fetchDashboardData();
  }, [accessToken]);

  // Fetch sessions when tab is active
  useEffect(() => {
    if (activeTab === 'sessions' && accessToken && sessions.length === 0) {
      fetchSessions();
    }
  }, [activeTab, accessToken]);

  // Fetch events when tab is active
  useEffect(() => {
    if (activeTab === 'events' && accessToken && events.length === 0) {
      fetchEvents();
    }
  }, [activeTab, accessToken]);

  // Fetch payments when tab is active
  useEffect(() => {
    if (activeTab === 'payments' && accessToken && payments.length === 0) {
      fetchPayments();
    }
  }, [activeTab, accessToken]);

  // Fetch saved blogs when tab is active
  useEffect(() => {
    if (activeTab === 'saved' && accessToken && savedBlogs.length === 0) {
      fetchSavedBlogs();
    }
  }, [activeTab, accessToken]);

  const fetchSessions = async () => {
    if (!accessToken) return;
    try {
      const response = await dashboardAPI.getUserSessions(accessToken);
      if (response.success) {
        setSessions(response.sessions);
      }
    } catch (error) {
      console.error('Failed to fetch sessions:', error);
    }
  };

  const fetchEvents = async () => {
    if (!accessToken) return;
    try {
      const response = await dashboardAPI.getUserEvents(accessToken);
      if (response.success) {
        setEvents(response.events);
      }
    } catch (error) {
      console.error('Failed to fetch events:', error);
    }
  };

  const fetchPayments = async () => {
    if (!accessToken) return;
    try {
      const response = await dashboardAPI.getUserPayments(accessToken);
      if (response.success) {
        setPayments(response.payments);
      }
    } catch (error) {
      console.error('Failed to fetch payments:', error);
    }
  };

  const fetchSavedBlogs = async () => {
    if (!accessToken) return;
    try {
      const response = await dashboardAPI.getSavedBlogs(accessToken);
      if (response.success) {
        setSavedBlogs(response.saved_blogs);
      }
    } catch (error) {
      console.error('Failed to fetch saved blogs:', error);
    }
  };

  const getStatusBadge = (status: string) => {
    const statusConfig: any = {
      confirmed: { bg: 'bg-green-100 dark:bg-green-900', text: 'text-green-800 dark:text-green-200' },
      pending: { bg: 'bg-yellow-100 dark:bg-yellow-900', text: 'text-yellow-800 dark:text-yellow-200' },
      cancelled: { bg: 'bg-red-100 dark:bg-red-900', text: 'text-red-800 dark:text-red-200' },
      completed: { bg: 'bg-blue-100 dark:bg-blue-900', text: 'text-blue-800 dark:text-blue-200' },
      success: { bg: 'bg-green-100 dark:bg-green-900', text: 'text-green-800 dark:text-green-200' },
      failed: { bg: 'bg-red-100 dark:bg-red-900', text: 'text-red-800 dark:text-red-200' },
    };

    const config = statusConfig[status?.toLowerCase()] || statusConfig.pending;

    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${config.bg} ${config.text}`}>
        {status}
      </span>
    );
  };

  if (!isAuthenticated) {
    return null;
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        <Navbar />
        <div className="container mx-auto px-4 pt-32 pb-20">
          <div className="flex items-center justify-center h-64">
            <Loader2 className="w-8 h-8 animate-spin text-primary" />
          </div>
        </div>
      </div>
    );
  }

  return (
    <>
      <SEO
        title={`Dashboard - ${user?.name} - A-Cube`}
        description="Manage your sessions, events, payments, and saved content on A-Cube Mental Health Platform."
      />
      <div className="min-h-screen bg-background">
        <Navbar />
        
        <div className="container mx-auto px-4 pt-32 pb-20">
          {/* Welcome Header */}
          <div className="mb-8 animate-fade-in">
            <h1 className="text-3xl md:text-4xl font-display font-bold mb-2">
              Welcome back, {user?.name}! 👋
            </h1>
            <p className="text-muted-foreground">
              Here's an overview of your mental wellness journey
            </p>
          </div>

          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <Card className="animate-slide-in-up" style={{ animationDelay: '0.1s' }}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Sessions</CardTitle>
                <Calendar className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats?.total_sessions || 0}</div>
                <p className="text-xs text-muted-foreground">
                  {stats?.upcoming_sessions || 0} upcoming
                </p>
              </CardContent>
            </Card>

            <Card className="animate-slide-in-up" style={{ animationDelay: '0.2s' }}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Events Attended</CardTitle>
                <Heart className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats?.total_events || 0}</div>
                <p className="text-xs text-muted-foreground">Total registrations</p>
              </CardContent>
            </Card>

            <Card className="animate-slide-in-up" style={{ animationDelay: '0.3s' }}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Saved Content</CardTitle>
                <BookOpen className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats?.saved_blogs || 0}</div>
                <p className="text-xs text-muted-foreground">
                  {stats?.liked_blogs || 0} liked articles
                </p>
              </CardContent>
            </Card>

            <Card className="animate-slide-in-up" style={{ animationDelay: '0.4s' }}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Spent</CardTitle>
                <CreditCard className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">₹{stats?.total_spent || 0}</div>
                <p className="text-xs text-muted-foreground">
                  {stats?.total_payments || 0} transactions
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Tabs for different sections */}
          <Card className="animate-slide-in-up" style={{ animationDelay: '0.5s' }}>
            <CardHeader>
              <CardTitle>Your Activity</CardTitle>
              <CardDescription>
                View and manage your sessions, events, payments, and saved content
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
                <TabsList className="grid w-full grid-cols-4">
                  <TabsTrigger value="sessions">Sessions</TabsTrigger>
                  <TabsTrigger value="events">Events</TabsTrigger>
                  <TabsTrigger value="payments">Payments</TabsTrigger>
                  <TabsTrigger value="saved">Saved</TabsTrigger>
                </TabsList>
                
                <TabsContent value="sessions" className="space-y-4 mt-4">
                  {sessions.length === 0 ? (
                    <div className="text-center py-12 text-muted-foreground">
                      <Calendar className="w-12 h-12 mx-auto mb-4 opacity-50" />
                      <p>No sessions booked yet</p>
                      <p className="text-sm mt-2">Book your first therapy session to get started</p>
                      <Button className="mt-4" onClick={() => navigate('/book-session')}>
                        Book Session
                      </Button>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {sessions.map((session: any) => (
                        <div key={session.id} className="p-4 border rounded-lg hover:bg-muted/50 transition-colors">
                          <div className="flex justify-between items-start mb-2">
                            <div>
                              <p className="font-medium">{session.psychologist_name}</p>
                              <p className="text-sm text-muted-foreground">
                                {new Date(session.session_date).toLocaleDateString()} at {session.session_time}
                              </p>
                            </div>
                            {getStatusBadge(session.status)}
                          </div>
                          <p className="text-sm text-muted-foreground capitalize">{session.session_type} Session</p>
                        </div>
                      ))}
                    </div>
                  )}
                </TabsContent>
                
                <TabsContent value="events" className="space-y-4 mt-4">
                  {events.length === 0 ? (
                    <div className="text-center py-12 text-muted-foreground">
                      <Heart className="w-12 h-12 mx-auto mb-4 opacity-50" />
                      <p>No events registered yet</p>
                      <p className="text-sm mt-2">Check out our upcoming events and workshops</p>
                      <Button className="mt-4" onClick={() => navigate('/events')}>
                        Browse Events
                      </Button>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {events.map((item: any) => (
                        <div key={item.registration.id} className="p-4 border rounded-lg hover:bg-muted/50 transition-colors">
                          <div className="flex justify-between items-start mb-2">
                            <div>
                              <p className="font-medium">{item.event.title}</p>
                              <p className="text-sm text-muted-foreground">
                                {new Date(item.event.date).toLocaleDateString()}
                              </p>
                            </div>
                            {getStatusBadge(item.event.status)}
                          </div>
                          <p className="text-sm text-muted-foreground">{item.event.location}</p>
                        </div>
                      ))}
                    </div>
                  )}
                </TabsContent>
                
                <TabsContent value="payments" className="space-y-4 mt-4">
                  {payments.length === 0 ? (
                    <div className="text-center py-12 text-muted-foreground">
                      <CreditCard className="w-12 h-12 mx-auto mb-4 opacity-50" />
                      <p>No payment history yet</p>
                      <p className="text-sm mt-2">Your transactions will appear here</p>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {payments.map((payment: any) => (
                        <div key={payment.transaction_id} className="p-4 border rounded-lg hover:bg-muted/50 transition-colors">
                          <div className="flex justify-between items-start mb-2">
                            <div>
                              <p className="font-medium">{payment.item_name}</p>
                              <p className="text-sm text-muted-foreground">
                                {new Date(payment.created_at).toLocaleDateString()}
                              </p>
                            </div>
                            <div className="text-right">
                              <p className="font-bold text-green-600">₹{payment.amount.toFixed(2)}</p>
                              {getStatusBadge(payment.status)}
                            </div>
                          </div>
                          <p className="text-xs text-muted-foreground font-mono">ID: {payment.transaction_id.slice(0, 16)}...</p>
                        </div>
                      ))}
                    </div>
                  )}
                </TabsContent>
                
                <TabsContent value="saved" className="space-y-4 mt-4">
                  {savedBlogs.length === 0 ? (
                    <div className="text-center py-12 text-muted-foreground">
                      <BookOpen className="w-12 h-12 mx-auto mb-4 opacity-50" />
                      <p>No saved articles yet</p>
                      <p className="text-sm mt-2">Save articles from our blog to read later</p>
                      <Button className="mt-4" onClick={() => navigate('/blogs')}>
                        Browse Blogs
                      </Button>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {savedBlogs.map((item: any) => (
                        <div key={item.blog.id} className="p-4 border rounded-lg hover:bg-muted/50 transition-colors">
                          <div className="flex justify-between items-start">
                            <div className="flex-1">
                              <p className="font-medium mb-1">{item.blog.title}</p>
                              <p className="text-sm text-muted-foreground line-clamp-2">
                                {item.blog.excerpt}
                              </p>
                              <p className="text-xs text-muted-foreground mt-2">
                                Saved on {new Date(item.saved_at).toLocaleDateString()}
                              </p>
                            </div>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => navigate(`/blogs/${item.blog.id}`)}
                            >
                              <ExternalLink className="w-4 h-4" />
                            </Button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
        </div>
      </div>
    </>
  );
};

export default UserDashboard;
