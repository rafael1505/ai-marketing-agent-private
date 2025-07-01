"use client";

import React from "react";

interface PricingBadgeProps {
  tier: 'free' | 'freemium' | 'paid';
  className?: string;
}

export function PricingBadge({ tier, className }: PricingBadgeProps) {
  const getBadgeStyles = () => {
    switch (tier) {
      case 'free':
        return {
          className: "bg-green-100 text-green-800 border-green-200",
          label: "Free",
          icon: "🆓"
        };
      case 'freemium':
        return {
          className: "bg-blue-100 text-blue-800 border-blue-200",
          label: "Freemium", 
          icon: "💎"
        };
      case 'paid':
        return {
          className: "bg-purple-100 text-purple-800 border-purple-200",
          label: "Paid",
          icon: "💳"
        };
      default:
        return {
          className: "bg-gray-100 text-gray-800 border-gray-200",
          label: "Unknown",
          icon: "❓"
        };
    }
  };

  const { className: badgeClass, label, icon } = getBadgeStyles();

  return (
    <span 
      className={`inline-flex items-center gap-1 px-2 py-1 text-xs font-medium rounded-full border ${badgeClass} ${className || ""}`}
    >
      <span>{icon}</span>
      {label}
    </span>
  );
}
