import React from 'react';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  glow?: boolean;
}

export const Card: React.FC<CardProps> = ({ children, className = '', glow = false }) => {
  return (
    <div
      className={`bg-[#0a0a0a] border border-[#1a1a1a] rounded-lg p-4 ${
        glow ? 'glow-green border-green-500/30' : ''
      } ${className}`}
    >
      {children}
    </div>
  );
};

interface StatCardProps {
  title: string;
  value: string | number;
  icon?: React.ReactNode;
  accentColor?: 'green' | 'yellow' | 'red' | 'blue';
}

const accentColors = {
  green: 'border-l-green-500',
  yellow: 'border-l-yellow-500',
  red: 'border-l-red-500',
  blue: 'border-l-blue-500',
};

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  icon,
  accentColor = 'green',
}) => {
  return (
    <div
      className={`bg-[#0a0a0a] border border-[#1a1a1a] rounded-lg p-4 border-l-4 ${accentColors[accentColor]}`}
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-gray-400 text-sm">{title}</p>
          <p className="text-2xl font-mono font-bold text-white mt-1">{value}</p>
        </div>
        {icon && <div className="text-green-500">{icon}</div>}
      </div>
    </div>
  );
};
