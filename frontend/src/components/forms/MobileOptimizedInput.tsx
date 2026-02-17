// Phase 15 - Mobile-optimized form inputs
import React, { forwardRef, useState } from 'react';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { cn } from '@/lib/utils';
import { Eye, EyeOff, AlertCircle, CheckCircle2 } from 'lucide-react';

interface MobileOptimizedInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  success?: string;
  showValidation?: boolean;
  touchOptimized?: boolean;
  icon?: React.ReactNode;
}

export const MobileOptimizedInput = forwardRef<HTMLInputElement, MobileOptimizedInputProps>(
  ({ 
    label, 
    error, 
    success,
    showValidation = true,
    touchOptimized = true, 
    className, 
    type,
    icon,
    ...props 
  }, ref) => {
    const [showPassword, setShowPassword] = useState(false);
    const [isFocused, setIsFocused] = useState(false);
    const isPassword = type === 'password';
    const inputType = isPassword && showPassword ? 'text' : type;

    return (
      <div className="w-full space-y-2">
        {label && (
          <Label 
            htmlFor={props.id} 
            className={cn(
              'text-base font-medium',
              touchOptimized && 'min-h-[24px]'
            )}
          >
            {label}
            {props.required && <span className="text-destructive ml-1">*</span>}
          </Label>
        )}
        <div className="relative">
          {icon && (
            <div className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">
              {icon}
            </div>
          )}
          <Input
            ref={ref}
            type={inputType}
            className={cn(
              'w-full transition-all',
              touchOptimized && 'min-h-[48px] text-base', // Larger touch targets for mobile
              icon && 'pl-10',
              isPassword && 'pr-10',
              error && 'border-destructive focus-visible:ring-destructive',
              success && showValidation && 'border-green-500 focus-visible:ring-green-500',
              isFocused && 'ring-2',
              className
            )}
            onFocus={(e) => {
              setIsFocused(true);
              props.onFocus?.(e);
            }}
            onBlur={(e) => {
              setIsFocused(false);
              props.onBlur?.(e);
            }}
            aria-invalid={!!error}
            aria-describedby={error ? `${props.id}-error` : undefined}
            data-testid={props['data-testid'] || 'mobile-optimized-input'}
            {...props}
          />
          {isPassword && (
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
              tabIndex={-1}
              aria-label={showPassword ? 'Hide password' : 'Show password'}
              data-testid="password-toggle"
            >
              {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
            </button>
          )}
          {showValidation && !isPassword && (
            <>
              {error && (
                <AlertCircle className="absolute right-3 top-1/2 -translate-y-1/2 h-5 w-5 text-destructive" />
              )}
              {success && !error && (
                <CheckCircle2 className="absolute right-3 top-1/2 -translate-y-1/2 h-5 w-5 text-green-500" />
              )}
            </>
          )}
        </div>
        {error && (
          <p 
            id={`${props.id}-error`}
            className="text-sm text-destructive flex items-center gap-1"
            role="alert"
            data-testid="input-error"
          >
            <AlertCircle className="h-4 w-4" />
            {error}
          </p>
        )}
        {success && !error && showValidation && (
          <p 
            className="text-sm text-green-600 flex items-center gap-1"
            data-testid="input-success"
          >
            <CheckCircle2 className="h-4 w-4" />
            {success}
          </p>
        )}
      </div>
    );
  }
);

MobileOptimizedInput.displayName = 'MobileOptimizedInput';

export default MobileOptimizedInput;