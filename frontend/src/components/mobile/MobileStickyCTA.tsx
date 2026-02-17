import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Calendar, Users, X } from 'lucide-react';
import { cn } from '@/lib/utils';

interface MobileStickyCTAProps {
  /** Show the CTA after scrolling X pixels */
  showAfterScroll?: number;
  /** Auto-hide the CTA (can be dismissed) */
  dismissable?: boolean;
}

/**
 * Mobile Sticky CTA - Bottom floating action buttons for mobile
 * Only shows on mobile devices (< 768px)
 */
export const MobileStickyCTA = ({ 
  showAfterScroll = 300,
  dismissable = true 
}: MobileStickyCTAProps) => {
  const [isVisible, setIsVisible] = useState(false);
  const [isDismissed, setIsDismissed] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      if (window.scrollY > showAfterScroll && !isDismissed) {
        setIsVisible(true);
      } else if (window.scrollY <= showAfterScroll) {
        setIsVisible(false);
      }
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [showAfterScroll, isDismissed]);

  const handleDismiss = () => {
    setIsDismissed(true);
    setIsVisible(false);
  };

  if (isDismissed) return null;

  return (
    <div
      className={cn(
        'fixed bottom-0 left-0 right-0 z-40 md:hidden',
        'transition-transform duration-300 ease-in-out',
        isVisible ? 'translate-y-0' : 'translate-y-full'
      )}
      role="complementary"
      aria-label="Quick action buttons"
    >
      <div className="bg-background/95 backdrop-blur-xl border-t border-border shadow-elevated">
        <div className="container mx-auto px-4 py-3">
          <div className="flex items-center gap-2">
            {/* Book Session CTA */}
            <Link to="/services" className="flex-1">
              <Button 
                className="w-full h-12 text-base font-medium shadow-soft"
                variant="default"
                size="lg"
                aria-label="Book a therapy session"
              >
                <Calendar className="w-5 h-5 mr-2" aria-hidden="true" />
                Book Session
              </Button>
            </Link>

            {/* Events CTA */}
            <Link to="/events" className="flex-1">
              <Button 
                className="w-full h-12 text-base font-medium shadow-soft"
                variant="outline"
                size="lg"
                aria-label="View upcoming events"
              >
                <Users className="w-5 h-5 mr-2" aria-hidden="true" />
                Events
              </Button>
            </Link>

            {/* Dismiss Button */}
            {dismissable && (
              <Button
                variant="ghost"
                size="icon"
                className="h-12 w-12 flex-shrink-0"
                onClick={handleDismiss}
                aria-label="Dismiss quick actions"
              >
                <X className="w-5 h-5" aria-hidden="true" />
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
