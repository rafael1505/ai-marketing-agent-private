import { useState, useCallback, useRef, useEffect } from 'react';

export interface UseInlineEditOptions<T> {
  initialValue: T;
  onSave: (value: T) => Promise<void>;
  onCancel?: () => void;
  validation?: (value: T) => string | null;
  autoSave?: boolean;
  autoSaveDelay?: number;
}

export interface UseInlineEditReturn<T> {
  value: T;
  originalValue: T;
  isEditing: boolean;
  isDirty: boolean;
  isSaving: boolean;
  error: string | null;
  validationError: string | null;
  
  startEditing: () => void;
  stopEditing: () => void;
  setValue: (value: T) => void;
  save: () => Promise<void>;
  cancel: () => void;
  reset: () => void;
}

export function useInlineEdit<T>({
  initialValue,
  onSave,
  onCancel,
  validation,
  autoSave = true,
  autoSaveDelay = 1000
}: UseInlineEditOptions<T>): UseInlineEditReturn<T> {
  const [value, setValue] = useState<T>(initialValue);
  const [originalValue, setOriginalValue] = useState<T>(initialValue);
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [validationError, setValidationError] = useState<string | null>(null);
  
  const autoSaveTimeoutRef = useRef<NodeJS.Timeout>();
  const isMountedRef = useRef(true);

  // Update original value when initialValue changes
  useEffect(() => {
    if (!isEditing) {
      setValue(initialValue);
      setOriginalValue(initialValue);
    }
  }, [initialValue, isEditing]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      isMountedRef.current = false;
      if (autoSaveTimeoutRef.current) {
        clearTimeout(autoSaveTimeoutRef.current);
      }
    };
  }, []);

  // Auto-save functionality
  useEffect(() => {
    if (!autoSave || !isEditing || !isDirty || isSaving) return;

    // Clear existing timeout
    if (autoSaveTimeoutRef.current) {
      clearTimeout(autoSaveTimeoutRef.current);
    }

    // Set new timeout for auto-save
    autoSaveTimeoutRef.current = setTimeout(() => {
      if (isMountedRef.current && isEditing && isDirty) {
        save();
      }
    }, autoSaveDelay);

    return () => {
      if (autoSaveTimeoutRef.current) {
        clearTimeout(autoSaveTimeoutRef.current);
      }
    };
  }, [value, isEditing, autoSave, autoSaveDelay]);

  // Validation effect
  useEffect(() => {
    if (validation && isEditing) {
      const validationResult = validation(value);
      setValidationError(validationResult);
    } else {
      setValidationError(null);
    }
  }, [value, validation, isEditing]);

  const isDirty = JSON.stringify(value) !== JSON.stringify(originalValue);

  const startEditing = useCallback(() => {
    setIsEditing(true);
    setError(null);
    setValidationError(null);
  }, []);

  const stopEditing = useCallback(() => {
    setIsEditing(false);
    // Clear auto-save timeout when stopping editing
    if (autoSaveTimeoutRef.current) {
      clearTimeout(autoSaveTimeoutRef.current);
    }
  }, []);

  const save = useCallback(async () => {
    if (!isDirty || isSaving || validationError) {
      console.log('🔧 DEBUG: Save blocked - isDirty:', isDirty, 'isSaving:', isSaving, 'validationError:', validationError);
      return;
    }

    console.log('🔧 DEBUG: Starting save process with value:', value);
    setIsSaving(true);
    setError(null);

    try {
      console.log('🔧 DEBUG: Calling onSave function...');
      await onSave(value);
      console.log('🔧 DEBUG: onSave completed successfully');
      console.log('🔧 DEBUG: isMountedRef.current:', isMountedRef.current);
      
      // Always try to update state to prevent stuck states
      try {
        setOriginalValue(value);
        setIsEditing(false);
        console.log('🔧 DEBUG: Save completed - exiting edit mode, new isEditing: false');
      } catch (stateError) {
        console.error('🔧 DEBUG: Failed to update edit state:', stateError);
      }
    } catch (err) {
      console.error('🔧 DEBUG: Save failed with error:', err);
      console.log('🔧 DEBUG: isMountedRef.current in catch:', isMountedRef.current);
      if (isMountedRef.current) {
        setError(err instanceof Error ? err.message : 'Save failed');
      }
    } finally {
      console.log('🔧 DEBUG: Setting isSaving to false');
      console.log('🔧 DEBUG: isMountedRef.current in finally:', isMountedRef.current);
      
      // Always try to update isSaving to prevent stuck loading states
      try {
        setIsSaving(false);
        console.log('🔧 DEBUG: isSaving state updated to false');
      } catch (stateError) {
        console.error('🔧 DEBUG: Failed to update isSaving state:', stateError);
      }
      
      // Force a small delay to ensure state updates are processed
      setTimeout(() => {
        console.log('🔧 DEBUG: Delayed check - isSaving should be false now');
      }, 100);
    }
  }, [value, isDirty, isSaving, validationError, onSave]);

  const cancel = useCallback(() => {
    setValue(originalValue);
    setIsEditing(false);
    setError(null);
    setValidationError(null);
    
    // Clear auto-save timeout when canceling
    if (autoSaveTimeoutRef.current) {
      clearTimeout(autoSaveTimeoutRef.current);
    }
    
    onCancel?.();
  }, [originalValue, onCancel]);

  const reset = useCallback(() => {
    setValue(initialValue);
    setOriginalValue(initialValue);
    setIsEditing(false);
    setError(null);
    setValidationError(null);
    
    // Clear auto-save timeout when resetting
    if (autoSaveTimeoutRef.current) {
      clearTimeout(autoSaveTimeoutRef.current);
    }
  }, [initialValue]);

  const setValueWrapper = useCallback((newValue: T) => {
    setValue(newValue);
    setError(null); // Clear errors when value changes
  }, []);

  return {
    value,
    originalValue,
    isEditing,
    isDirty,
    isSaving,
    error,
    validationError,
    
    startEditing,
    stopEditing,
    setValue: setValueWrapper,
    save,
    cancel,
    reset
  };
}