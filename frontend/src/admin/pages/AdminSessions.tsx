import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ButtonLoading } from '@/components/ui/button-loading';
import { EnhancedEmptyState } from '@/components/ui/enhanced-empty-state';
import { TableSkeleton, StatsCardSkeleton } from '@/components/ui/enhanced-skeleton';
import { StatusIndicator } from '@/components/ui/status-indicator';
import { adminSessionsAPI } from '@/lib/adminApi';
import { toast } from 'sonner';

interface SessionBooking {
  id: string;
  full_name: string;
  email: string;
  phone: string;
  age: string;
  gender: string;
  therapy_type: string;
  concerns: string[];
  current_feelings: string;
  previous_therapy: string;
  preferred_time: string;
  additional_info?: string;
  status: string;
  created_at: string;
}

interface Stats {
  pending: number;
  confirmed: number;
  completed: number;
  cancelled: number;
  total: number;
}

interface Pagination {
  total: number;
  page: number;
  limit: number;
  pages: number;
}

const AdminSessions = () => {
  const [sessions, setSessions] = useState<SessionBooking[]>([]);
  const [stats, setStats] = useState<Stats>({
    pending: 0,
    confirmed: 0,
    completed: 0,
    cancelled: 0,
    total: 0,
  });
  const [pagination, setPagination] = useState<Pagination>({
    total: 0,
    page: 1,
    limit: 10,
    pages: 0,
  });
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [updatingId, setUpdatingId] = useState<string | null>(null);

  const fetchSessions = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await adminSessionsAPI.getSessions(
        pagination.page,
        pagination.limit,
        statusFilter
      );
      setSessions(response.data);
      setStats(response.stats);
      setPagination(response.pagination);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch sessions');
      console.error('Error fetching sessions:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSessions();
  }, [pagination.page, statusFilter]);

  const handleStatusUpdate = async (sessionId: string, newStatus: string) => {
    try {
      setUpdatingId(sessionId);
      await adminSessionsAPI.updateSessionStatus(sessionId, newStatus);
      toast.success('Session status updated successfully');
      // Refresh the sessions list
      await fetchSessions();
    } catch (err: any) {
      toast.error(err.message || 'Failed to update status');
      console.error('Error updating status:', err);
    } finally {
      setUpdatingId(null);
    }
  };

  const getStatusBadgeColor = (status: string) => {
    switch (status) {
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'confirmed':
        return 'bg-green-100 text-green-800';
      case 'completed':
        return 'bg-blue-100 text-blue-800';
      case 'cancelled':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Session Management</h1>
        <p className="text-gray-600 mt-2">Manage therapy session bookings</p>
      </div>

      {/* Stats Grid */}
      {loading && sessions.length === 0 ? (
        <StatsCardSkeleton count={4} />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 stagger-reveal">
          <Card className="hover-lift">
            <CardContent className="pt-6">
              <p className="text-sm text-gray-600">Pending Sessions</p>
              <p className="text-3xl font-bold text-yellow-600 mt-2">{stats.pending}</p>
            </CardContent>
          </Card>
          <Card className="hover-lift">
            <CardContent className="pt-6">
              <p className="text-sm text-gray-600">Confirmed Sessions</p>
              <p className="text-3xl font-bold text-green-600 mt-2">{stats.confirmed}</p>
            </CardContent>
          </Card>
          <Card className="hover-lift">
            <CardContent className="pt-6">
              <p className="text-sm text-gray-600">Completed Sessions</p>
              <p className="text-3xl font-bold text-blue-600 mt-2">{stats.completed}</p>
            </CardContent>
          </Card>
          <Card className="hover-lift">
            <CardContent className="pt-6">
              <p className="text-sm text-gray-600">Total Sessions</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">{stats.total}</p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex gap-2">
            <Button
              variant={statusFilter === 'all' ? 'default' : 'outline'}
              onClick={() => {
                setStatusFilter('all');
                setPagination((prev) => ({ ...prev, page: 1 }));
              }}
            >
              All
            </Button>
            <Button
              variant={statusFilter === 'pending' ? 'default' : 'outline'}
              onClick={() => {
                setStatusFilter('pending');
                setPagination((prev) => ({ ...prev, page: 1 }));
              }}
            >
              Pending
            </Button>
            <Button
              variant={statusFilter === 'confirmed' ? 'default' : 'outline'}
              onClick={() => {
                setStatusFilter('confirmed');
                setPagination((prev) => ({ ...prev, page: 1 }));
              }}
            >
              Confirmed
            </Button>
            <Button
              variant={statusFilter === 'completed' ? 'default' : 'outline'}
              onClick={() => {
                setStatusFilter('completed');
                setPagination((prev) => ({ ...prev, page: 1 }));
              }}
            >
              Completed
            </Button>
            <Button
              variant={statusFilter === 'cancelled' ? 'default' : 'outline'}
              onClick={() => {
                setStatusFilter('cancelled');
                setPagination((prev) => ({ ...prev, page: 1 }));
              }}
            >
              Cancelled
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Sessions Table */}
      <Card>
        <CardHeader>
          <CardTitle>Sessions List</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <TableSkeleton rows={5} />
          ) : error ? (
            <EnhancedEmptyState
              icon="file"
              title="Failed to Load Sessions"
              description={error}
              action={{
                label: 'Retry',
                onClick: fetchSessions,
              }}
            />
          ) : sessions.length === 0 ? (
            <EnhancedEmptyState
              icon="calendar"
              title="No Sessions Found"
              description={
                statusFilter === 'all'
                  ? 'No session bookings have been created yet.'
                  : `No ${statusFilter} sessions found. Try changing the filter.`
              }
              action={{
                label: 'Clear Filters',
                onClick: () => setStatusFilter('all'),
              }}
            />
          ) : (
            <>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Client
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Contact
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Type
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Preferred Time
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Created
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Status
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {sessions.map((session) => (
                      <tr key={session.id}>
                        <td className="px-4 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-gray-900">
                            {session.full_name}
                          </div>
                          <div className="text-sm text-gray-500">
                            {session.age}, {session.gender}
                          </div>
                        </td>
                        <td className="px-4 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900">{session.email}</div>
                          <div className="text-sm text-gray-500">{session.phone}</div>
                        </td>
                        <td className="px-4 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900 capitalize">
                            {session.therapy_type}
                          </div>
                        </td>
                        <td className="px-4 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900">{session.preferred_time}</div>
                        </td>
                        <td className="px-4 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900">
                            {formatDate(session.created_at)}
                          </div>
                        </td>
                        <td className="px-4 py-4 whitespace-nowrap">
                          <StatusIndicator
                            status={
                              session.status === 'pending' ? 'pending' :
                              session.status === 'confirmed' ? 'success' :
                              session.status === 'completed' ? 'success' :
                              'error'
                            }
                            label={session.status}
                            size="sm"
                          />
                        </td>
                        <td className="px-4 py-4 whitespace-nowrap text-sm">
                          <div className="flex gap-2">
                            {session.status !== 'confirmed' && (
                              <ButtonLoading
                                size="sm"
                                variant="outline"
                                onClick={() => handleStatusUpdate(session.id, 'confirmed')}
                                loading={updatingId === session.id}
                                disabled={updatingId === session.id}
                                className="text-green-600 hover:text-green-700 transition-all"
                              >
                                Confirm
                              </ButtonLoading>
                            )}
                            {session.status !== 'completed' && session.status !== 'cancelled' && (
                              <ButtonLoading
                                size="sm"
                                variant="outline"
                                onClick={() => handleStatusUpdate(session.id, 'completed')}
                                loading={updatingId === session.id}
                                disabled={updatingId === session.id}
                                className="text-blue-600 hover:text-blue-700 transition-all"
                              >
                                Complete
                              </ButtonLoading>
                            )}
                            {session.status !== 'cancelled' && session.status !== 'completed' && (
                              <ButtonLoading
                                size="sm"
                                variant="outline"
                                onClick={() => handleStatusUpdate(session.id, 'cancelled')}
                                loading={updatingId === session.id}
                                disabled={updatingId === session.id}
                                className="text-red-600 hover:text-red-700 transition-all"
                              >
                                Cancel
                              </ButtonLoading>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Pagination */}
              <div className="mt-4 flex items-center justify-between">
                <div className="text-sm text-gray-700">
                  Showing {sessions.length} of {pagination.total} sessions
                </div>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    onClick={() =>
                      setPagination((prev) => ({ ...prev, page: prev.page - 1 }))
                    }
                    disabled={pagination.page === 1}
                  >
                    Previous
                  </Button>
                  <span className="px-4 py-2 text-sm">
                    Page {pagination.page} of {pagination.pages}
                  </span>
                  <Button
                    variant="outline"
                    onClick={() =>
                      setPagination((prev) => ({ ...prev, page: prev.page + 1 }))
                    }
                    disabled={pagination.page >= pagination.pages}
                  >
                    Next
                  </Button>
                </div>
              </div>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default AdminSessions;
