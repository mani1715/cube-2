import { FileX, Search, Inbox } from 'lucide-react';

interface EmptyStateProps {
  icon?: 'file' | 'search' | 'inbox';
  title: string;
  description: string;
  action?: React.ReactNode;
}

export const EmptyState = ({ icon = 'inbox', title, description, action }: EmptyStateProps) => {
  const Icon = icon === 'file' ? FileX : icon === 'search' ? Search : Inbox;

  return (
    <div className="flex flex-col items-center justify-center py-12 px-4">
      <Icon className="w-16 h-16 text-gray-400 mb-4" />
      <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
      <p className="text-sm text-gray-600 text-center max-w-sm mb-4">{description}</p>
      {action && <div className="mt-2">{action}</div>}
    </div>
  );
};
