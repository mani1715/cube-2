// Phase 15 - Mobile Form Component with optimizations
import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Button } from '@/components/ui/button';
import MobileOptimizedInput from './MobileOptimizedInput';
import { Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

interface MobileFormField {
  name: string;
  label: string;
  type: string;
  placeholder?: string;
  required?: boolean;
  validation?: z.ZodTypeAny;
  icon?: React.ReactNode;
}

interface MobileOptimizedFormProps {
  fields: MobileFormField[];
  onSubmit: (data: any) => Promise<void>;
  submitButtonText?: string;
  className?: string;
  showResetButton?: boolean;
}

export const MobileOptimizedForm: React.FC<MobileOptimizedFormProps> = ({
  fields,
  onSubmit,
  submitButtonText = 'Submit',
  className,
  showResetButton = false,
}) => {
  const [isSubmitting, setIsSubmitting] = React.useState(false);

  // Build Zod schema from fields
  const schemaShape: Record<string, z.ZodTypeAny> = {};
  fields.forEach((field) => {
    if (field.validation) {
      schemaShape[field.name] = field.validation;
    } else if (field.required) {
      schemaShape[field.name] = z.string().min(1, `${field.label} is required`);
    } else {
      schemaShape[field.name] = z.string().optional();
    }
  });

  const schema = z.object(schemaShape);

  const {
    register,
    handleSubmit,
    formState: { errors, touchedFields },
    reset,
    watch,
  } = useForm({
    resolver: zodResolver(schema),
    mode: 'onBlur', // Validate on blur for better mobile UX
  });

  const handleFormSubmit = async (data: any) => {
    setIsSubmitting(true);
    try {
      await onSubmit(data);
      reset();
    } catch (error) {
      console.error('Form submission error:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form
      onSubmit={handleSubmit(handleFormSubmit)}
      className={cn('space-y-6', className)}
      data-testid="mobile-optimized-form"
    >
      {fields.map((field) => {
        const fieldValue = watch(field.name);
        const isTouched = touchedFields[field.name];
        const error = errors[field.name]?.message as string | undefined;
        const hasValue = fieldValue && fieldValue.length > 0;

        return (
          <MobileOptimizedInput
            key={field.name}
            {...register(field.name)}
            id={field.name}
            label={field.label}
            type={field.type}
            placeholder={field.placeholder}
            error={isTouched ? error : undefined}
            success={isTouched && !error && hasValue ? 'Looks good!' : undefined}
            required={field.required}
            icon={field.icon}
            touchOptimized={true}
            showValidation={true}
            autoComplete={field.type === 'email' ? 'email' : field.type === 'tel' ? 'tel' : 'off'}
            inputMode={
              field.type === 'email'
                ? 'email'
                : field.type === 'tel'
                ? 'tel'
                : field.type === 'number'
                ? 'numeric'
                : 'text'
            }
            data-testid={`form-field-${field.name}`}
          />
        );
      })}

      <div className="flex gap-3 pt-2">
        <Button
          type="submit"
          disabled={isSubmitting}
          className="flex-1 min-h-[48px] text-base font-medium"
          data-testid="submit-button"
        >
          {isSubmitting ? (
            <>
              <Loader2 className="mr-2 h-5 w-5 animate-spin" />
              Submitting...
            </>
          ) : (
            submitButtonText
          )}
        </Button>
        {showResetButton && (
          <Button
            type="button"
            variant="outline"
            onClick={() => reset()}
            disabled={isSubmitting}
            className="min-h-[48px] text-base"
            data-testid="reset-button"
          >
            Reset
          </Button>
        )}
      </div>
    </form>
  );
};

export default MobileOptimizedForm;