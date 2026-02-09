/**
 * Accessible Form Success Message Component
 */
import { CheckCircle2 } from 'lucide-react';
import { cn } from '@/lib/utils';

interface FormSuccessMessageProps {
  message?: string;
  id?: string;
  className?: string;
}

export const FormSuccessMessage: React.FC<FormSuccessMessageProps> = ({
  message,
  id,
  className,
}) => {
  if (!message) return null;

  return (
    <div
      id={id}
      role="status"
      aria-live="polite"
      className={cn(
        'flex items-start gap-2 text-sm text-green-600 dark:text-green-400 mt-1.5 animate-in slide-in-from-top-1',
        className
      )}
    >
      <CheckCircle2 className="w-4 h-4 mt-0.5 flex-shrink-0 animate-scale-in" aria-hidden="true" />
      <span>{message}</span>
    </div>
  );
};
