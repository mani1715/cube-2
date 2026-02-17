// Phase 13 - Skeleton Loaders for better loading states
import React from 'react';
import { cn } from '@/lib/utils';

interface SkeletonProps {
  className?: string;
  variant?: 'text' | 'circular' | 'rectangular' | 'rounded';
  width?: string | number;
  height?: string | number;
  animation?: 'pulse' | 'wave' | 'none';
}

export const Skeleton: React.FC<SkeletonProps> = ({
  className,
  variant = 'rectangular',
  width,
  height,
  animation = 'pulse',
}) => {
  const variantClasses = {
    text: 'h-4 rounded',
    circular: 'rounded-full',
    rectangular: 'rounded-none',
    rounded: 'rounded-lg',
  };

  const animationClasses = {
    pulse: 'animate-pulse',
    wave: 'animate-shimmer',
    none: '',
  };

  return (
    <div
      className={cn(
        'bg-gray-200 dark:bg-gray-700',
        variantClasses[variant],
        animationClasses[animation],
        className
      )}
      style={{
        width: width || '100%',
        height: height || (variant === 'text' ? '1rem' : '100%'),
      }}
      aria-hidden="true"
      data-testid="skeleton-loader"
    />
  );
};

// Card Skeleton
export const CardSkeleton: React.FC<{ className?: string }> = ({ className }) => (
  <div className={cn('p-4 border rounded-lg space-y-3', className)} data-testid="card-skeleton">
    <Skeleton variant="rounded" height={150} />
    <Skeleton variant="text" width="80%" />
    <Skeleton variant="text" width="60%" />
    <div className="flex gap-2">
      <Skeleton variant="rounded" height={32} width={80} />
      <Skeleton variant="rounded" height={32} width={80} />
    </div>
  </div>
);

// List Item Skeleton
export const ListItemSkeleton: React.FC<{ className?: string }> = ({ className }) => (
  <div className={cn('flex items-center gap-3 p-3', className)} data-testid="list-item-skeleton">
    <Skeleton variant="circular" width={40} height={40} />
    <div className="flex-1 space-y-2">
      <Skeleton variant="text" width="70%" />
      <Skeleton variant="text" width="40%" />
    </div>
  </div>
);

// Table Row Skeleton
export const TableRowSkeleton: React.FC<{ columns?: number; className?: string }> = ({ 
  columns = 4, 
  className 
}) => (
  <tr className={className} data-testid="table-row-skeleton">
    {Array.from({ length: columns }).map((_, i) => (
      <td key={i} className="p-3">
        <Skeleton variant="text" />
      </td>
    ))}
  </tr>
);

// Blog Post Skeleton
export const BlogPostSkeleton: React.FC<{ className?: string }> = ({ className }) => (
  <article className={cn('space-y-4', className)} data-testid="blog-post-skeleton">
    <Skeleton variant="rounded" height={200} />
    <Skeleton variant="text" width="90%" height={24} />
    <Skeleton variant="text" width="70%" />
    <div className="space-y-2">
      <Skeleton variant="text" />
      <Skeleton variant="text" />
      <Skeleton variant="text" width="85%" />
    </div>
    <div className="flex items-center gap-3">
      <Skeleton variant="circular" width={32} height={32} />
      <Skeleton variant="text" width={120} />
    </div>
  </article>
);

// Event Card Skeleton
export const EventCardSkeleton: React.FC<{ className?: string }> = ({ className }) => (
  <div className={cn('border rounded-lg p-4 space-y-3', className)} data-testid="event-card-skeleton">
    <div className="flex justify-between">
      <Skeleton variant="text" width={100} />
      <Skeleton variant="rounded" width={60} height={24} />
    </div>
    <Skeleton variant="text" width="85%" height={20} />
    <Skeleton variant="text" width="95%" />
    <Skeleton variant="text" width="75%" />
    <div className="flex gap-2 pt-2">
      <Skeleton variant="rounded" width={80} height={36} />
      <Skeleton variant="rounded" width={80} height={36} />
    </div>
  </div>
);

export default Skeleton;