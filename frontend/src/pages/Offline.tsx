import React from 'react';
import { WifiOff, RefreshCw, Home } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Link } from 'react-router-dom';

const Offline: React.FC = () => {
  const handleRefresh = () => {
    window.location.reload();
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-br from-purple-50 to-blue-50 dark:from-gray-900 dark:to-gray-800">
      <Card className="max-w-md w-full p-8 text-center">
        <div className="mb-6 flex justify-center">
          <div className="p-4 bg-red-100 dark:bg-red-900/20 rounded-full">
            <WifiOff className="w-16 h-16 text-red-600 dark:text-red-400" />
          </div>
        </div>

        <h1 className="text-3xl font-bold mb-3">You're Offline</h1>
        
        <p className="text-muted-foreground mb-6">
          It looks like you've lost your internet connection. Don't worry, some features
          of A-Cube are still available offline.
        </p>

        <div className="space-y-3 mb-6">
          <div className="text-left p-4 bg-muted/50 rounded-lg">
            <h3 className="font-semibold mb-2 text-sm">Available Offline:</h3>
            <ul className="text-sm space-y-1 text-muted-foreground">
              <li>• Browse previously viewed content</li>
              <li>• Access cached pages</li>
              <li>• Read saved articles</li>
            </ul>
          </div>

          <div className="text-left p-4 bg-muted/50 rounded-lg">
            <h3 className="font-semibold mb-2 text-sm">Requires Connection:</h3>
            <ul className="text-sm space-y-1 text-muted-foreground">
              <li>• Booking new sessions</li>
              <li>• Registering for events</li>
              <li>• Submitting forms</li>
            </ul>
          </div>
        </div>

        <div className="flex flex-col sm:flex-row gap-3">
          <Button
            onClick={handleRefresh}
            className="flex-1 flex items-center justify-center gap-2"
          >
            <RefreshCw className="w-4 h-4" />
            Try Again
          </Button>
          <Button
            asChild
            variant="outline"
            className="flex-1 flex items-center justify-center gap-2"
          >
            <Link to="/">
              <Home className="w-4 h-4" />
              Go Home
            </Link>
          </Button>
        </div>

        <p className="text-xs text-muted-foreground mt-6">
          Your connection will be restored automatically when you're back online.
        </p>
      </Card>
    </div>
  );
};

export default Offline;