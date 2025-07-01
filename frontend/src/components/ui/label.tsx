import React from "react";
import { cn } from "@/lib/utils";

interface LabelProps extends React.LabelHTMLAttributes<HTMLLabelElement> {
  optional?: boolean;
}

const Label = React.forwardRef<HTMLLabelElement, LabelProps>(
  ({ className, children, optional, ...props }, ref) => {
    return (
      <div className="flex items-baseline justify-between">
        <label
          ref={ref}
          className={cn(
            "text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70",
            className
          )}
          {...props}
        >
          {children}
        </label>
        {optional && (
          <span className="text-xs text-gray-500">Optional</span>
        )}
      </div>
    );
  }
);

Label.displayName = "Label";

export { Label };
