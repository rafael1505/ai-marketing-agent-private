declare module "@radix-ui/react-select" {
  import * as React from "react";

  // Add minimal type definitions for what we use in our Select component
  export const Root: React.FC<any>;
  export const Group: React.FC<any>;
  export const Value: React.FC<any>;
  export const Trigger: React.ForwardRefExoticComponent<any>;
  export const Portal: React.FC<any>;
  export const Content: React.ForwardRefExoticComponent<any>;
  export const Viewport: React.FC<any>;
  export const Item: React.ForwardRefExoticComponent<any>;
  export const ItemIndicator: React.FC<any>;
  export const ItemText: React.FC<any>;
  export const Label: React.ForwardRefExoticComponent<any>;
  export const Separator: React.ForwardRefExoticComponent<any>;
  export const Icon: React.FC<any>;
}

declare module "lucide-react" {
  import * as React from "react";
  
  // Add minimal type definitions for what we use in our components
  export const ChevronDown: React.FC<any>;
  export const Check: React.FC<any>;
  export const X: React.FC<any>;
}
