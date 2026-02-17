// Phase 15 - Push Notification Frontend Integration
import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Bell, BellOff, Settings } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

const API_BASE_URL = import.meta.env.VITE_REACT_APP_BACKEND_URL || '';

interface NotificationPreferences {
  push_enabled: boolean;
  notifications: {
    session_reminders: boolean;
    event_updates: boolean;
    blog_updates: boolean;
    promotional: boolean;
    system_alerts: boolean;
  };
  quiet_hours: {
    enabled: boolean;
    start: string;
    end: string;
  };
}

interface PushNotificationManagerProps {
  userId?: string;
}

export const PushNotificationManager: React.FC<PushNotificationManagerProps> = ({ userId }) => {
  const [isSupported, setIsSupported] = useState(false);
  const [isSubscribed, setIsSubscribed] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [preferences, setPreferences] = useState<NotificationPreferences | null>(null);
  const { toast } = useToast();

  useEffect(() => {
    checkPushSupport();
    if (userId) {
      loadPreferences();
    }
  }, [userId]);

  const checkPushSupport = () => {
    const supported = 'serviceWorker' in navigator && 'PushManager' in window;
    setIsSupported(supported);
    
    if (supported) {
      checkSubscriptionStatus();
    }
  };

  const checkSubscriptionStatus = async () => {
    try {
      const registration = await navigator.serviceWorker.ready;
      const subscription = await registration.pushManager.getSubscription();
      setIsSubscribed(!!subscription);
    } catch (error) {
      console.error('Error checking subscription:', error);
    }
  };

  const loadPreferences = async () => {
    if (!userId) return;

    try {
      const response = await fetch(`${API_BASE_URL}/api/phase15/push/preferences/${userId}`);
      if (response.ok) {
        const data = await response.json();
        setPreferences(data.preferences);
      }
    } catch (error) {
      console.error('Error loading preferences:', error);
    }
  };

  const requestNotificationPermission = async () => {
    if (!('Notification' in window)) {
      toast({
        title: 'Not Supported',
        description: 'Push notifications are not supported in your browser',
        variant: 'destructive',
      });
      return false;
    }

    const permission = await Notification.requestPermission();
    return permission === 'granted';
  };

  const subscribeToPush = async () => {
    if (!userId) {
      toast({
        title: 'Authentication Required',
        description: 'Please log in to enable push notifications',
        variant: 'destructive',
      });
      return;
    }

    setIsLoading(true);

    try {
      // Request notification permission
      const permissionGranted = await requestNotificationPermission();
      if (!permissionGranted) {
        toast({
          title: 'Permission Denied',
          description: 'Please allow notifications in your browser settings',
          variant: 'destructive',
        });
        setIsLoading(false);
        return;
      }

      // Get service worker registration
      const registration = await navigator.serviceWorker.ready;

      // Subscribe to push notifications
      const subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(
          'BEl62iUYgUivxIkv69yViEuiBIa-Ib37J8xQmrEcxaC8zAL3-VPxkXqAKkOZ1FYxhDbqGe2fW3UjJ6fLGI6P6Vk'
        ),
      });

      // Send subscription to backend
      const response = await fetch(`${API_BASE_URL}/api/phase15/push/subscribe`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          endpoint: subscription.endpoint,
          keys: {
            p256dh: arrayBufferToBase64(subscription.getKey('p256dh')!),
            auth: arrayBufferToBase64(subscription.getKey('auth')!),
          },
          platform: 'web',
          browser: navigator.userAgent,
        }),
      });

      if (response.ok) {
        setIsSubscribed(true);
        toast({
          title: 'Success',
          description: 'Push notifications enabled successfully',
        });
      } else {
        throw new Error('Failed to subscribe');
      }
    } catch (error) {
      console.error('Error subscribing to push:', error);
      toast({
        title: 'Error',
        description: 'Failed to enable push notifications',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const unsubscribeFromPush = async () => {
    if (!userId) return;

    setIsLoading(true);

    try {
      const registration = await navigator.serviceWorker.ready;
      const subscription = await registration.pushManager.getSubscription();

      if (subscription) {
        await subscription.unsubscribe();

        // Remove subscription from backend
        await fetch(
          `${API_BASE_URL}/api/phase15/push/unsubscribe?user_id=${userId}&endpoint=${encodeURIComponent(subscription.endpoint)}`,
          { method: 'DELETE' }
        );

        setIsSubscribed(false);
        toast({
          title: 'Success',
          description: 'Push notifications disabled',
        });
      }
    } catch (error) {
      console.error('Error unsubscribing from push:', error);
      toast({
        title: 'Error',
        description: 'Failed to disable push notifications',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const updatePreferences = async (newPreferences: Partial<NotificationPreferences>) => {
    if (!userId) return;

    try {
      const response = await fetch(`${API_BASE_URL}/api/phase15/push/preferences/${userId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newPreferences),
      });

      if (response.ok) {
        const data = await response.json();
        setPreferences(data.preferences);
        toast({
          title: 'Success',
          description: 'Notification preferences updated',
        });
      }
    } catch (error) {
      console.error('Error updating preferences:', error);
      toast({
        title: 'Error',
        description: 'Failed to update preferences',
        variant: 'destructive',
      });
    }
  };

  if (!isSupported) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BellOff className="h-5 w-5" />
            Push Notifications Not Available
          </CardTitle>
          <CardDescription>
            Your browser doesn't support push notifications
          </CardDescription>
        </CardHeader>
      </Card>
    );
  }

  return (
    <Card data-testid="push-notification-manager">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Bell className="h-5 w-5" />
          Push Notifications
        </CardTitle>
        <CardDescription>
          Manage your notification preferences
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <Label htmlFor="push-toggle" className="font-medium">
              Enable Push Notifications
            </Label>
            <p className="text-sm text-muted-foreground">
              Receive important updates and reminders
            </p>
          </div>
          <Switch
            id="push-toggle"
            checked={isSubscribed}
            onCheckedChange={(checked) => {
              if (checked) {
                subscribeToPush();
              } else {
                unsubscribeFromPush();
              }
            }}
            disabled={isLoading}
            data-testid="push-toggle"
          />
        </div>

        {isSubscribed && preferences && (
          <div className="space-y-3 pt-4 border-t">
            <h4 className="font-medium flex items-center gap-2">
              <Settings className="h-4 w-4" />
              Notification Types
            </h4>
            
            {Object.entries(preferences.notifications).map(([key, value]) => (
              <div key={key} className="flex items-center justify-between">
                <Label htmlFor={key} className="font-normal cursor-pointer">
                  {key.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase())}
                </Label>
                <Switch
                  id={key}
                  checked={value}
                  onCheckedChange={(checked) => {
                    updatePreferences({
                      notifications: {
                        ...preferences.notifications,
                        [key]: checked,
                      },
                    });
                  }}
                  data-testid={`notification-type-${key}`}
                />
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

// Helper functions
function urlBase64ToUint8Array(base64String: string): Uint8Array {
  const padding = '='.repeat((4 - (base64String.length % 4)) % 4);
  const base64 = (base64String + padding).replace(/\-/g, '+').replace(/_/g, '/');
  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);
  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}

function arrayBufferToBase64(buffer: ArrayBuffer): string {
  const bytes = new Uint8Array(buffer);
  let binary = '';
  for (let i = 0; i < bytes.byteLength; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return window.btoa(binary);
}

export default PushNotificationManager;