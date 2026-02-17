import { cn } from '@/lib/utils';
import { Card, CardProps } from '@/components/ui/card';
import { useState } from 'react';

interface AnimatedCardProps extends CardProps {
  hoverable?: boolean;
  children: React.ReactNode;
}

export const AnimatedCard = ({
  hoverable = true,
  children,
  className,
  ...props
}: AnimatedCardProps) => {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <Card
      className={cn(
        'transition-all duration-300 ease-out',
        hoverable && 'cursor-pointer hover:shadow-lg hover:-translate-y-1',
        className
      )}
      onMouseEnter={() => hoverable && setIsHovered(true)}
      onMouseLeave={() => hoverable && setIsHovered(false)}
      {...props}
    >
      {children}
    </Card>
  );
};
