import { cn } from '@/lib/utils';
import { CheckCircle2, XCircle, Clock, AlertCircle, Loader2 } from 'lucide-react';

interface StatusIndicatorProps {
  status: 'success' | 'error' | 'warning' | 'pending' | 'loading';
  label?: string;
  showIcon?: boolean;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export const StatusIndicator = ({
  status,
  label,
  showIcon = true,
  size = 'md',
  className,
}: StatusIndicatorProps) => {
  const config = {
    success: {
      icon: CheckCircle2,
      color: 'text-green-600 bg-green-50 border-green-200',
      dotColor: 'bg-green-500',
    },
    error: {
      icon: XCircle,
      color: 'text-red-600 bg-red-50 border-red-200',
      dotColor: 'bg-red-500',
    },
    warning: {
      icon: AlertCircle,
      color: 'text-yellow-600 bg-yellow-50 border-yellow-200',
      dotColor: 'bg-yellow-500',
    },
    pending: {
      icon: Clock,
      color: 'text-blue-600 bg-blue-50 border-blue-200',
      dotColor: 'bg-blue-500',
    },
    loading: {
      icon: Loader2,
      color: 'text-gray-600 bg-gray-50 border-gray-200',
      dotColor: 'bg-gray-500',
    },
  };

  const { icon: Icon, color, dotColor } = config[status];

  const sizeClasses = {
    sm: 'text-xs px-2 py-1',
    md: 'text-sm px-3 py-1.5',
    lg: 'text-base px-4 py-2',
  };

  const iconSizes = {
    sm: 'h-3 w-3',
    md: 'h-4 w-4',
    lg: 'h-5 w-5',
  };

  return (
    <div
      className={cn(
        'inline-flex items-center gap-2 rounded-full border font-medium transition-all',
        color,
        sizeClasses[size],
        className
      )}
    >
      {showIcon && (
        <Icon
          className={cn(iconSizes[size], status === 'loading' && 'animate-spin')}
        />
      )}
      {label && <span>{label}</span>}
      {!label && !showIcon && (
        <div className={cn('h-2 w-2 rounded-full', dotColor)} />
      )}
    </div>
  );
};
