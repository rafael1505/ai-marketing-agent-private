# API Status Banner Integration Guide

To help developers quickly identify and troubleshoot API connection issues, we've created a status banner that can be integrated into any page of the application.

## How to Add the API Status Banner

### Option 1: Add to the main layout file

Add the following code to your main layout file (like `frontend/src/app/[locale]/layout.tsx`):

```tsx
// Add API Status Banner for development environments only
const ApiStatusBanner = () => {
  // Only render in development
  if (process.env.NODE_ENV !== 'development') return null;
  
  return (
    <div
      dangerouslySetInnerHTML={{
        __html: `<iframe 
          src="/api-status-banner.html" 
          style="border: none; position: fixed; bottom: 0; right: 0; z-index: 9999; width: 400px; height: 60px; overflow: hidden;" 
          title="API Status"
        ></iframe>`
      }}
    />
  );
};

// Then include the component in your layout:
{process.env.NODE_ENV === 'development' && <ApiStatusBanner />}
```

### Option 2: Add to individual pages

For pages where you want to show the banner, add:

```tsx
// At the top of your component file:
import { useEffect } from 'react';

// In your component function:
useEffect(() => {
  // Only in development
  if (process.env.NODE_ENV !== 'development') return;
  
  // Add the iframe element
  const iframe = document.createElement('iframe');
  iframe.src = '/api-status-banner.html';
  iframe.style.border = 'none';
  iframe.style.position = 'fixed';
  iframe.style.bottom = '0';
  iframe.style.right = '0';
  iframe.style.zIndex = '9999';
  iframe.style.width = '400px';
  iframe.style.height = '60px';
  iframe.style.overflow = 'hidden';
  iframe.title = 'API Status';
  
  // Append to the body
  document.body.appendChild(iframe);
  
  // Cleanup on unmount
  return () => {
    document.body.removeChild(iframe);
  };
}, []);
```

### Option 3: Add using a script tag

For simplicity, you can add a script tag to your HTML that will load the banner:

```html
<!-- Add at the end of the <body> tag -->
<script>
  // Only in development
  if (process.env.NODE_ENV === 'development' || 
      window.location.hostname === 'localhost' || 
      window.location.hostname === '127.0.0.1') {
    const iframe = document.createElement('iframe');
    iframe.src = '/api-status-banner.html';
    iframe.style.border = 'none';
    iframe.style.position = 'fixed';
    iframe.style.bottom = '0';
    iframe.style.right = '0';
    iframe.style.zIndex = '9999';
    iframe.style.width = '400px';
    iframe.style.height = '60px';
    iframe.style.overflow = 'hidden';
    iframe.title = 'API Status';
    document.body.appendChild(iframe);
  }
</script>
```

## Features of the API Status Banner

The banner provides:

1. **Real-time API status indicator**:
   - Green: Connected to port 8088 (correct)
   - Red: Connected to port 8089 (wrong) or not connected

2. **Quick access links**:
   - "Test API Connection" - Opens the comprehensive test tool
   - "Port Guide" - Opens the port configuration documentation

3. **User control**:
   - Close button to dismiss the banner
   - Banner state is saved to localStorage to respect user preferences

## Customization

The banner is designed to be non-intrusive and only appears in development environments. 
If you need to customize its appearance, edit the `frontend/public/api-status-banner.html` file.
