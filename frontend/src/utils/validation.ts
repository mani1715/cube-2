// Phase 13 - Inline Validation Utilities
import { z } from 'zod';

export interface ValidationResult {
  isValid: boolean;
  error?: string;
}

// Email validation
export const validateEmail = (email: string): ValidationResult => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!email) {
    return { isValid: false, error: 'Email is required' };
  }
  if (!emailRegex.test(email)) {
    return { isValid: false, error: 'Please enter a valid email address' };
  }
  return { isValid: true };
};

// Phone validation
export const validatePhone = (phone: string): ValidationResult => {
  const phoneRegex = /^[\d\s\-\+\(\)]+$/;
  if (!phone) {
    return { isValid: false, error: 'Phone number is required' };
  }
  if (phone.replace(/[\s\-\+\(\)]/g, '').length < 10) {
    return { isValid: false, error: 'Phone number must be at least 10 digits' };
  }
  if (!phoneRegex.test(phone)) {
    return { isValid: false, error: 'Please enter a valid phone number' };
  }
  return { isValid: true };
};

// Name validation
export const validateName = (name: string, fieldName: string = 'Name'): ValidationResult => {
  if (!name || name.trim().length === 0) {
    return { isValid: false, error: `${fieldName} is required` };
  }
  if (name.trim().length < 2) {
    return { isValid: false, error: `${fieldName} must be at least 2 characters` };
  }
  if (name.trim().length > 100) {
    return { isValid: false, error: `${fieldName} must be less than 100 characters` };
  }
  return { isValid: true };
};

// Password validation
export const validatePassword = (password: string): ValidationResult => {
  if (!password) {
    return { isValid: false, error: 'Password is required' };
  }
  if (password.length < 8) {
    return { isValid: false, error: 'Password must be at least 8 characters' };
  }
  if (!/[A-Z]/.test(password)) {
    return { isValid: false, error: 'Password must contain at least one uppercase letter' };
  }
  if (!/[a-z]/.test(password)) {
    return { isValid: false, error: 'Password must contain at least one lowercase letter' };
  }
  if (!/[0-9]/.test(password)) {
    return { isValid: false, error: 'Password must contain at least one number' };
  }
  return { isValid: true };
};

// Date validation
export const validateDate = (date: string): ValidationResult => {
  if (!date) {
    return { isValid: false, error: 'Date is required' };
  }
  const dateObj = new Date(date);
  if (isNaN(dateObj.getTime())) {
    return { isValid: false, error: 'Please enter a valid date' };
  }
  return { isValid: true };
};

// Future date validation
export const validateFutureDate = (date: string): ValidationResult => {
  const validation = validateDate(date);
  if (!validation.isValid) return validation;

  const dateObj = new Date(date);
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  if (dateObj < today) {
    return { isValid: false, error: 'Date must be in the future' };
  }
  return { isValid: true };
};

// URL validation
export const validateUrl = (url: string): ValidationResult => {
  if (!url) {
    return { isValid: false, error: 'URL is required' };
  }
  try {
    new URL(url);
    return { isValid: true };
  } catch {
    return { isValid: false, error: 'Please enter a valid URL' };
  }
};

// Text area validation
export const validateTextArea = (
  text: string,
  minLength: number = 10,
  maxLength: number = 1000,
  fieldName: string = 'Message'
): ValidationResult => {
  if (!text || text.trim().length === 0) {
    return { isValid: false, error: `${fieldName} is required` };
  }
  if (text.trim().length < minLength) {
    return { isValid: false, error: `${fieldName} must be at least ${minLength} characters` };
  }
  if (text.trim().length > maxLength) {
    return { isValid: false, error: `${fieldName} must be less than ${maxLength} characters` };
  }
  return { isValid: true };
};

// Generic required field validation
export const validateRequired = (value: any, fieldName: string = 'Field'): ValidationResult => {
  if (value === null || value === undefined || value === '' || (typeof value === 'string' && value.trim() === '')) {
    return { isValid: false, error: `${fieldName} is required` };
  }
  return { isValid: true };
};

// Real-time validation hook helper
export const getValidationError = (fieldName: string, value: any, validationType: string): string | undefined => {
  let result: ValidationResult;

  switch (validationType) {
    case 'email':
      result = validateEmail(value);
      break;
    case 'phone':
      result = validatePhone(value);
      break;
    case 'name':
      result = validateName(value, fieldName);
      break;
    case 'password':
      result = validatePassword(value);
      break;
    case 'date':
      result = validateDate(value);
      break;
    case 'futureDate':
      result = validateFutureDate(value);
      break;
    case 'url':
      result = validateUrl(value);
      break;
    case 'required':
      result = validateRequired(value, fieldName);
      break;
    default:
      result = { isValid: true };
  }

  return result.isValid ? undefined : result.error;
};