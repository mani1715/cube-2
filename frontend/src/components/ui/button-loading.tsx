import { Loader2 } from 'lucide-react';
import { Button, ButtonProps } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface ButtonLoadingProps extends ButtonProps {
  loading?: boolean;
  loadingText?: string;
}

export const ButtonLoading = ({
  loading = false,
  loadingText,
  children,
  disabled,
  className,
  ...props
}: ButtonLoadingProps) => {
  return (
    <Button
      disabled={disabled || loading}
      className={cn(
        'relative transition-all',
        loading && 'cursor-not-allowed',
        className
      )}
      {...props}
    >
      {loading && (
        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
      )}
      {loading && loadingText ? loadingText : children}
    </Button>
  );
};
