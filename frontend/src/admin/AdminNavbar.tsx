import { Bell, User, LogOut, Shield, Eye } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAdmin } from '../contexts/AdminContext';
import { toast } from '../lib/toast';
import GlobalSearch from './components/GlobalSearch';

const AdminNavbar = () => {
  const navigate = useNavigate();
  const { admin, logout } = useAdmin();

  const handleLogout = async () => {
    try {
      await logout();
      toast.success('Logged out successfully');
      navigate('/admin/login');
    } catch (error) {
      console.error('Logout error:', error);
      toast.error('Logout failed', 'Please try again');
    }
  };

  const getRoleIcon = () => {
    if (admin?.role === 'super_admin') return <Shield className="w-4 h-4" />;
    if (admin?.role === 'viewer') return <Eye className="w-4 h-4" />;
    return <User className="w-4 h-4" />;
  };

  const getRoleBadgeColor = () => {
    if (admin?.role === 'super_admin') return 'bg-purple-100 text-purple-700';
    if (admin?.role === 'admin') return 'bg-blue-100 text-blue-700';
    return 'bg-gray-100 text-gray-700';
  };

  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between gap-6">
        {/* Page Title */}
        <div className="flex-shrink-0">
          <h2 className="text-xl font-semibold text-gray-800">Admin Panel</h2>
        </div>

        {/* Global Search - Center */}
        <div className="flex-1 max-w-2xl">
          <GlobalSearch />
        </div>

        {/* Right side actions */}
        <div className="flex items-center gap-4 flex-shrink-0">
          {/* Notifications */}
          <button 
            className="p-2 rounded-lg hover:bg-gray-100 transition-colors relative"
            aria-label="Notifications"
          >
            <Bell className="w-5 h-5 text-gray-600" />
            {/* Notification badge - placeholder */}
            <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
          </button>

          {/* User Profile with Role */}
          <div className="flex items-center gap-3">
            <div className="text-right">
              <p className="text-sm font-medium text-gray-700">{admin?.email || 'Admin'}</p>
              <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${getRoleBadgeColor()}`}>
                {getRoleIcon()}
                {admin?.role?.replace('_', ' ') || 'Admin'}
              </span>
            </div>
            <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center">
              <User className="w-5 h-5 text-white" />
            </div>
          </div>

          {/* Logout Button */}
          <button
            onClick={handleLogout}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-red-50 hover:bg-red-100 text-red-600 transition-colors"
            aria-label="Logout"
          >
            <LogOut className="w-5 h-5" />
            <span className="text-sm font-medium">Logout</span>
          </button>
        </div>
      </div>
    </header>
  );
};

export default AdminNavbar;
