/**
 * Network Status Indicator
 * Shows online/offline status with retry functionality
 */
import { useEffect, useState } from 'react';
import { WifiOff, Wifi, RefreshCw } from 'lucide-react';
import { Button } from './button';
import { cn } from '@/lib/utils';

export const NetworkStatus = () => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [showOffline, setShowOffline] = useState(false);

  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      setShowOffline(false);
    };

    const handleOffline = () => {
      setIsOnline(false);
      setShowOffline(true);
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  const handleRetry = () => {
    window.location.reload();
  };

  if (!showOffline) return null;

  return (
    <div
      className={cn(
        'fixed bottom-4 right-4 z-50 max-w-sm',
        'bg-background border border-border rounded-lg shadow-lg',
        'p-4 animate-in slide-in-from-bottom-5'
      )}
      role="status"
      aria-live="polite"
    >
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0">
          {isOnline ? (
            <Wifi className="w-5 h-5 text-green-500" aria-hidden="true" />
          ) : (
            <WifiOff className="w-5 h-5 text-red-500" aria-hidden="true" />
          )}
        </div>
        <div className="flex-1">
          <h3 className="font-semibold text-sm text-foreground mb-1">
            {isOnline ? 'Back Online' : 'No Internet Connection'}
          </h3>
          <p className="text-xs text-muted-foreground">
            {isOnline
              ? 'Your connection has been restored.'
              : 'Please check your network connection and try again.'}
          </p>
        </div>
        {!isOnline && (
          <Button
            size="sm"
            variant="outline"
            onClick={handleRetry}
            className="ml-2"
            aria-label="Retry connection"
          >
            <RefreshCw className="w-4 h-4" />
          </Button>
        )}
      </div>
    </div>
  );
};
