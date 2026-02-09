/**
 * useFocusManagement Hook
 * Manages focus for accessibility
 * WCAG 2.4.3 - Focus Order (Level A)
 */
import { useEffect, useRef, useCallback } from 'react';

interface FocusManagementOptions {
  restoreFocus?: boolean;
  autoFocus?: boolean;
}

export const useFocusManagement = (options: FocusManagementOptions = {}) => {
  const { restoreFocus = true, autoFocus = true } = options;
  const elementRef = useRef<HTMLElement | null>(null);
  const previousFocusRef = useRef<HTMLElement | null>(null);

  const setFocusRef = useCallback((element: HTMLElement | null) => {
    elementRef.current = element;
  }, []);

  const focusElement = useCallback(() => {
    if (elementRef.current) {
      elementRef.current.focus();
    }
  }, []);

  const storePreviousFocus = useCallback(() => {
    previousFocusRef.current = document.activeElement as HTMLElement;
  }, []);

  const restorePreviousFocus = useCallback(() => {
    if (previousFocusRef.current && restoreFocus) {
      previousFocusRef.current.focus();
    }
  }, [restoreFocus]);

  useEffect(() => {
    if (autoFocus) {
      storePreviousFocus();
      focusElement();
    }

    return () => {
      if (restoreFocus) {
        restorePreviousFocus();
      }
    };
  }, [autoFocus, restoreFocus, focusElement, storePreviousFocus, restorePreviousFocus]);

  return {
    setFocusRef,
    focusElement,
    storePreviousFocus,
    restorePreviousFocus,
  };
};