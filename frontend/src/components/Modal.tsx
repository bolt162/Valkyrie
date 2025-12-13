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
        className={`relative bg-[#0a0a0a] border border-green-500/30 rounded-lg shadow-2xl glow-green w-full ${sizeStyles[size]} mx-4 max-h-[90vh] overflow-hidden flex flex-col`}
      >
        <div className="flex items-center justify-between p-4 border-b border-[#1a1a1a]">
          <h2 className="text-lg font-mono font-semibold text-green-500">{title}</h2>
          <button
            onClick={onClose}
            className="p-1 hover:bg-[#1a1a1a] rounded transition-colors text-gray-400 hover:text-white"
          >
            <X size={20} />
          </button>
        </div>
        <div className="p-4 overflow-y-auto">{children}</div>
      </div>
    </div>
  );
};
