import * as React from "react";
import { cn } from "@/lib/utils";
import { Slot } from "@radix-ui/react-slot";

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "default" | "outline" | "ghost" | "link" | "destructive";
  size?: "default" | "sm" | "lg" | "icon";
  isLoading?: boolean;
  asChild?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      className,
      variant = "default",
      size = "default",
      isLoading = false,
      asChild = false,
      disabled,
      children,
      ...props
    },
    ref
  ) => {
    const Comp = asChild ? Slot : "button";
    const buttonProps = {
      className: cn(
        "inline-flex items-center justify-center rounded-md font-medium btn-scale directBtnScale focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none",
        {
          "bg-gradient-to-r from-blue-500 to-blue-600 text-white hover:shadow-lg hover:from-blue-600 hover:to-blue-700 shadow": variant === "default",
          "bg-gradient-to-r from-red-500 to-red-600 text-white hover:shadow-lg hover:from-red-600 hover:to-red-700 shadow": variant === "destructive",
          "border border-gray-200 bg-white hover:bg-gray-50 hover:border-blue-300 hover:text-blue-500": variant === "outline",
          "hover:bg-gray-100 hover:text-blue-500": variant === "ghost",
          "underline-offset-4 hover:underline text-blue-500": variant === "link",
          "h-10 py-2 px-4 text-sm": size === "default",
          "h-9 px-3 rounded-md text-xs": size === "sm",
          "h-11 px-8 rounded-md text-base": size === "lg",
          "h-10 w-10": size === "icon",
        },
        className
      ),
      ref: ref,
      disabled: disabled || isLoading,
      ...props
    };

    if (asChild) {
      return <Comp {...buttonProps}>{children}</Comp>;
    }

    return (
      <Comp {...buttonProps}>
        {isLoading && (
          <span className="mr-2">
            <svg
              className="animate-spin -ml-1 mr-2 h-4 w-4 text-white"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              ></circle>
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              ></path>
            </svg>
          </span>
        )}
        {children}
      </Comp>
    );
  }
);

Button.displayName = "Button";

export { Button };
