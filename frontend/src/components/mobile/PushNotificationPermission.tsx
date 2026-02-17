import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Bell, BellOff, X } from 'lucide-react';
import { cn } from '@/lib/utils';
import { toast } from 'sonner';

interface PushNotificationPermissionProps {
  /** User ID for subscription management */
  userId?: string;
  /** Show permission prompt automatically */
  autoPrompt?: boolean;
  /** Custom button text */
  buttonText?: string;
}

/**
 * Push Notification Permission Component
 * Handles permission request and subscription management
 * Disabled by default - requires admin to enable feature
 */
export const PushNotificationPermission = ({
  userId,
  autoPrompt = false,
  buttonText = 'Enable Notifications'
}: PushNotificationPermissionProps) => {
  const [permission, setPermission] = useState<NotificationPermission>('default');
  const [isSubscribed, setIsSubscribed] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isFeatureEnabled, setIsFeatureEnabled] = useState(false);
  const [isDismissed, setIsDismissed] = useState(false);

  useEffect(() => {
    // Check if push notifications are supported
    if (!('Notification' in window) || !('serviceWorker' in navigator)) {
      return;
    }

    // Check current permission status
    setPermission(Notification.permission);

    // Check if feature is enabled
    checkFeatureStatus();

    // Check if already subscribed
    checkSubscriptionStatus();
  }, []);

  const checkFeatureStatus = async () => {
    try {
      const response = await fetch('/api/phase15/push/status');
      const data = await response.json();
      setIsFeatureEnabled(data.push_notifications_enabled);
    } catch (error) {
      console.error('Failed to check push notification status:', error);
    }
  };

  const checkSubscriptionStatus = async () => {
    if (!userId) return;

    try {
      const response = await fetch(`/api/phase15/push/subscriptions/${userId}`);
      const data = await response.json();
      setIsSubscribed(data.total > 0);
    } catch (error) {
      console.error('Failed to check subscription status:', error);
    }
  };

  const requestPermission = async () => {
    if (!isFeatureEnabled) {
      toast.error('Push notifications are currently unavailable');
      return;
    }

    if (!('Notification' in window)) {
      toast.error('This browser does not support notifications');
      return;
    }

    setIsLoading(true);

    try {
      const result = await Notification.requestPermission();
      setPermission(result);

      if (result === 'granted') {
        toast.success('Notifications enabled successfully!');
      } else if (result === 'denied') {
        toast.error('Please enable notifications in your browser settings.');
      }
    } catch (error) {
      console.error('Error requesting notification permission:', error);
      toast.error('Failed to enable notifications');
    } finally {
      setIsLoading(false);
    }
  };

  // Don't show if notifications not supported or feature disabled
  if (!('Notification' in window) || !isFeatureEnabled || isDismissed) {
    return null;
  }

  return (
    <div
      className={cn(
        'p-4 rounded-lg border bg-card',
        permission === 'default' && 'border-primary/20 bg-primary/5'
      )}
      role="region"
      aria-label="Push notification settings"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-3 flex-1">
          <div className="mt-1">
            {permission === 'granted' ? (
              <Bell className="w-5 h-5 text-primary" aria-hidden="true" />
            ) : (
              <BellOff className="w-5 h-5 text-muted-foreground" aria-hidden="true" />
            )}
          </div>
          <div className="flex-1">
            <h3 className="font-semibold text-foreground mb-1">
              {permission === 'granted' ? 'Notifications Enabled' : 'Stay Updated'}
            </h3>
            <p className="text-sm text-muted-foreground mb-3">
              {permission === 'granted'
                ? "You'll receive important updates and reminders."
                : 'Get notified about session reminders, event updates, and more.'}
            </p>
            <div className="flex items-center gap-2">
              {permission !== 'granted' && (
                <Button
                  onClick={requestPermission}
                  disabled={isLoading || permission === 'denied'}
                  size="sm"
                  aria-label="Enable push notifications"
                >
                  {isLoading ? 'Enabling...' : buttonText}
                </Button>
              )}
              {permission === 'denied' && (
                <p className="text-xs text-muted-foreground">
                  Notifications blocked. Please enable in browser settings.
                </p>
              )}
            </div>
          </div>
        </div>
        
        {permission === 'default' && (
          <Button
            variant="ghost"
            size="icon"
            className="flex-shrink-0 h-8 w-8"
            onClick={() => setIsDismissed(true)}
            aria-label="Dismiss notification prompt"
          >
            <X className="w-4 h-4" aria-hidden="true" />
          </Button>
        )}
      </div>
    </div>
  );
};
