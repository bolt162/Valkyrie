import React from 'react';
import { X } from 'lucide-react';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  size?: 'sm' | 'md' | 'lg' | 'xl';
}

const sizeStyles = {
  sm: 'max-w-md',
  md: 'max-w-lg',
  lg: 'max-w-2xl',
  xl: 'max-w-4xl',
};

export const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  children,
  size = 'md',
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div
        className="absolute inset-0 bg-black/80 backdrop-blur-sm"
        onClick={onClose}
      />
      <div
        className={`relative bg-white dark:bg-[#0a0a0a] border border-green-500/30 rounded-lg shadow-2xl dark:glow-green w-full ${sizeStyles[size]} mx-4 max-h-[90vh] overflow-hidden flex flex-col transition-colors duration-300`}
      >
        <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-[#1a1a1a]">
          <h2 className="text-lg font-mono font-semibold text-green-600 dark:text-green-500">{title}</h2>
          <button
            onClick={onClose}
            className="p-1 hover:bg-gray-100 dark:hover:bg-[#1a1a1a] rounded transition-colors text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
          >
            <X size={20} />
          </button>
        </div>
        <div className="p-4 overflow-y-auto">{children}</div>
      </div>
    </div>
  );
};
