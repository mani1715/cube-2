/**
 * Accessible Form Error Message Component
 * WCAG 3.3.1 - Error Identification (Level A)
 */
import { AlertCircle } from 'lucide-react';
import { cn } from '@/lib/utils';

interface FormErrorMessageProps {
  error?: string;
  id?: string;
  className?: string;
}

export const FormErrorMessage: React.FC<FormErrorMessageProps> = ({
  error,
  id,
  className,
}) => {
  if (!error) return null;

  return (
    <div
      id={id}
      role="alert"
      aria-live="polite"
      className={cn(
        'flex items-start gap-2 text-sm text-red-600 dark:text-red-400 mt-1.5 animate-in slide-in-from-top-1',
        className
      )}
    >
      <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" aria-hidden="true" />
      <span>{error}</span>
    </div>
  );
};
