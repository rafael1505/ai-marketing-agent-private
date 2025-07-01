# React Hydration Error Prevention Guide

## What are React Hydration Errors?

React hydration errors occur when the HTML generated during server-side rendering doesn't match what React tries to render on the client side. The error message typically looks like:

```
Error: Text content does not match server-rendered HTML.

Warning: Text content did not match. Server: "..." Client: "..."
```

These errors can cause poor user experience, flickering UI, and can break functionality.

## Recently Fixed Hydration Issues

We recently fixed a hydration error in the `fixed-style/page.tsx` file where client-side rendering was producing different content than server-side rendering. The solution was to:

1. Add an `isClient` flag using useState that's set to true only after the component mounts
2. Only render the actual content with dynamic values when on the client side
3. Render a placeholder with a consistent structure during server-side rendering

### Authentication Components and Navigation System (May 2025)

We fixed a series of hydration errors in the Navbar and authentication systems where conditional rendering based on authentication state was causing mismatches between server and client rendering:

1. Added explicit client-side detection to all components accessing authentication state
2. Implemented two-phase rendering in the Navbar component
3. Removed key-based re-rendering in MainLayout
4. Used safe defaults for AuthContext during server rendering

The key pattern implemented across these components was:

```tsx
// Phase 1: Track if we're on the client
const [isClient, setIsClient] = React.useState(false);

// First effect: Just set client flag
React.useEffect(() => {
  setIsClient(true);
}, []);

// Second effect: Only access auth after client detection
React.useEffect(() => {
  if (isClient) {
    // Safe to access localStorage, authentication state, etc.
  }
}, [isClient]);

// For server render, use a safe default output
if (!isClient) {
  return <SafeServerContent />; // No auth-dependent UI
}

// Only on client after hydration
return <ClientAuthenticatedContent />;
```

See `react-hydration-fixes-summary.md` for complete details on this fix.

## Common Causes in Our Project

1. **Browser-only API access during rendering**
   - Accessing `window`, `document`, or other browser-only APIs during component rendering
   - Example: `document.body.className` in JSX templates

2. **Dynamic content differences**
   - Different content between server and client renders
   - Example: Generating random IDs or using `Date.now()`

3. **CSS Variable access**
   - Reading CSS variables or computed styles during rendering
   - Example: `getComputedStyle(document.documentElement).getPropertyValue('--primary')`

## Best Practices to Prevent Hydration Errors

### 1. Use Client-Side Effects for Browser APIs

Always access browser APIs inside `useEffect` hooks, never during rendering:

```tsx
// ❌ BAD - Accessing browser API during render
function Component() {
  const bodyClasses = document.body.className;
  return <div>{bodyClasses}</div>;
}

// ✅ GOOD - Using useEffect and useState
function Component() {
  const [bodyClasses, setBodyClasses] = useState("Loading...");
  
  useEffect(() => {
    setBodyClasses(document.body.className);
  }, []);
  
  return <div>{bodyClasses}</div>;
}
```

### 2. Add Browser Environment Checks

When working with browser APIs, always check for their existence:

```tsx
// ❌ BAD - Direct access
const styles = window.getComputedStyle(element);

// ✅ GOOD - Safe access
const getStyles = () => {
  if (typeof window !== 'undefined') {
    return window.getComputedStyle(element);
  }
  return null;
};
```

### 3. Extract Client-Only Components

Extract parts that need browser APIs into separate client-only components:

```tsx
// ✅ GOOD - Separate client component
"use client";
function StyleDebugger() {
  const [styles, setStyles] = useState({});
  
  useEffect(() => {
    // Browser-only code here
  }, []);
  
  return <pre>{JSON.stringify(styles, null, 2)}</pre>;
}

// Parent component doesn't need to be client-only
function Page() {
  return (
    <div>
      <h1>My Page</h1>
      <StyleDebugger />
    </div>
  );
}
```

### 4. Use Two-Phase Rendering with Client Detection

Use a dedicated client detection flag to ensure consistent rendering:

```tsx
// ✅ GOOD - Two-phase rendering with client detection
function Component() {
  // Phase 1: Track if we're on the client
  const [isClient, setIsClient] = useState(false);
  // Phase 2: Only after client is confirmed, handle actual data
  const [data, setData] = useState(null);
  
  // First effect: Just set client flag
  useEffect(() => {
    setIsClient(true);
  }, []);
  
  // Second effect: Only run after client is confirmed
  useEffect(() => {
    if (isClient) {
      fetchData().then(result => {
        setData(result);
      });
    }
  }, [isClient]);
  
  // Server & initial client render - use a stable placeholder
  if (!isClient) {
    return <div className="placeholder">Loading...</div>;
  }
  
  // Only on client after hydration is complete
  return <div>{data}</div>;
}
```

### 5. Use Dynamic Imports for Browser-Only Components

Consider using dynamic imports for components with browser dependencies:

```tsx
// ✅ GOOD - Dynamic import
import dynamic from 'next/dynamic';

const BrowserComponent = dynamic(
  () => import('./BrowserComponent'),
  { ssr: false }
);
```

## Project-Specific Guidelines

1. **Style Debugging Tools**
   - Always wrap style debugging in `useEffect` hooks
   - Extract style inspection into client-only components
   - Use state variables to store computed styles

2. **CSS Variable Access**
   - Never access CSS variables during initial render
   - Use `useState` + `useEffect` pattern for computed styles

3. **DOM Manipulation**
   - Only manipulate DOM in `useEffect` hooks
   - Always check for browser environment before DOM operations
   - Clean up event listeners and DOM elements in effect cleanup functions

4. **Testing for Hydration**
   - Test your application with both client-side and server-side rendering
   - Build with `npm run build` and test with `npm start` to catch hydration errors

## Examples from Our Project

### Fixed Style Debugger Example

```tsx
// Style debugger component that safely handles browser APIs
const StyleDebugger = () => {
  // Phase 1: Client detection
  const [isClient, setIsClient] = useState(false);
  // Phase 2: Style information (only populated on client)
  const [styleInfo, setStyleInfo] = useState({
    primary: '',
    transition: '',
    bodyClasses: ''
  });

  // First effect: Just detect client
  useEffect(() => {
    setIsClient(true);
  }, []);

  // Second effect: Access browser APIs only after client is confirmed
  useEffect(() => {
    if (isClient) {
      setStyleInfo({
        primary: getComputedStyle(document.documentElement).getPropertyValue('--primary'),
        transition: getComputedStyle(document.documentElement).getPropertyValue('--transition-medium'),
        bodyClasses: document.body.className
      });
    }
  }, [isClient]);

  // If not client, render placeholder with the same structure
  if (!isClient) {
    return (
      <pre className="p-4 bg-gray-100 rounded text-sm overflow-auto">
        <span>Loading style information...</span>
      </pre>
    );
  }

  // Only on client after hydration
  return (
    <pre className="p-4 bg-gray-100 rounded text-sm overflow-auto">
      {`
CSS Variables:
--primary: ${styleInfo.primary}
--transition-medium: ${styleInfo.transition}

Body Classes: ${styleInfo.bodyClasses}
      `}
    </pre>
  );
};
```

By following these guidelines, we can prevent React hydration errors and ensure our application renders consistently across both server and client environments.
