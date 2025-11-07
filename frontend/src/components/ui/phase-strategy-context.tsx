"use client";

import React from "react";
import { Material } from "@/types";

interface PhaseStrategyContextProps {
  material: Material | null;
  translations?: Record<string, any>;
}

export const PhaseStrategyContext: React.FC<PhaseStrategyContextProps> = ({
  material,
  translations = {}
}) => {
  if (!material) return null;

  const t = translations;

  return (
    <div className="mb-6 p-5 bg-gradient-to-r from-gray-50 to-blue-50 dark:from-gray-900/50 dark:to-blue-950/30 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm">
      <div className="flex items-center space-x-2 mb-4">
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-blue-600 dark:text-blue-400">
          <path d="M12 20h9"></path>
          <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path>
        </svg>
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
          {t?.creation?.refinement?.strategy_context || "Campaign Strategy (Phase 1)"}
        </h3>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Title */}
        {material.title && (
          <div className="space-y-1">
            <p className="text-xs font-medium text-gray-500 dark:text-gray-400">
              {t?.creation?.idea?.form?.title || "Title"}
            </p>
            <p className="text-sm text-gray-900 dark:text-gray-100 font-medium">
              {material.title}
            </p>
          </div>
        )}
        
        {/* Target Audience */}
        {material.target_audience && (
          <div className="space-y-1">
            <p className="text-xs font-medium text-gray-500 dark:text-gray-400">
              {t?.creation?.idea?.form?.target_audience || "Target Audience"}
            </p>
            <p className="text-sm text-gray-700 dark:text-gray-200">
              {material.target_audience}
            </p>
          </div>
        )}
        
        {/* Campaign Objective */}
        {material.campaign_objective && (
          <div className="space-y-1">
            <p className="text-xs font-medium text-gray-500 dark:text-gray-400">
              {t?.creation?.idea?.form?.campaign_objective || "Campaign Objective"}
            </p>
            <p className="text-sm text-gray-700 dark:text-gray-200">
              {material.campaign_objective}
            </p>
          </div>
        )}
      </div>
      
      {/* Keywords */}
      {material.keywords && material.keywords.length > 0 && (
        <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
          <p className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-2">
            {t?.creation?.idea?.form?.keywords || "Keywords"}
          </p>
          <div className="flex flex-wrap gap-2">
            {material.keywords.map((keyword, idx) => (
              <span
                key={idx}
                className="inline-block px-2 py-1 text-xs bg-blue-100 dark:bg-blue-900/50 text-blue-800 dark:text-blue-200 rounded-full"
              >
                {keyword}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
