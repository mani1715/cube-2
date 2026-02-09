import { LucideIcon, Inbox, FileX, Search, Calendar, Users, BookOpen, Briefcase, MessageCircle, ClipboardList } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface EmptyStateProps {
  icon?: 'inbox' | 'file' | 'search' | 'calendar' | 'users' | 'book' | 'briefcase' | 'message' | 'clipboard';
  title: string;
  description: string;
  action?: {
    label: string;
    onClick: () => void;
  };
  secondaryAction?: {
    label: string;
    onClick: () => void;
  };
  className?: string;
}

const iconMap: Record<string, LucideIcon> = {
  inbox: Inbox,
  file: FileX,
  search: Search,
  calendar: Calendar,
  users: Users,
  book: BookOpen,
  briefcase: Briefcase,
  message: MessageCircle,
  clipboard: ClipboardList,
};

export const EnhancedEmptyState = ({
  icon = 'inbox',
  title,
  description,
  action,
  secondaryAction,
  className,
}: EmptyStateProps) => {
  const Icon = iconMap[icon];

  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center py-16 px-4 text-center',
        className
      )}
    >
      {/* Icon with subtle animation */}
      <div className="relative mb-6">
        <div className="absolute inset-0 bg-primary/5 rounded-full blur-2xl animate-pulse" />
        <div className="relative bg-muted rounded-full p-6">
          <Icon className="w-12 h-12 text-muted-foreground" />
        </div>
      </div>

      {/* Title */}
      <h3 className="text-xl font-semibold text-foreground mb-2">{title}</h3>

      {/* Description */}
      <p className="text-sm text-muted-foreground max-w-md mb-6">{description}</p>

      {/* Actions */}
      {(action || secondaryAction) && (
        <div className="flex flex-col sm:flex-row gap-3">
          {action && (
            <Button onClick={action.onClick} size="lg">
              {action.label}
            </Button>
          )}
          {secondaryAction && (
            <Button onClick={secondaryAction.onClick} variant="outline" size="lg">
              {secondaryAction.label}
            </Button>
          )}
        </div>
      )}
    </div>
  );
};
