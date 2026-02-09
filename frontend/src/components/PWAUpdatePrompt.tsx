import React, { useEffect, useState } from 'react';
import { RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { useRegisterSW } from 'virtual:pwa-register/react';

const PWAUpdatePrompt: React.FC = () => {
  const [showUpdatePrompt, setShowUpdatePrompt] = useState(false);

  const {
    offlineReady: [offlineReady, setOfflineReady],
    needRefresh: [needRefresh, setNeedRefresh],
    updateServiceWorker,
  } = useRegisterSW({
    onRegistered(r) {
      console.log('SW Registered:', r);
    },
    onRegisterError(error) {
      console.log('SW registration error', error);
    },
  });

  useEffect(() => {
    if (needRefresh) {
      setShowUpdatePrompt(true);
    }
  }, [needRefresh]);

  const handleUpdate = async () => {
    await updateServiceWorker(true);
    setShowUpdatePrompt(false);
    setNeedRefresh(false);
  };

  const handleDismiss = () => {
    setShowUpdatePrompt(false);
    setNeedRefresh(false);
  };

  if (!showUpdatePrompt && !offlineReady) return null;

  return (
    <div className="fixed top-4 right-4 z-50 max-w-md animate-in slide-in-from-top-5">
      {offlineReady && (
        <Card className="p-4 shadow-lg border-2 border-green-500/20 bg-green-50 dark:bg-green-950">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-green-500/10 rounded-lg">
              <RefreshCw className="w-5 h-5 text-green-600 dark:text-green-400" />
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-green-900 dark:text-green-100">
                App ready to work offline
              </h3>
              <p className="text-sm text-green-700 dark:text-green-300">
                You can now use the app without an internet connection
              </p>
            </div>
            <Button
              onClick={() => setOfflineReady(false)}
              size="sm"
              variant="ghost"
              className="text-green-600 hover:text-green-700"
            >
              Close
            </Button>
          </div>
        </Card>
      )}

      {showUpdatePrompt && (
        <Card className="p-4 shadow-lg border-2 border-primary/20">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-primary/10 rounded-lg">
              <RefreshCw className="w-5 h-5 text-primary" />
            </div>
            <div className="flex-1">
              <h3 className="font-semibold">New version available</h3>
              <p className="text-sm text-muted-foreground">
                Click reload to update to the latest version
              </p>
            </div>
            <div className="flex gap-2">
              <Button onClick={handleUpdate} size="sm">
                Reload
              </Button>
              <Button onClick={handleDismiss} size="sm" variant="outline">
                Later
              </Button>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
};

export default PWAUpdatePrompt;