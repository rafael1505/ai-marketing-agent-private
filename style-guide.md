# AI Marketing Agent Style Guide

## Introduction

This style guide provides guidelines for maintaining consistent UI throughout the AI Marketing Agent application. It defines the design system, color palette, typography, and component styling standards.

## Table of Contents

1. [Color Palette](#color-palette)
2. [Typography](#typography)
3. [Components](#components)
4. [CSS Classes](#css-classes)
5. [Animations](#animations)
6. [Responsive Design](#responsive-design)
7. [Best Practices](#best-practices)

## Color Palette

### Primary Colors
- **Primary Blue**: `#3B82F6` (Used for primary buttons, links, and accents)
- **Primary Purple**: `#A855F7` (Used for gradient effects and secondary accents)
- **Secondary Blue**: `#60A5FA` (Used for hover states and secondary elements)
- **Secondary Purple**: `#C026D3` (Used for gradient ends and emphasis)

### Neutral Colors
- **Background**: `#FFFFFF` (Page background)
- **Card Background**: `#FFFFFF` (Card background)
- **Text Primary**: `#111827` (Primary text color)
- **Text Secondary**: `#6B7280` (Secondary text color)
- **Border Color**: `#E5E7EB` (Borders and separators)

### Semantic Colors
- **Success**: `#10B981` (Success states and confirmations)
- **Error**: `#EF4444` (Error states and destructive actions)
- **Warning**: `#F59E0B` (Warning states and caution actions)
- **Info**: `#3B82F6` (Information states)

### Gradients
- **Primary Gradient**: `linear-gradient(90deg, #3B82F6, #C026D3)` (Used for text and accent backgrounds)
- **Secondary Gradient**: `linear-gradient(90deg, #60A5FA, #A855F7)` (Used for secondary elements)
- **Background Gradient**: `linear-gradient(to right, #F9FAFB, #F3F4F6)` (Subtle background gradient)

## Typography

### Font Family
- **Primary Font**: Inter, system-ui, sans-serif
- **Monospace Font**: Menlo, Monaco, Consolas, monospace

### Font Sizes
- **xs**: 0.75rem (12px)
- **sm**: 0.875rem (14px)
- **base**: 1rem (16px)
- **lg**: 1.125rem (18px)
- **xl**: 1.25rem (20px)
- **2xl**: 1.5rem (24px)
- **3xl**: 1.875rem (30px)
- **4xl**: 2.25rem (36px)

### Font Weights
- **normal**: 400
- **medium**: 500
- **semibold**: 600
- **bold**: 700

## Components

### Buttons
- Use the `Button` component for all buttons
- Apply `directBtnScale` class for hover effects
- Available variants: `default`, `outline`, `ghost`, `link`, `destructive`
- Available sizes: `default`, `sm`, `lg`, `icon`

Example:
```tsx
<Button 
  variant="default" 
  size="default" 
  className="directBtnScale"
>
  Click Me
</Button>
```

### Cards
- Use the `Card` component for all card elements
- Apply `directHoverCard` class for hover effects
- Use CardHeader, CardTitle, CardContent, and CardFooter for structure

Example:
```tsx
<Card className="directHoverCard">
  <CardHeader>
    <CardTitle className="directGradientText">Card Title</CardTitle>
  </CardHeader>
  <CardContent>
    Card content here
  </CardContent>
  <CardFooter>
    <Button className="directBtnScale">Action</Button>
  </CardFooter>
</Card>
```

### Forms
- Group form elements with clearly labeled sections
- Use Label component for all form labels
- Provide adequate spacing between form elements
- Include validation feedback and error messages

Example:
```tsx
<form>
  <div className="space-y-2">
    <Label htmlFor="name">Name</Label>
    <Input id="name" placeholder="Enter your name" />
  </div>
</form>
```

## CSS Classes

### Direct Style Classes
These classes use !important rules and direct styling to ensure they work regardless of CSS processing:

- **directGradientText**: Blue-to-purple gradient text effect
- **directHoverCard**: Elevation and border color change on hover
- **directBtnScale**: Button scaling effect on hover/click
- **directFadeIn**: Fade-in animation effect

Example:
```tsx
<h1 className="directGradientText">Welcome</h1>
```

### Regular Style Classes
These classes depend on the styling system but are preferred when it works correctly:

- **gradient-text**: Blue-to-purple gradient text effect
- **hover-card**: Elevation and border color change on hover
- **btn-scale**: Button scaling effect on hover/click
- **fade-in**: Fade-in animation effect

Example:
```tsx
<h1 className="gradient-text">Welcome</h1>
```

## Animations

### Transitions
- Card hover: 0.3s ease
- Button hover: 0.15s ease
- Content transitions: 0.5s ease

### Keyframe Animations
- Fade in: 0.5s, translate Y from 10px to 0
- Scale: 0.3s, scale from 0.95 to 1

## Responsive Design

### Breakpoints
- **sm**: 640px (Small devices)
- **md**: 768px (Medium devices)
- **lg**: 1024px (Large devices)
- **xl**: 1280px (Extra large devices)
- **2xl**: 1536px (2X large devices)

### Responsive Patterns
- Use container class for consistent margins
- Use grid and flex layouts for responsive design
- Stack elements vertically on mobile, horizontally on larger screens
- Adjust font sizes, padding, and margins at different breakpoints

## Best Practices

### CSS Style Application

1. **CSS Import Order**:
   - First import `globals.css`
   - Then import `custom-styles.css`
   - Finally import `direct-styles.css`

2. **Force Styles When Needed**:
   ```tsx
   import { forceApplyCustomStyles } from "@/lib/force-styles";
   
   useEffect(() => {
     forceApplyCustomStyles();
   }, []);
   ```

3. **Style Debugging**:
   - Use the style-debug page for troubleshooting
   - Check browser dev tools for style application
   - Use `directXXX` classes when styles aren't applying properly

4. **Performance Considerations**:
   - Avoid excessive use of !important rules
   - Use CSS variables for theming
   - Group related styles together
   - Avoid inline styles unless necessary

### Accessibility

- Maintain sufficient color contrast (at least 4.5:1 for normal text)
- Provide focus styles for keyboard navigation
- Use semantic HTML elements
- Include ARIA attributes when needed
- Test with screen readers

### Component Usage

- Use the UI components from `@/components/ui/` whenever possible
- Follow the component API documentation
- Extend components rather than creating new ones
- Maintain consistent spacing and layout throughout the application
