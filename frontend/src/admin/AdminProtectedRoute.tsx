import { Navigate, Outlet } from 'react-router-dom';
import { useAdmin } from '../contexts/AdminContext';
import { Loader2 } from 'lucide-react';

const AdminProtectedRoute = () => {
  const { admin, loading } = useAdmin();

  // Still checking authentication
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <Loader2 className="h-12 w-12 animate-spin text-primary mx-auto" />
          <p className="mt-4 text-gray-600">Verifying authentication...</p>
        </div>
      </div>
    );
  }

  // Not authenticated
  if (!admin) {
    return <Navigate to="/admin/login" replace />;
  }

  // Authenticated
  return <Outlet />;
};

export default AdminProtectedRoute;
