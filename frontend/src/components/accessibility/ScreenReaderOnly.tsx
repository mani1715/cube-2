/**
 * Screen Reader Only Component
 * Hides content visually but keeps it accessible to screen readers
 * WCAG 1.3.1 - Info and Relationships (Level A)
 */
import React from 'react';

interface ScreenReaderOnlyProps {
  children: React.ReactNode;
  as?: keyof JSX.IntrinsicElements;
}

const ScreenReaderOnly: React.FC<ScreenReaderOnlyProps> = ({ 
  children, 
  as: Component = 'span' 
}) => {
  return (
    <Component className="sr-only">
      {children}
    </Component>
  );
};

export default ScreenReaderOnly;