import { useEffect, useState } from 'react';
import { cn } from '@/lib/utils';

interface ProgressBarProps {
  value: number; // 0-100
  showLabel?: boolean;
  label?: string;
  className?: string;
  barClassName?: string;
  size?: 'sm' | 'md' | 'lg';
  animated?: boolean;
}

export const ProgressBar = ({
  value,
  showLabel = false,
  label,
  className,
  barClassName,
  size = 'md',
  animated = true,
}: ProgressBarProps) => {
  const [displayValue, setDisplayValue] = useState(0);

  useEffect(() => {
    if (animated) {
      const timer = setTimeout(() => setDisplayValue(value), 100);
      return () => clearTimeout(timer);
    } else {
      setDisplayValue(value);
    }
  }, [value, animated]);

  const sizeClasses = {
    sm: 'h-1',
    md: 'h-2',
    lg: 'h-3',
  };

  return (
    <div className={cn('w-full space-y-2', className)}>
      {(showLabel || label) && (
        <div className="flex items-center justify-between text-sm">
          <span className="text-muted-foreground">{label}</span>
          {showLabel && <span className="font-medium">{Math.round(displayValue)}%</span>}
        </div>
      )}
      <div className={cn('w-full bg-muted rounded-full overflow-hidden', sizeClasses[size])}>
        <div
          className={cn(
            'h-full bg-primary rounded-full transition-all duration-500 ease-out',
            barClassName
          )}
          style={{ width: `${displayValue}%` }}
        />
      </div>
    </div>
  );
};
