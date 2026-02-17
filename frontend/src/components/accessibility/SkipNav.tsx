/**
 * Skip Navigation Component
 * Provides keyboard users a way to skip to main content
 * WCAG 2.4.1 - Bypass Blocks (Level A)
 */
import React from 'react';

const SkipNav: React.FC = () => {
  return (
    <div className="skip-nav">
      <a href="#main-content" className="skip-nav-link">
        Skip to main content
      </a>
      <a href="#main-navigation" className="skip-nav-link">
        Skip to navigation
      </a>
    </div>
  );
};

export default SkipNav;