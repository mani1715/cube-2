/**
 * useAnnouncer Hook
 * Announces messages to screen readers dynamically
 * WCAG 4.1.3 - Status Messages (Level AA)
 */
import { useState, useCallback, useEffect } from 'react';

interface AnnouncerOptions {
  politeness?: 'polite' | 'assertive';
  clearDelay?: number;
}

export const useAnnouncer = (options: AnnouncerOptions = {}) => {
  const { politeness = 'polite', clearDelay = 5000 } = options;
  const [message, setMessage] = useState<string>('');

  const announce = useCallback((newMessage: string) => {
    setMessage(newMessage);
  }, []);

  const clear = useCallback(() => {
    setMessage('');
  }, []);

  useEffect(() => {
    if (!message) return;

    const timer = setTimeout(() => {
      clear();
    }, clearDelay);

    return () => clearTimeout(timer);
  }, [message, clearDelay, clear]);

  return {
    message,
    politeness,
    announce,
    clear,
  };
};