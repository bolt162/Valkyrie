import React from 'react';

interface BadgeProps {
  variant: 'success' | 'warning' | 'danger' | 'info' | 'critical';
  children: React.ReactNode;
  className?: string;
}

const variantStyles = {
  success: 'bg-green-500/20 text-green-400 border-green-500/50',
  warning: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/50',
  danger: 'bg-red-500/20 text-red-400 border-red-500/50',
  critical: 'bg-red-600/30 text-red-300 border-red-500/70',
  info: 'bg-blue-500/20 text-blue-400 border-blue-500/50',
};

export const Badge: React.FC<BadgeProps> = ({ variant, children, className = '' }) => {
  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-mono border ${variantStyles[variant]} ${className}`}
    >
      {children}
    </span>
  );
};

export const getSeverityVariant = (severity: string): BadgeProps['variant'] => {
  switch (severity?.toLowerCase()) {
    case 'critical':
      return 'critical';
    case 'high':
      return 'danger';
    case 'medium':
      return 'warning';
    case 'low':
      return 'success';
    default:
      return 'info';
  }
};

export const getRiskVariant = (risk: string): BadgeProps['variant'] => {
  switch (risk?.toLowerCase()) {
    case 'high':
      return 'danger';
    case 'medium':
      return 'warning';
    case 'low':
      return 'success';
    default:
      return 'info';
  }
};

export const getStatusVariant = (status: string): BadgeProps['variant'] => {
  switch (status?.toLowerCase()) {
    case 'completed':
      return 'success';
    case 'running':
      return 'info';
    case 'failed':
      return 'danger';
    default:
      return 'info';
  }
};
