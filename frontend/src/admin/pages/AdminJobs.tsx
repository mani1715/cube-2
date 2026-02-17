import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Plus } from 'lucide-react';

const AdminJobs = () => {
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Job Postings Management</h1>
          <p className="text-gray-600 mt-2">Manage career opportunities and applications</p>
        </div>
        <Button className="flex items-center gap-2">
          <Plus className="w-4 h-4" />
          Post New Job
        </Button>
      </div>

      {/* Placeholder Content */}
      <Card>
        <CardHeader>
          <CardTitle>Jobs Overview</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-600">
            Job posting management features will be available here. Create job listings,
            review applications, and manage the hiring process.
          </p>
        </CardContent>
      </Card>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-gray-600">Active Postings</p>
            <p className="text-3xl font-bold text-green-600 mt-2">---</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-gray-600">Total Applications</p>
            <p className="text-3xl font-bold text-blue-600 mt-2">---</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-gray-600">Under Review</p>
            <p className="text-3xl font-bold text-yellow-600 mt-2">---</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-gray-600">Positions Filled</p>
            <p className="text-3xl font-bold text-primary mt-2">---</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default AdminJobs;
