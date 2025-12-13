import React from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
}

const variantStyles = {
  primary: 'bg-green-500 hover:bg-green-600 text-black font-semibold glow-green',
  secondary: 'bg-[#1a1a1a] hover:bg-[#2a2a2a] text-white border border-[#333]',
  outline: 'bg-transparent border-2 border-green-500 text-green-500 hover:bg-green-500/10',
  ghost: 'bg-transparent hover:bg-[#1a1a1a] text-gray-300',
};

const sizeStyles = {
  sm: 'px-3 py-1.5 text-sm',
  md: 'px-4 py-2 text-sm',
  lg: 'px-6 py-3 text-base',
};

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  loading = false,
  disabled,
  className = '',
  children,
  ...props
}) => {
  return (
    <button
      className={`rounded-lg font-medium transition-all duration-200 flex items-center justify-center gap-2 ${
        variantStyles[variant]
      } ${sizeStyles[size]} ${
        disabled || loading ? 'opacity-50 cursor-not-allowed' : ''
      } ${className}`}
      disabled={disabled || loading}
      {...props}
    >
      {loading && (
        <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
            fill="none"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          />
        </svg>
      )}
      {children}
    </button>
  );
};
