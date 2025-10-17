// src/hooks/useToast.ts
import { toast } from 'sonner';

export const useToast = () => {
  return {
    toast: (options: { title?: string; description?: string; variant?: 'default' | 'destructive' }) => {
      const { title, description, variant } = options;
      toast(
        title || '',
        {
          description,
          className:
            variant === 'destructive'
              ? 'bg-destructive text-destructive-foreground'
              : undefined,
        }
      );
    },
  };
};
