import { useEffect, useRef, useState, ReactNode, memo } from "react";

interface ScrollRevealProps {
  children: ReactNode;
  className?: string;
  delay?: number;
  threshold?: number;
}

export const ScrollReveal = memo(({ 
  children, 
  className = "", 
  delay = 0,
  threshold = 0.1 
}: ScrollRevealProps) => {
  const [isRevealed, setIsRevealed] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Check for reduced motion preference
    const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    
    if (prefersReducedMotion) {
      setIsRevealed(true);
      return;
    }

    const element = ref.current;
    if (!element) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          // Use requestAnimationFrame for smoother animation triggering
          if (delay > 0) {
            setTimeout(() => {
              requestAnimationFrame(() => setIsRevealed(true));
            }, delay);
          } else {
            requestAnimationFrame(() => setIsRevealed(true));
          }
          observer.disconnect();
        }
      },
      {
        threshold,
        rootMargin: "0px 0px -40px 0px",
      }
    );

    observer.observe(element);

    return () => observer.disconnect();
  }, [delay, threshold]);

  return (
    <div
      ref={ref}
      className={`scroll-reveal ${isRevealed ? "revealed" : ""} ${className}`}
    >
      {children}
    </div>
  );
});

ScrollReveal.displayName = "ScrollReveal";
