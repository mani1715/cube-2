import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { adminErrorAPI as adminAPI } from '@/lib/adminApi';
import { toast } from 'sonner';
import { AlertTriangle, CheckCircle, Trash2, RefreshCw } from 'lucide-react';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

interface ErrorLog {
  id: string;
  error_type: string;
  severity: string;
  message: string;
  stack_trace?: string;
  component?: string;
  url?: string;
  admin_email?: string;
  timestamp: string;
  resolved: boolean;
}

interface ErrorStats {
  total: number;
  unresolved: number;
  critical: number;
  frontend: number;
  backend: number;
}

interface Pagination {
  total: number;
  page: number;
  limit: number;
  pages: number;
}

const AdminErrors = () => {
  const [errors, setErrors] = useState<ErrorLog[]>([]);
  const [stats, setStats] = useState<ErrorStats>({
    total: 0,
    unresolved: 0,
    critical: 0,
    frontend: 0,
    backend: 0,
  });
  const [pagination, setPagination] = useState<Pagination>({
    total: 0,
    page: 1,
    limit: 50,
    pages: 0,
  });
  const [loading, setLoading] = useState(true);
  const [severityFilter, setSeverityFilter] = useState<string>('all');
  const [typeFilter, setTypeFilter] = useState<string>('all');
  const [resolvedFilter, setResolvedFilter] = useState<string>('unresolved');
  const [selectedError, setSelectedError] = useState<ErrorLog | null>(null);

  const fetchErrors = async () => {
    try {
      setLoading(true);
      const filters: any = {};
      
      if (severityFilter !== 'all') filters.severity = severityFilter;
      if (typeFilter !== 'all') filters.error_type = typeFilter;
      if (resolvedFilter !== 'all') filters.resolved = resolvedFilter === 'resolved';

      const response = await adminAPI.getErrors(pagination.page, pagination.limit, filters);
      setErrors(response.data || []);
      setPagination(response.pagination || pagination);
    } catch (error: any) {
      toast.error('Failed to fetch errors');
      console.error('Error fetching errors:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await adminAPI.getErrorStats();
      setStats(response);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  useEffect(() => {
    fetchErrors();
    fetchStats();
  }, [pagination.page, severityFilter, typeFilter, resolvedFilter]);

  const handleResolve = async (errorId: string) => {
    try {
      await adminAPI.resolveError(errorId);
      toast.success('Error marked as resolved');
      fetchErrors();
      fetchStats();
    } catch (error) {
      toast.error('Failed to resolve error');
    }
  };

  const handleDelete = async (errorId: string) => {
    if (!confirm('Are you sure you want to delete this error log?')) return;
    
    try {
      await adminAPI.deleteError(errorId);
      toast.success('Error deleted successfully');
      fetchErrors();
      fetchStats();
    } catch (error) {
      toast.error('Failed to delete error');
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-100 text-red-800 border-red-300';
      case 'error':
        return 'bg-orange-100 text-orange-800 border-orange-300';
      case 'warning':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('en-US', {
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
        <h1 className="text-3xl font-bold text-gray-900">Error Tracking</h1>
        <p className="text-gray-600 mt-2">Monitor and resolve application errors</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-gray-600">Total Errors</p>
            <p className="text-3xl font-bold text-gray-900 mt-2">{stats.total}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-gray-600">Unresolved</p>
            <p className="text-3xl font-bold text-orange-600 mt-2">{stats.unresolved}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-gray-600">Critical</p>
            <p className="text-3xl font-bold text-red-600 mt-2">{stats.critical}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-gray-600">Frontend</p>
            <p className="text-3xl font-bold text-blue-600 mt-2">{stats.frontend}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-gray-600">Backend</p>
            <p className="text-3xl font-bold text-purple-600 mt-2">{stats.backend}</p>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-wrap gap-4 items-center">
            <div className="flex-1 min-w-[200px]">
              <label className="text-sm font-medium text-gray-700 mb-2 block">Severity</label>
              <Select value={severityFilter} onValueChange={setSeverityFilter}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Severities</SelectItem>
                  <SelectItem value="critical">Critical</SelectItem>
                  <SelectItem value="error">Error</SelectItem>
                  <SelectItem value="warning">Warning</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="flex-1 min-w-[200px]">
              <label className="text-sm font-medium text-gray-700 mb-2 block">Type</label>
              <Select value={typeFilter} onValueChange={setTypeFilter}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Types</SelectItem>
                  <SelectItem value="frontend">Frontend</SelectItem>
                  <SelectItem value="backend">Backend</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="flex-1 min-w-[200px]">
              <label className="text-sm font-medium text-gray-700 mb-2 block">Status</label>
              <Select value={resolvedFilter} onValueChange={setResolvedFilter}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Status</SelectItem>
                  <SelectItem value="unresolved">Unresolved</SelectItem>
                  <SelectItem value="resolved">Resolved</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="pt-6">
              <Button onClick={() => { fetchErrors(); fetchStats(); }} variant="outline">
                <RefreshCw className="h-4 w-4 mr-2" />
                Refresh
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Errors List */}
      <Card>
        <CardHeader>
          <CardTitle>Error Logs</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8 text-gray-500">Loading errors...</div>
          ) : errors.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <AlertTriangle className="h-12 w-12 mx-auto mb-4 text-gray-400" />
              <p>No errors found</p>
            </div>
          ) : (
            <div className="space-y-4">
              {errors.map((error) => (
                <div
                  key={error.id}
                  className={`border rounded-lg p-4 ${getSeverityColor(error.severity)}`}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="px-2 py-1 rounded text-xs font-medium bg-white border">
                          {error.error_type}
                        </span>
                        <span className="px-2 py-1 rounded text-xs font-medium bg-white border">
                          {error.severity}
                        </span>
                        {error.resolved && (
                          <span className="px-2 py-1 rounded text-xs font-medium bg-green-100 text-green-800 border border-green-300">
                            Resolved
                          </span>
                        )}
                      </div>
                      <p className="font-medium text-gray-900 mb-1">{error.message}</p>
                      <p className="text-sm text-gray-600">
                        {error.component && `Component: ${error.component} • `}
                        Admin: {error.admin_email} • {formatDate(error.timestamp)}
                      </p>
                      {error.url && (
                        <p className="text-xs text-gray-500 mt-1">URL: {error.url}</p>
                      )}
                    </div>
                    <div className="flex gap-2 ml-4">
                      {!error.resolved && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleResolve(error.id)}
                          className="flex items-center gap-1"
                        >
                          <CheckCircle className="h-4 w-4" />
                          Resolve
                        </Button>
                      )}
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleDelete(error.id)}
                        className="flex items-center gap-1 text-red-600 hover:text-red-700"
                      >
                        <Trash2 className="h-4 w-4" />
                        Delete
                      </Button>
                    </div>
                  </div>
                  {error.stack_trace && (
                    <details className="mt-2">
                      <summary className="cursor-pointer text-sm font-medium text-gray-700 hover:text-gray-900">
                        View Stack Trace
                      </summary>
                      <pre className="mt-2 p-3 bg-white rounded text-xs overflow-auto max-h-48 border">
                        {error.stack_trace}
                      </pre>
                    </details>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Pagination */}
          {pagination.pages > 1 && (
            <div className="flex items-center justify-between mt-6 pt-4 border-t">
              <p className="text-sm text-gray-600">
                Showing page {pagination.page} of {pagination.pages}
              </p>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPagination({ ...pagination, page: pagination.page - 1 })}
                  disabled={pagination.page === 1}
                >
                  Previous
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPagination({ ...pagination, page: pagination.page + 1 })}
                  disabled={pagination.page >= pagination.pages}
                >
                  Next
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default AdminErrors;
