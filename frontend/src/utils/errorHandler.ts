/**
 * Global Error Handler Utility
 * Centralized error handling with user-friendly messages
 */

export interface ErrorDetails {
  message: string;
  code?: string;
  status?: number;
  details?: any;
}

export class AppError extends Error {
  code?: string;
  status?: number;
  details?: any;

  constructor(message: string, code?: string, status?: number, details?: any) {
    super(message);
    this.name = 'AppError';
    this.code = code;
    this.status = status;
    this.details = details;
  }
}

/**
 * Parse error from API response or general error
 */
export function parseError(error: any): ErrorDetails {
  // Network error
  if (!navigator.onLine) {
    return {
      message: 'No internet connection. Please check your network and try again.',
      code: 'NETWORK_ERROR',
      status: 0,
    };
  }

  // API error response
  if (error.response) {
    const status = error.response.status;
    const data = error.response.data;

    switch (status) {
      case 400:
        return {
          message: data?.message || 'Invalid request. Please check your input.',
          code: 'BAD_REQUEST',
          status: 400,
          details: data?.details,
        };
      case 401:
        return {
          message: 'Your session has expired. Please login again.',
          code: 'UNAUTHORIZED',
          status: 401,
        };
      case 403:
        return {
          message: 'You do not have permission to perform this action.',
          code: 'FORBIDDEN',
          status: 403,
        };
      case 404:
        return {
          message: 'The requested resource was not found.',
          code: 'NOT_FOUND',
          status: 404,
        };
      case 429:
        return {
          message: 'Too many requests. Please slow down and try again later.',
          code: 'RATE_LIMIT',
          status: 429,
        };
      case 500:
        return {
          message: 'Server error. Our team has been notified. Please try again later.',
          code: 'SERVER_ERROR',
          status: 500,
        };
      case 503:
        return {
          message: 'Service temporarily unavailable. Please try again in a few moments.',
          code: 'SERVICE_UNAVAILABLE',
          status: 503,
        };
      default:
        return {
          message: data?.message || 'An unexpected error occurred. Please try again.',
          code: 'UNKNOWN_ERROR',
          status,
        };
    }
  }

  // Request timeout
  if (error.code === 'ECONNABORTED') {
    return {
      message: 'Request timed out. Please check your connection and try again.',
      code: 'TIMEOUT',
    };
  }

  // Network error (no response)
  if (error.request) {
    return {
      message: 'Unable to reach the server. Please check your internet connection.',
      code: 'NETWORK_ERROR',
    };
  }

  // Generic error
  return {
    message: error.message || 'An unexpected error occurred. Please try again.',
    code: 'GENERIC_ERROR',
  };
}

/**
 * Get user-friendly error message
 */
export function getUserFriendlyMessage(error: any): string {
  return parseError(error).message;
}

/**
 * Check if error is retryable
 */
export function isRetryableError(error: any): boolean {
  const errorDetails = parseError(error);
  const retryableCodes = ['NETWORK_ERROR', 'TIMEOUT', 'SERVICE_UNAVAILABLE', 'RATE_LIMIT'];
  const retryableStatuses = [408, 429, 500, 502, 503, 504];

  return (
    retryableCodes.includes(errorDetails.code || '') ||
    retryableStatuses.includes(errorDetails.status || 0)
  );
}

/**
 * Retry with exponential backoff
 */
export async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  maxRetries: number = 3,
  baseDelay: number = 1000
): Promise<T> {
  let lastError: any;

  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;

      if (attempt < maxRetries - 1 && isRetryableError(error)) {
        const delay = baseDelay * Math.pow(2, attempt);
        await new Promise((resolve) => setTimeout(resolve, delay));
      } else {
        throw error;
      }
    }
  }

  throw lastError;
}
