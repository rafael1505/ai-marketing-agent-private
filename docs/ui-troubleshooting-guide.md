# UI Update and Troubleshooting Guide

## Updated UI Components and Styling System

The UI has been enhanced with the following improvements:

- **Modern Styling**: Gradient text, hover effects, and animations
- **Component Classes**: Consistent styling for cards, buttons, and forms
- **New Style Debugging Tools**: Added utilities to help diagnose styling issues
- **Port Configuration**: Changed from 3088 to 3001 for better compatibility

## Fix Metadata Warnings
The metadata warnings you're seeing are related to how Next.js expects viewport and themeColor settings.

1. Open `frontend/src/app/layout.tsx`
2. Make sure it looks like this structure:
```tsx
import type { Metadata, Viewport } from "next";

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
  themeColor: "#3B82F6",
};

export const metadata: Metadata = {
  title: "AI Marketing Agent",
  description: "Generate marketing materials with AI assistance",
  // other metadata...
};
```

## Make UI Changes Visible
To ensure your UI changes are visible:

1. Clear the Next.js build cache:
```bash
cd frontend
rm -rf .next
```

2. Restart the frontend service with a clean environment:
```bash
cd frontend
npm run dev -- --port 3001
```

3. If the browser still shows the old UI, clear your browser cache:
   - Chrome: Press Ctrl+Shift+Delete
   - Select "Cached images and files"
   - Click "Clear data"
   - Hard refresh the page with Ctrl+F5

## Style Debugging Tools

We've added several tools to help diagnose and fix styling issues:

1. **Style Debugging Page**:
   - Access http://localhost:3001/style-debug to see all styled components

2. **CSS Utilities**:
   - Use helper functions from `src/lib/style-utils.ts`:
     ```tsx
     import { gradientText, withHoverCard, withButtonScale } from "@/lib/style-utils";
     
     // Apply gradient text to headings
     <h1>{gradientText("My Heading")}</h1>
     
     // Add hover effects to cards
     <Card className={withHoverCard("")}>...</Card>
     
     // Add button animations
     <Button className={withButtonScale("")}>Click Me</Button>
     ```

3. **Style Inspector**:
   - Available on the style debug page
   - Hover over elements to see their applied classes

## CSS Classes Reference

The following custom CSS classes are available:

| Class Name | Description | Example Usage |
|------------|-------------|--------------|
| `gradient-text` | Creates a blue-to-purple gradient text | `<h1 className="gradient-text">Title</h1>` |
| `hover-card` | Adds elevation and scaling on hover | `<Card className="hover-card">...</Card>` |
| `btn-scale` | Adds scaling effect to buttons | `<button className="btn-scale">...</button>` |
| `fade-in` | Animates element fading in | `<div className="fade-in">...</div>` |
| `stagger-fade-in` | Children fade in with delays | `<div className="stagger-fade-in"><p>1</p><p>2</p></div>` |
| `spinner` | Creates a loading spinner | `<div className="spinner"></div>` |

## Troubleshoot Common Issues

### Styles Not Applying Correctly

If your styles aren't being applied properly:

1. **Use Force Styles Feature**:
   - Press `Alt+S` on any page to force-apply critical styles
   - Alternatively, import and use the utility directly:
     ```tsx
     import { forceApplyCustomStyles } from "@/lib/force-styles";
     
     // In a component with useEffect:
     useEffect(() => {
       forceApplyCustomStyles();
     }, []);
     ```

2. **Check CSS Import Order**:
   - In `src/app/layout.tsx`, ensure imports are in this order:
     ```tsx
     import "./globals.css";
     import "./custom-styles.css";
     ```

2. **Clear Cache and Rebuild**:
   - Use the rebuild script:
     ```bash
     ./rebuild-frontend.sh
     ```
   - Or manually:
     ```bash
     cd frontend
     rm -rf .next
     npm run build
     npm run dev -- --port 3001
     ```

3. **Inspect Browser Elements**:
   - Use browser devtools (F12) to inspect elements
   - Check if classes are applied but overridden
   - Look for CSS specificity issues

4. **Check Tailwind Configuration**:
   - Verify `tailwind.config.js` has all content paths:
     ```js
     content: [
       './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
       './src/components/**/*.{js,ts,jsx,tsx,mdx}',
       './src/app/**/*.{js,ts,jsx,tsx,mdx}',
       './src/lib/**/*.{js,ts,jsx,tsx,mdx}',
     ],
     ```

### If the frontend won't start:
1. Check for port conflicts:
```bash
lsof -i :3001
```

2. If something is using the port, kill it:
```bash
kill -9 $(lsof -t -i:3001)
```

3. Check for Node.js process issues:
```bash
ps aux | grep node
```

### If the styling isn't showing up:
1. Make sure the CSS import order in layout.tsx is correct:
```tsx
import "./globals.css";
import "./custom-styles.css";
```

2. Verify there are no errors in the browser console that might be preventing CSS from loading

## Verify UI Updates
The updated UI should include:
- Gradient text headers
- Card hover effects
- Animated buttons
- Fade-in animations
- Modern color scheme with blue and purple accents
