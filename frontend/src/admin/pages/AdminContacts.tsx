import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

const AdminContacts = () => {
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Contact Form Management</h1>
        <p className="text-gray-600 mt-2">View and respond to contact form submissions</p>
      </div>

      {/* Placeholder Content */}
      <Card>
        <CardHeader>
          <CardTitle>Contact Forms Overview</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-600">
            Contact form management features will be available here. View submissions,
            respond to inquiries, and mark messages as read or resolved.
          </p>
        </CardContent>
      </Card>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-gray-600">New Messages</p>
            <p className="text-3xl font-bold text-red-600 mt-2">---</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-gray-600">Read</p>
            <p className="text-3xl font-bold text-blue-600 mt-2">---</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-gray-600">Responded</p>
            <p className="text-3xl font-bold text-green-600 mt-2">---</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default AdminContacts;
