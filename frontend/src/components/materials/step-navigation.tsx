"use client";

import React, { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

export interface StepNavigationProps {
  currentStep: number;
  totalSteps: number;
  stepTitles: string[];
  onPrevious?: () => void;
  onNext?: () => void;
  onCancel?: () => void;
  onSaveDraft?: () => Promise<void> | void;
  canGoNext?: boolean;
  canGoPrevious?: boolean;
  hasUnsavedChanges?: boolean;
  isNextLoading?: boolean;
  isPreviousLoading?: boolean;
  showSaveDraft?: boolean;
  showCancel?: boolean;
  translations: {
    previous_step?: string;
    next_step?: string;
    save_draft?: string;
    cancel_editing?: string;
    unsaved_changes?: string;
    unsaved_changes_message?: string;
    confirm?: string;
    back?: string;
  };
}

/**
 * StepNavigation Component
 * 
 * Apple-inspired navigation component for multi-step material creation/editing.
 * Features:
 * - Smooth transitions between steps
 * - Unsaved changes detection and warning
 * - Keyboard shortcuts (Ctrl+ArrowLeft/Right)
 * - Responsive design (mobile/desktop)
 * - Accessible (WCAG AA compliant)
 * - Clean, minimal design following UX guidelines
 */
export function StepNavigation({
  currentStep,
  totalSteps,
  stepTitles,
  onPrevious,
  onNext,
  onCancel,
  onSaveDraft,
  canGoNext = true,
  canGoPrevious = true,
  hasUnsavedChanges = false,
  isNextLoading = false,
  isPreviousLoading = false,
  showSaveDraft = true,
  showCancel = true,
  translations,
}: StepNavigationProps) {
  const [showUnsavedDialog, setShowUnsavedDialog] = useState(false);
  const [pendingAction, setPendingAction] = useState<"previous" | "cancel" | null>(null);
  const [draftSaving, setDraftSaving] = useState(false);

  // Handle keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      // Ctrl/Cmd + ArrowLeft = Previous
      if ((event.ctrlKey || event.metaKey) && event.key === "ArrowLeft") {
        event.preventDefault();
        if (canGoPrevious && onPrevious) {
          handlePreviousClick();
        }
      }
      
      // Ctrl/Cmd + ArrowRight = Next
      if ((event.ctrlKey || event.metaKey) && event.key === "ArrowRight") {
        event.preventDefault();
        if (canGoNext && onNext) {
          onNext();
        }
      }
      
      // Ctrl/Cmd + S = Save Draft
      if ((event.ctrlKey || event.metaKey) && event.key === "s") {
        event.preventDefault();
        if (showSaveDraft && onSaveDraft) {
          handleSaveDraft();
        }
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [canGoNext, canGoPrevious, onNext, onPrevious, onSaveDraft, showSaveDraft]);

  const handlePreviousClick = () => {
    if (hasUnsavedChanges) {
      setPendingAction("previous");
      setShowUnsavedDialog(true);
    } else {
      onPrevious?.();
    }
  };

  const handleCancelClick = () => {
    if (hasUnsavedChanges) {
      setPendingAction("cancel");
      setShowUnsavedDialog(true);
    } else {
      onCancel?.();
    }
  };

  const handleConfirmUnsavedAction = () => {
    setShowUnsavedDialog(false);
    if (pendingAction === "previous") {
      onPrevious?.();
    } else if (pendingAction === "cancel") {
      onCancel?.();
    }
    setPendingAction(null);
  };

  const handleSaveDraft = async () => {
    if (!onSaveDraft) return;
    
    setDraftSaving(true);
    try {
      await onSaveDraft();
    } finally {
      setDraftSaving(false);
    }
  };

  const currentStepTitle = stepTitles[currentStep] || `Step ${currentStep + 1}`;

  return (
    <>
      {/* Navigation Bar - Fixed at bottom with Apple-inspired design */}
      <div className="fixed bottom-0 left-0 right-0 z-40 bg-white border-t border-gray-200 shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16 sm:h-20">
            {/* Left Section - Previous & Cancel */}
            <div className="flex items-center gap-2">
              {canGoPrevious && onPrevious && (
                <Button
                  variant="outline"
                  onClick={handlePreviousClick}
                  disabled={isPreviousLoading}
                  className="rounded-xl border-gray-300 hover:bg-gray-50 transition-all duration-200"
                  aria-label={translations.previous_step || "Previous Step"}
                >
                  <svg className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                  </svg>
                  <span className="hidden sm:inline">
                    {translations.previous_step || "Previous"}
                  </span>
                  <span className="sm:hidden">
                    {translations.back || "Back"}
                  </span>
                </Button>
              )}
              
              {showCancel && onCancel && (
                <Button
                  variant="ghost"
                  onClick={handleCancelClick}
                  className="rounded-xl text-gray-600 hover:text-gray-900 hover:bg-gray-100 transition-all duration-200"
                  aria-label={translations.cancel_editing || "Cancel"}
                >
                  <svg className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                  <span className="hidden sm:inline">
                    {translations.cancel_editing || "Cancel"}
                  </span>
                </Button>
              )}
            </div>

            {/* Center Section - Step Indicator (hidden on mobile) */}
            <div className="hidden md:flex items-center gap-3">
              <div className="flex items-center gap-2">
                {Array.from({ length: totalSteps }).map((_, index) => (
                  <div
                    key={index}
                    className={`h-2 rounded-full transition-all duration-300 ${
                      index === currentStep
                        ? "w-8 bg-blue-500"
                        : index < currentStep
                        ? "w-2 bg-green-500"
                        : "w-2 bg-gray-300"
                    }`}
                    aria-label={`Step ${index + 1}${index === currentStep ? " (current)" : index < currentStep ? " (completed)" : ""}`}
                  />
                ))}
              </div>
              <span className="text-sm text-gray-600 font-medium ml-2">
                {currentStepTitle}
              </span>
            </div>

            {/* Right Section - Save & Next */}
            <div className="flex items-center gap-2">
              {showSaveDraft && onSaveDraft && (
                <Button
                  variant="outline"
                  onClick={handleSaveDraft}
                  disabled={draftSaving}
                  className="rounded-xl border-gray-300 hover:bg-gray-50 transition-all duration-200"
                  aria-label={translations.save_draft || "Save Draft"}
                >
                  <svg className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4" />
                  </svg>
                  <span className="hidden sm:inline">
                    {draftSaving ? "Saving..." : translations.save_draft || "Save"}
                  </span>
                </Button>
              )}
              
              {onNext && (
                <Button
                  onClick={onNext}
                  disabled={!canGoNext || isNextLoading}
                  className="rounded-xl bg-blue-500 hover:bg-blue-600 text-white shadow-sm transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                  aria-label={translations.next_step || "Next Step"}
                >
                  <span className="hidden sm:inline">
                    {isNextLoading ? "Loading..." : translations.next_step || "Next"}
                  </span>
                  <span className="sm:hidden">
                    {translations.next_step?.split(" ")[0] || "Next"}
                  </span>
                  <svg className="h-4 w-4 ml-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </Button>
              )}
            </div>
          </div>

          {/* Mobile Step Indicator */}
          <div className="md:hidden pb-3 flex items-center justify-center gap-2">
            <div className="flex items-center gap-2">
              {Array.from({ length: totalSteps }).map((_, index) => (
                <div
                  key={index}
                  className={`h-1.5 rounded-full transition-all duration-300 ${
                    index === currentStep
                      ? "w-6 bg-blue-500"
                      : index < currentStep
                      ? "w-1.5 bg-green-500"
                      : "w-1.5 bg-gray-300"
                  }`}
                />
              ))}
            </div>
            <span className="text-xs text-gray-500 font-medium ml-2">
              {currentStep + 1}/{totalSteps}
            </span>
          </div>
        </div>
      </div>

      {/* Unsaved Changes Confirmation Dialog */}
      <Dialog open={showUnsavedDialog} onOpenChange={setShowUnsavedDialog}>
        <DialogContent className="rounded-2xl">
          <DialogHeader>
            <DialogTitle className="text-xl font-semibold">
              {translations.unsaved_changes || "Unsaved Changes"}
            </DialogTitle>
            <DialogDescription className="text-gray-600">
              {translations.unsaved_changes_message || "Are you sure you want to leave? Your changes will be lost."}
            </DialogDescription>
          </DialogHeader>
          <DialogFooter className="flex gap-2 mt-6">
            <Button
              variant="outline"
              onClick={() => setShowUnsavedDialog(false)}
              className="rounded-xl"
            >
              {translations.back || "Cancel"}
            </Button>
            <Button
              onClick={handleConfirmUnsavedAction}
              className="rounded-xl bg-red-500 hover:bg-red-600 text-white"
            >
              {translations.confirm || "Confirm"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Spacer to prevent content from being hidden under fixed navigation */}
      <div className="h-16 sm:h-20 md:h-20" aria-hidden="true" />
    </>
  );
}
