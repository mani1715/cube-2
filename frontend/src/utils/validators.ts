/**
 * Common form validation utilities
 * Reusable validation functions for forms
 */

export const validators = {
  required: (value: any) => {
    if (typeof value === 'string') {
      return value.trim().length > 0;
    }
    return value !== null && value !== undefined && value !== '';
  },

  email: (value: string) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(value);
  },

  phone: (value: string) => {
    // Accepts various phone formats
    const phoneRegex = /^[+]?[(]?[0-9]{1,4}[)]?[-\s.]?[(]?[0-9]{1,4}[)]?[-\s.]?[0-9]{1,9}$/;
    return phoneRegex.test(value.replace(/\s/g, ''));
  },

  minLength: (min: number) => (value: string) => {
    return value.trim().length >= min;
  },

  maxLength: (max: number) => (value: string) => {
    return value.trim().length <= max;
  },

  minValue: (min: number) => (value: number) => {
    return value >= min;
  },

  maxValue: (max: number) => (value: number) => {
    return value <= max;
  },

  pattern: (pattern: RegExp) => (value: string) => {
    return pattern.test(value);
  },

  url: (value: string) => {
    try {
      new URL(value);
      return true;
    } catch {
      return false;
    }
  },

  strongPassword: (value: string) => {
    // At least 8 chars, 1 uppercase, 1 lowercase, 1 number
    const strongRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$/;
    return strongRegex.test(value);
  },

  alphanumeric: (value: string) => {
    const alphanumericRegex = /^[a-zA-Z0-9]+$/;
    return alphanumericRegex.test(value);
  },

  numeric: (value: string) => {
    return !isNaN(Number(value));
  },

  checked: (value: boolean) => {
    return value === true;
  },
};

export const errorMessages = {
  required: 'This field is required',
  email: 'Please enter a valid email address',
  phone: 'Please enter a valid phone number',
  minLength: (min: number) => `Must be at least ${min} characters`,
  maxLength: (max: number) => `Must be less than ${max} characters`,
  minValue: (min: number) => `Must be at least ${min}`,
  maxValue: (max: number) => `Must be less than ${max}`,
  url: 'Please enter a valid URL',
  strongPassword: 'Password must be at least 8 characters with uppercase, lowercase, and number',
  alphanumeric: 'Only letters and numbers are allowed',
  numeric: 'Please enter a valid number',
  checked: 'You must accept this',
};
