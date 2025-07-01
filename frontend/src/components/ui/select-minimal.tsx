"use client";

import * as React from "react";

// Simple Select component to replace the more complex one
export const Select = ({
  children,
  defaultValue,
  value,
  onValueChange,
}: {
  children: React.ReactNode;
  defaultValue?: string;
  value?: string;
  onValueChange?: (value: string) => void;
}) => {
  return <div className="relative">{children}</div>;
};

export const SelectTrigger = ({
  children,
}: {
  children: React.ReactNode;
}) => {
  return (
    <button
      type="button"
      className="flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
    >
      {children}
      <span className="h-4 w-4 opacity-50">▼</span>
    </button>
  );
};

export const SelectValue = ({
  placeholder,
}: {
  placeholder?: string;
}) => {
  return <span>{placeholder}</span>;
};

export const SelectContent = ({
  children,
}: {
  children: React.ReactNode;
}) => {
  return (
    <div className="relative z-50 min-w-[8rem] overflow-hidden rounded-md border bg-popover text-popover-foreground shadow-md animate-in fade-in-80 translate-y-1">
      <div className="p-1">{children}</div>
    </div>
  );
};

export const SelectItem = ({
  value,
  children,
}: {
  value: string;
  children: React.ReactNode;
}) => {
  return (
    <div className="relative flex w-full cursor-default select-none items-center rounded-sm py-1.5 pl-8 pr-2 text-sm outline-none focus:bg-accent focus:text-accent-foreground data-[disabled]:pointer-events-none data-[disabled]:opacity-50">
      {children}
    </div>
  );
};
