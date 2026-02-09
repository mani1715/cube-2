/**
 * Accessible Form Wrapper Component
 * Provides WCAG-compliant form structure with error announcements
 */
import React, { useRef, useEffect } from 'react';
import { LiveRegion } from './LiveRegion';

interface AccessibleFormProps {
  children: React.ReactNode;
  onSubmit: (e: React.FormEvent) => void;
  errors?: Record<string, string>;
  isSubmitting?: boolean;
  ariaLabel?: string;
  className?: string;
}

export const AccessibleForm: React.FC<AccessibleFormProps> = ({
  children,
  onSubmit,
  errors = {},
  isSubmitting = false,
  ariaLabel,
  className = '',
}) => {
  const errorMessage = Object.values(errors).filter(Boolean).join(', ');
  const errorCount = Object.values(errors).filter(Boolean).length;

  return (
    <>
      {errorMessage && (
        <LiveRegion
          message={`Form has ${errorCount} error${errorCount > 1 ? 's' : ''}: ${errorMessage}`}
          politeness="assertive"
        />
      )}
      {isSubmitting && (
        <LiveRegion
          message="Submitting form, please wait"
          politeness="polite"
        />
      )}
      <form
        onSubmit={onSubmit}
        aria-label={ariaLabel}
        aria-busy={isSubmitting}
        noValidate
        className={className}
      >
        {children}
      </form>
    </>
  );
};
