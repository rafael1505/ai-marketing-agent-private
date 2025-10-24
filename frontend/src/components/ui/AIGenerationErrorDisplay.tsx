import React, { useState } from 'react';
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";

export interface AIGenerationError {
  type: string;
  message: string;
  userMessage: string;
  provider: string;
  suggestedAction: string;
  retryPossible: boolean;
  correlationId?: string;
  timestamp: string;
}

interface ErrorDisplayProps {
  error: AIGenerationError;
  onRetry?: () => void;
  onDismiss?: () => void;
}

export const AIGenerationErrorDisplay: React.FC<ErrorDisplayProps> = ({
  error,
  onRetry,
  onDismiss
}) => {
  return (
    <Alert className="border-red-200 bg-red-50">
      <AlertDescription>
        <div className="space-y-3">
          <div>
            <h4 className="font-medium text-red-800">Erro na Geração de Imagem</h4>
            <p className="text-red-700 mt-1">{error.userMessage}</p>
          </div>
          
          {error.suggestedAction && (
            <div className="text-sm text-red-600">
              <strong>Ação sugerida:</strong> {error.suggestedAction}
            </div>
          )}
          
          <div className="flex gap-2 mt-3">
            {error.retryPossible && onRetry && (
              <Button
                size="sm"
                variant="outline"
                onClick={onRetry}
                className="text-red-700 border-red-300 hover:bg-red-100"
              >
                Tentar Novamente
              </Button>
            )}
            
            {onDismiss && (
              <Button
                size="sm"
                variant="ghost"
                onClick={onDismiss}
                className="text-red-600 hover:bg-red-100"
              >
                Dispensar
              </Button>
            )}
          </div>
        </div>
      </AlertDescription>
    </Alert>
  );
};

export const useAIGenerationErrors = () => {
  const [errors, setErrors] = useState<AIGenerationError[]>([]);

  const addError = (error: AIGenerationError) => {
    setErrors(prev => [...prev, error]);
  };

  const removeError = (correlationId: string) => {
    setErrors(prev => prev.filter(e => e.correlationId !== correlationId));
  };

  const clearErrors = () => {
    setErrors([]);
  };

  return {
    errors,
    addError,
    removeError,
    clearErrors
  };
};

export default AIGenerationErrorDisplay;
