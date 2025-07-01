# TypeScript and JSX Integration Guide

## Recent Fix: JSX in TypeScript Files

We recently fixed an issue where JSX syntax was being used in a regular `.ts` file instead of a `.tsx` file. This was causing compilation errors with messages like:

```
Error: Expected '>', got 'className'
```

## Understanding TypeScript File Extensions

In a TypeScript project using React, there are two main file extensions:

1. **`.ts`** - For pure TypeScript files with no JSX/React components
2. **`.tsx`** - For TypeScript files that include JSX syntax

## Best Practices

1. **Use the correct file extension**:
   - If your file contains JSX (such as `<div>`, `<span>`, etc.), use `.tsx`
   - If your file only contains regular TypeScript with no JSX, use `.ts`

2. **When to create .tsx files**:
   - Any file that returns React components
   - Files that export functions that return JSX elements
   - Utility functions that manipulate or create JSX

3. **When to use .ts files**:
   - Pure utility functions with no JSX
   - Type definitions
   - Configuration files
   - API service wrappers

## Common Mistakes and Solutions

### 1. JSX in .ts files

**Problem**: Including JSX syntax in a `.ts` file:
```typescript
// Wrong approach in a .ts file
export const MyComponent = () => {
  return <div>Hello World</div>;
};
```

**Solution**: Either:
1. Rename the file to `.tsx` (preferred)
2. Create a re-export pattern:
   ```typescript
   // style-utils.ts
   export * from './style-utils.tsx';
   ```

### 2. Import React when using JSX

In projects using React 17+, you don't need to import React explicitly for JSX. However, for clarity and compatibility, it's still a good practice:

```tsx
import React from 'react';

export const MyComponent = () => {
  return <div>Hello World</div>;
};
```

## Handling the Transition

When fixing these issues:

1. Create a new `.tsx` file with the same base name
2. Move all JSX code to this file
3. Update the original `.ts` file to re-export from the `.tsx` file
4. Gradually update imports in other files if needed

This approach ensures backward compatibility while fixing the issue.

## Our Project Convention

For our project, we'll follow these guidelines:
- All files containing UI components should use `.tsx`
- Files with utility functions that return JSX (like `gradientText`) should use `.tsx`
- Pure utility functions with no JSX should use `.ts`

By following these conventions, we'll avoid compilation errors and maintain a clean codebase.
