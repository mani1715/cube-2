import { useState, useEffect } from "react";
import { cn } from "@/lib/utils";

interface OptimizedImageProps {
  src: string;
  alt: string;
  className?: string;
  width?: number;
  height?: number;
  priority?: boolean; // If true, don't lazy load
  objectFit?: "cover" | "contain" | "fill" | "none" | "scale-down";
}

/**
 * OptimizedImage Component
 * Phase 13.1 - Performance Optimization
 * 
 * Features:
 * - Lazy loading by default (can be disabled with priority prop)
 * - Shows blur placeholder while loading
 * - Responsive image loading
 * - Error handling with fallback
 */
const OptimizedImage = ({
  src,
  alt,
  className = "",
  width,
  height,
  priority = false,
  objectFit = "cover",
}: OptimizedImageProps) => {
  const [isLoaded, setIsLoaded] = useState(false);
  const [hasError, setHasError] = useState(false);
  const [imageSrc, setImageSrc] = useState(src);

  useEffect(() => {
    // Reset states when src changes
    setIsLoaded(false);
    setHasError(false);
    setImageSrc(src);
  }, [src]);

  const handleLoad = () => {
    setIsLoaded(true);
  };

  const handleError = () => {
    setHasError(true);
    // Fallback to a placeholder image
    setImageSrc("/placeholder-image.jpg");
  };

  const imageStyle: React.CSSProperties = {
    objectFit,
    width: width ? `${width}px` : "100%",
    height: height ? `${height}px` : "100%",
  };

  return (
    <div className={cn("relative overflow-hidden bg-muted", className)}>
      {/* Blur placeholder - shown while loading */}
      {!isLoaded && !hasError && (
        <div className="absolute inset-0 animate-pulse bg-muted" />
      )}

      {/* Actual image */}
      <img
        src={imageSrc}
        alt={alt}
        loading={priority ? "eager" : "lazy"}
        onLoad={handleLoad}
        onError={handleError}
        style={imageStyle}
        className={cn(
          "transition-opacity duration-300",
          isLoaded ? "opacity-100" : "opacity-0",
          hasError && "opacity-50"
        )}
      />

      {/* Error state indicator */}
      {hasError && (
        <div className="absolute inset-0 flex items-center justify-center text-xs text-muted-foreground">
          Failed to load image
        </div>
      )}
    </div>
  );
};

export default OptimizedImage;
