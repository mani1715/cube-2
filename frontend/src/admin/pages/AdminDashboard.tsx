import { useState, useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { adminDashboardAPI } from '@/lib/adminApi';
import { CardSkeleton } from '@/components/ui/loading-skeleton';
import { Users, Calendar, FileText, UserCheck, HandHeart, Briefcase, MessageSquare } from 'lucide-react';

interface DashboardStats {
  sessions: {
    total: number;
    pending: number;
    confirmed: number;
    recent: number;
  };
  events: {
    total: number;
    active: number;
  };
  blogs: {
    total: number;
    published: number;
  };
  psychologists: {
    total: number;
    active: number;
  };
  volunteers: {
    total: number;
    pending: number;
  };
  contacts: {
    total: number;
    pending: number;
    recent: number;
  };
  jobs: {
    total: number;
    active: number;
  };
}

const AdminDashboard = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const response = await adminDashboardAPI.getDashboard();
      setStats(response.stats);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch dashboard data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-2">Welcome to A-Cube Admin Panel</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[...Array(8)].map((_, i) => (
            <Card key={i}>
              <CardContent className="pt-6">
                <CardSkeleton />
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-2">Welcome to A-Cube Admin Panel</p>
        </div>
        <Card>
          <CardContent className="pt-6">
            <p className="text-red-600">{error}</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  const mainStats = [
    {
      label: 'Total Sessions',
      value: stats?.sessions.total || 0,
      subtitle: `${stats?.sessions.pending || 0} pending`,
      icon: Users,
      color: 'bg-blue-50 text-blue-700',
      iconColor: 'text-blue-600',
    },
    {
      label: 'Active Events',
      value: stats?.events.active || 0,
      subtitle: `${stats?.events.total || 0} total`,
      icon: Calendar,
      color: 'bg-green-50 text-green-700',
      iconColor: 'text-green-600',
    },
    {
      label: 'Published Blogs',
      value: stats?.blogs.published || 0,
      subtitle: `${stats?.blogs.total || 0} total`,
      icon: FileText,
      color: 'bg-purple-50 text-purple-700',
      iconColor: 'text-purple-600',
    },
    {
      label: 'Active Psychologists',
      value: stats?.psychologists.active || 0,
      subtitle: `${stats?.psychologists.total || 0} total`,
      icon: UserCheck,
      color: 'bg-orange-50 text-orange-700',
      iconColor: 'text-orange-600',
    },
    {
      label: 'Volunteers',
      value: stats?.volunteers.total || 0,
      subtitle: `${stats?.volunteers.pending || 0} pending`,
      icon: HandHeart,
      color: 'bg-pink-50 text-pink-700',
      iconColor: 'text-pink-600',
    },
    {
      label: 'Active Jobs',
      value: stats?.jobs.active || 0,
      subtitle: `${stats?.jobs.total || 0} total`,
      icon: Briefcase,
      color: 'bg-indigo-50 text-indigo-700',
      iconColor: 'text-indigo-600',
    },
    {
      label: 'Contact Requests',
      value: stats?.contacts.total || 0,
      subtitle: `${stats?.contacts.pending || 0} pending`,
      icon: MessageSquare,
      color: 'bg-teal-50 text-teal-700',
      iconColor: 'text-teal-600',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-2">Welcome to A-Cube Admin Panel</p>
      </div>

      {/* Main Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {mainStats.map((stat) => {
          const Icon = stat.icon;
          return (
            <Card key={stat.label}>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 mb-1">{stat.label}</p>
                    <p className={`text-3xl font-bold ${stat.color}`}>{stat.value}</p>
                    <p className="text-xs text-gray-500 mt-1">{stat.subtitle}</p>
                  </div>
                  <Icon className={`w-10 h-10 ${stat.iconColor}`} />
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardContent className="pt-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Sessions (7 days)</h3>
            <div className="flex items-center justify-between">
              <p className="text-4xl font-bold text-blue-600">{stats?.sessions.recent || 0}</p>
              <p className="text-sm text-gray-600">New bookings this week</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Contacts (7 days)</h3>
            <div className="flex items-center justify-between">
              <p className="text-4xl font-bold text-teal-600">{stats?.contacts.recent || 0}</p>
              <p className="text-sm text-gray-600">New messages this week</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Stats Summary */}
      <Card>
        <CardContent className="pt-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Platform Overview</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-4 bg-yellow-50 rounded-lg">
              <p className="text-2xl font-bold text-yellow-700">{stats?.sessions.pending || 0}</p>
              <p className="text-sm text-gray-600 mt-1">Pending Sessions</p>
            </div>
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <p className="text-2xl font-bold text-green-700">{stats?.sessions.confirmed || 0}</p>
              <p className="text-sm text-gray-600 mt-1">Confirmed Sessions</p>
            </div>
            <div className="text-center p-4 bg-orange-50 rounded-lg">
              <p className="text-2xl font-bold text-orange-700">{stats?.volunteers.pending || 0}</p>
              <p className="text-sm text-gray-600 mt-1">Pending Volunteers</p>
            </div>
            <div className="text-center p-4 bg-teal-50 rounded-lg">
              <p className="text-2xl font-bold text-teal-700">{stats?.contacts.pending || 0}</p>
              <p className="text-sm text-gray-600 mt-1">Pending Contacts</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AdminDashboard;
