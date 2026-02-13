// Phase 15 - Enhanced PWA Install Prompt with A2HS improvements
import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Download, X, Smartphone, Monitor } from 'lucide-react';
import { cn } from '@/lib/utils';

interface BeforeInstallPromptEvent extends Event {
  prompt: () => Promise<void>;
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>;
}

const EnhancedPWAInstallPrompt: React.FC = () => {
  const [deferredPrompt, setDeferredPrompt] = useState<BeforeInstallPromptEvent | null>(null);
  const [showPrompt, setShowPrompt] = useState(false);
  const [isInstalling, setIsInstalling] = useState(false);
  const [isStandalone, setIsStandalone] = useState(false);
  const [platform, setPlatform] = useState<'ios' | 'android' | 'desktop'>('desktop');

  useEffect(() => {
    // Check if already installed
    const standalone = window.matchMedia('(display-mode: standalone)').matches;
    setIsStandalone(standalone);

    // Detect platform
    const userAgent = window.navigator.userAgent.toLowerCase();
    const isIOS = /iphone|ipad|ipod/.test(userAgent);
    const isAndroid = /android/.test(userAgent);

    if (isIOS) {
      setPlatform('ios');
    } else if (isAndroid) {
      setPlatform('android');
    } else {
      setPlatform('desktop');
    }

    // Check if user has dismissed before
    const dismissed = localStorage.getItem('pwa-install-dismissed');
    const dismissedTime = dismissed ? parseInt(dismissed) : 0;
    const daysSinceDismissed = (Date.now() - dismissedTime) / (1000 * 60 * 60 * 24);

    // Show prompt again after 7 days
    if (dismissed && daysSinceDismissed < 7) {
      return;
    }

    // Listen for the beforeinstallprompt event
    const handleBeforeInstallPrompt = (e: Event) => {
      e.preventDefault();
      setDeferredPrompt(e as BeforeInstallPromptEvent);
      
      // Show prompt after 30 seconds or on scroll
      const timer = setTimeout(() => setShowPrompt(true), 30000);
      
      const handleScroll = () => {
        if (window.scrollY > 500) {
          setShowPrompt(true);
          window.removeEventListener('scroll', handleScroll);
          clearTimeout(timer);
        }
      };
      
      window.addEventListener('scroll', handleScroll);
      
      return () => {
        clearTimeout(timer);
        window.removeEventListener('scroll', handleScroll);
      };
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    };
  }, []);

  const handleInstallClick = async () => {
    if (!deferredPrompt) {
      // For iOS, show instructions
      if (platform === 'ios') {
        setShowPrompt(true);
      }
      return;
    }

    setIsInstalling(true);

    try {
      await deferredPrompt.prompt();
      const { outcome } = await deferredPrompt.userChoice;

      if (outcome === 'accepted') {
        console.log('PWA installed successfully');
        setShowPrompt(false);
        localStorage.setItem('pwa-install-accepted', Date.now().toString());
      } else {
        console.log('PWA installation dismissed');
        handleDismiss();
      }
    } catch (error) {
      console.error('Error installing PWA:', error);
    } finally {
      setIsInstalling(false);
      setDeferredPrompt(null);
    }
  };

  const handleDismiss = () => {
    setShowPrompt(false);
    localStorage.setItem('pwa-install-dismissed', Date.now().toString());
  };

  // Don't show if already installed
  if (isStandalone) {
    return null;
  }

  // Don't show if no prompt and not iOS
  if (!showPrompt && platform !== 'ios') {
    return null;
  }

  // iOS-specific instructions
  if (platform === 'ios' && showPrompt) {
    return (
      <div className="fixed bottom-0 left-0 right-0 z-50 p-4 animate-slide-up" data-testid="pwa-install-prompt">
        <Card className="shadow-lg border-2">
          <CardHeader className="relative pb-3">
            <Button
              variant="ghost"
              size="icon"
              className="absolute right-2 top-2"
              onClick={handleDismiss}
              aria-label="Dismiss"
              data-testid="dismiss-button"
            >
              <X className="h-4 w-4" />
            </Button>
            <CardTitle className="flex items-center gap-2 text-lg">
              <Smartphone className="h-5 w-5" />
              Install A-Cube App
            </CardTitle>
            <CardDescription>
              Add to your home screen for quick access
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <p>To install this app on your iPhone:</p>
            <ol className="list-decimal list-inside space-y-1 text-muted-foreground">
              <li>Tap the Share button (box with arrow)</li>
              <li>Scroll down and tap "Add to Home Screen"</li>
              <li>Tap "Add" in the top right corner</li>
            </ol>
          </CardContent>
          <CardFooter>
            <Button variant="outline" onClick={handleDismiss} className="w-full">
              Got it
            </Button>
          </CardFooter>
        </Card>
      </div>
    );
  }

  // Android/Desktop install prompt
  if (showPrompt && deferredPrompt) {
    return (
      <div className="fixed bottom-0 left-0 right-0 z-50 p-4 animate-slide-up" data-testid="pwa-install-prompt">
        <Card className="shadow-lg border-2">
          <CardHeader className="relative pb-3">
            <Button
              variant="ghost"
              size="icon"
              className="absolute right-2 top-2"
              onClick={handleDismiss}
              aria-label="Dismiss"
              data-testid="dismiss-button"
            >
              <X className="h-4 w-4" />
            </Button>
            <CardTitle className="flex items-center gap-2 text-lg">
              {platform === 'android' ? (
                <Smartphone className="h-5 w-5" />
              ) : (
                <Monitor className="h-5 w-5" />
              )}
              Install A-Cube App
            </CardTitle>
            <CardDescription>
              Get instant access and work offline
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li className="flex items-center gap-2">
                <span className="text-primary">✓</span>
                Fast and reliable performance
              </li>
              <li className="flex items-center gap-2">
                <span className="text-primary">✓</span>
                Works offline with cached content
              </li>
              <li className="flex items-center gap-2">
                <span className="text-primary">✓</span>
                Quick access from home screen
              </li>
              <li className="flex items-center gap-2">
                <span className="text-primary">✓</span>
                Receive important notifications
              </li>
            </ul>
          </CardContent>
          <CardFooter className="flex gap-2">
            <Button
              variant="outline"
              onClick={handleDismiss}
              className="flex-1"
              data-testid="maybe-later-button"
            >
              Maybe Later
            </Button>
            <Button
              onClick={handleInstallClick}
              disabled={isInstalling}
              className="flex-1"
              data-testid="install-button"
            >
              <Download className="mr-2 h-4 w-4" />
              {isInstalling ? 'Installing...' : 'Install'}
            </Button>
          </CardFooter>
        </Card>
      </div>
    );
  }

  return null;
};

export default EnhancedPWAInstallPrompt;