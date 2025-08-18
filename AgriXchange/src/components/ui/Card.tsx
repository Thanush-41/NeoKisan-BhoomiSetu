import React from 'react';
import type { ReactNode } from 'react';

interface CardProps {
  children: ReactNode;
  className?: string;
  hover?: boolean;
  padding?: 'sm' | 'md' | 'lg';
}

export const Card: React.FC<CardProps> = ({
  children,
  className = '',
  hover = false,
  padding = 'md',
}) => {
  const baseClasses = 'bg-white rounded-lg shadow-md transition-shadow duration-200';
  const hoverClasses = hover ? 'hover:shadow-lg cursor-pointer' : '';
  
  const paddingClasses = {
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8',
  };

  const classes = [
    baseClasses,
    hoverClasses,
    paddingClasses[padding],
    className,
  ].join(' ');

  return (
    <div className={classes}>
      {children}
    </div>
  );
};
