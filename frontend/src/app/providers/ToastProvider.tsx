// src/app/providers/ToastProvider.tsx
import React, { ReactNode } from 'react';
import { Toaster } from '../../components/ui/sonner';

interface ToastProviderProps {
  children: ReactNode;
}

export const ToastProvider: React.FC<ToastProviderProps> = ({ children }) => {
  return (
    <>
      {children}
      <Toaster />
    </>
  );
};