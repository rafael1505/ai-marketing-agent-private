# React Hydration Protection Pattern

This document describes the pattern we use to prevent React hydration errors when working with browser APIs and client-side only features in a Next.js application with server-side rendering.

## What Are Hydration Errors?

Hydration errors occur when the HTML generated during server-side rendering doesn't match what React tries to render on the client side. This typically happens when:

1. Components access browser APIs (`window`, `document`, `localStorage`, etc.) during rendering
2. Components render different content based on client-side state that doesn't exist during server rendering
3. Components use non-deterministic values during rendering (like random numbers or current time)

## Our Solution: Two-Phase Rendering Pattern

We implement a two-phase rendering approach for any component that needs to access browser APIs or client state:

### Phase 1: Initial Render (Server & Client)
- Render a stable, deterministic placeholder that's identical on both server and client
- Avoid accessing any browser APIs or client-specific state
- Ensure the initial UI is meaningful but doesn't depend on client-side data

### Phase 2: Client-Only Updates (After Hydration)
- Track if the component has mounted on the client using a state flag
- Only access browser APIs after confirming client-side rendering
- Apply client-specific UI changes only after hydration is complete

## Implementation: useClientSide Hook

We've created a custom hook to standardize this pattern:

```tsx
import { useClientSide } from '@/hooks/use-client-side';

function MyComponent() {
  const { isClient } = useClientSide();
  const [data, setData] = useState(null);
  
  useEffect(() => {
    if (isClient) {
      // Safe to access localStorage, window, etc.
      const storedValue = localStorage.getItem('my-key');
      setData(storedValue);
    }
  }, [isClient]);
  
  // Server-safe rendering
  if (!isClient) {
    return <div>Loading...</div>;
  }
  
  // Client-only rendering
  return <div>Client data: {data}</div>;
}
```

## Related Hooks

We've also created specialized hooks built on this pattern:

### useLocalStorage

Safely access and update localStorage values:

```tsx
const { value, setValue, isLoading } = useLocalStorage('theme', 'light');

if (isLoading) return <div>Loading...</div>;

return (
  <select value={value} onChange={(e) => setValue(e.target.value)}>
    <option value="light">Light</option>
    <option value="dark">Dark</option>
  </select>
);
```

## Example Components

See `components/examples/hydration-safe-example.tsx` for a complete example of a component that safely uses browser APIs without causing hydration errors.

## When To Use This Pattern

Use this pattern whenever:

1. Your component needs to access browser APIs (`window`, `document`, `localStorage`, etc.)
2. Your component renders differently based on client-side state
3. You're experiencing React hydration errors in the console

## Benefits

1. Eliminates React hydration errors and warnings
2. Improves rendering performance
3. Makes components more predictable and easier to test
4. Provides a consistent approach to handling client-side functionality
