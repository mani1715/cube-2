import { Link, useLocation } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Calendar, 
  CalendarCheck,
  FileText, 
  Users, 
  UserPlus, 
  Briefcase, 
  MessageSquare,
  AlertTriangle,
  Settings 
} from 'lucide-react';

const AdminSidebar = () => {
  const location = useLocation();
  
  const menuItems = [
    { icon: LayoutDashboard, label: 'Dashboard', path: '/admin' },
    { icon: CalendarCheck, label: 'Sessions', path: '/admin/sessions' },
    { icon: Calendar, label: 'Events', path: '/admin/events' },
    { icon: FileText, label: 'Blogs', path: '/admin/blogs' },
    { icon: Users, label: 'Psychologists', path: '/admin/psychologists' },
    { icon: UserPlus, label: 'Volunteers', path: '/admin/volunteers' },
    { icon: Briefcase, label: 'Jobs', path: '/admin/jobs' },
    { icon: MessageSquare, label: 'Contacts', path: '/admin/contacts' },
    { icon: AlertTriangle, label: 'Error Tracking', path: '/admin/errors' },
    { icon: Settings, label: 'Settings', path: '/admin/settings' },
  ];

  const isActive = (path: string) => {
    if (path === '/admin') {
      return location.pathname === path;
    }
    return location.pathname.startsWith(path);
  };

  return (
    <aside className="w-64 bg-white border-r border-gray-200 flex flex-col">
      {/* Logo/Brand */}
      <div className="p-6 border-b border-gray-200">
        <h1 className="text-2xl font-bold text-primary">A-Cube Admin</h1>
      </div>

      {/* Navigation Menu */}
      <nav className="flex-1 p-4 space-y-1">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const active = isActive(item.path);
          
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`
                flex items-center gap-3 px-4 py-3 rounded-lg transition-colors
                ${active 
                  ? 'bg-primary text-white' 
                  : 'text-gray-700 hover:bg-gray-100'
                }
              `}
            >
              <Icon className="w-5 h-5" />
              <span className="font-medium">{item.label}</span>
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-gray-200 text-sm text-gray-500">
        <p>© 2024 A-Cube</p>
      </div>
    </aside>
  );
};

export default AdminSidebar;
