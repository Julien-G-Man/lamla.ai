# Lamla AI Design System

## Overview

This document outlines the design system for Lamla AI, a Django-based educational platform. The design system provides consistent styling, components, and patterns across all user interfaces.

## Color Palette

### Primary Colors
- **Primary Yellow**: `#FFD600` - Main brand color, used for buttons, highlights, and accents
- **Primary Yellow Dark**: `#FDC72B` - Hover states and secondary actions
- **Primary Yellow Light**: `#FFFBF0` - Background accents and subtle highlights

### Neutral Colors
- **Primary Black**: `#222222` - Main text color
- **Primary Black Light**: `#333333` - Secondary text and borders
- **Primary Black Dark**: `#111111` - Dark backgrounds

### Background Colors
- **Background Primary**: `#FFFFFF` - Main background
- **Background Secondary**: `#F8F9FA` - Page background
- **Background Tertiary**: `#ECF0F1` - Card backgrounds and subtle sections

### Text Colors
- **Text Primary**: `#222222` - Main text
- **Text Secondary**: `#555555` - Secondary text
- **Text Muted**: `#888888` - Muted text and placeholders
- **Text Light**: `#FFFFFF` - Text on dark backgrounds

## Typography

### Font Family
- **Primary**: `'Poppins', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif`

### Font Sizes
- **XS**: `0.75rem` (12px)
- **SM**: `0.875rem` (14px)
- **Base**: `1rem` (16px)
- **LG**: `1.125rem` (18px)
- **XL**: `1.25rem` (20px)
- **2XL**: `1.5rem` (24px)
- **3XL**: `1.875rem` (30px)
- **4XL**: `2.25rem` (36px)

### Font Weights
- **Normal**: `400`
- **Medium**: `500`
- **Semibold**: `600`
- **Bold**: `700`

## Spacing System

### Spacing Scale
- **XS**: `0.25rem` (4px)
- **SM**: `0.5rem` (8px)
- **MD**: `1rem` (16px)
- **LG**: `1.5rem` (24px)
- **XL**: `2rem` (32px)
- **2XL**: `3rem` (48px)
- **3XL**: `4rem` (64px)

## Border Radius

### Radius Scale
- **SM**: `4px`
- **MD**: `8px`
- **LG**: `12px`
- **XL**: `16px`
- **2XL**: `24px`

## Shadows

### Shadow Scale
- **SM**: `0 2px 4px rgba(0, 0, 0, 0.05)`
- **MD**: `0 4px 8px rgba(0, 0, 0, 0.1)`
- **LG**: `0 8px 16px rgba(0, 0, 0, 0.15)`
- **XL**: `0 12px 24px rgba(0, 0, 0, 0.2)`

## Components

### Buttons

#### Primary Button
```html
<a href="#" class="btn btn-primary">Primary Action</a>
```

#### Secondary Button
```html
<a href="#" class="btn btn-secondary">Secondary Action</a>
```

#### Outline Button
```html
<a href="#" class="btn btn-outline">Outline Action</a>
```

#### Button Sizes
- **Default**: `btn`
- **Small**: `btn btn-sm`
- **Large**: `btn btn-lg`

### Cards

#### Basic Card
```html
<div class="card">
    <div class="card-header">
        <h2>Card Title</h2>
    </div>
    <div class="card-content">
        <p>Card content goes here</p>
    </div>
</div>
```

### Forms

#### Form Group
```html
<div class="form-group">
    <label for="input" class="form-label">Label</label>
    <input type="text" id="input" class="form-input" placeholder="Placeholder">
</div>
```

#### Form Input Types
- **Text Input**: `form-input`
- **Textarea**: `form-textarea`
- **Select**: `form-select`

### Navigation

#### Navbar
The navbar is automatically included in the base template and includes:
- Logo with branding
- Navigation links
- Mobile hamburger menu
- User authentication status

## Layout

### Container
```html
<div class="container">
    <!-- Content here -->
</div>
```

### Grid System
```html
<div class="grid grid-2 gap-lg">
    <div>Column 1</div>
    <div>Column 2</div>
</div>
```

#### Grid Options
- **2 Columns**: `grid-2`
- **3 Columns**: `grid-3`
- **4 Columns**: `grid-4`

### Flexbox Utilities
```html
<div class="flex items-center justify-between gap-md">
    <div>Item 1</div>
    <div>Item 2</div>
</div>
```

## Utility Classes

### Text Utilities
- `.text-center` - Center align text
- `.text-left` - Left align text
- `.text-right` - Right align text
- `.text-primary` - Primary text color
- `.text-secondary` - Secondary text color
- `.text-muted` - Muted text color
- `.text-yellow` - Yellow text color
- `.text-light` - Light text color

### Background Utilities
- `.bg-primary` - Primary background
- `.bg-secondary` - Secondary background
- `.bg-tertiary` - Tertiary background
- `.bg-dark` - Dark background
- `.bg-yellow` - Yellow background

### Spacing Utilities
- `.mt-*` - Margin top (sm, md, lg, xl)
- `.mb-*` - Margin bottom (sm, md, lg, xl)
- `.p-*` - Padding (sm, md, lg, xl)
- `.py-xl` - Padding top and bottom

### Border Radius Utilities
- `.rounded-sm` - Small border radius
- `.rounded-md` - Medium border radius
- `.rounded-lg` - Large border radius
- `.rounded-xl` - Extra large border radius

### Shadow Utilities
- `.shadow-sm` - Small shadow
- `.shadow-md` - Medium shadow
- `.shadow-lg` - Large shadow

## Responsive Design

### Breakpoints
- **Mobile**: `max-width: 480px`
- **Tablet**: `max-width: 768px`
- **Desktop**: `max-width: 1024px`

### Mobile-First Approach
The design system uses a mobile-first approach with responsive utilities that scale up for larger screens.

## Usage Guidelines

### 1. Always Use the Base Template
```html
{% extends 'base.html' %}
{% block content %}
    <!-- Your content here -->
{% endblock %}
```

### 2. Use Semantic HTML
Always use semantic HTML elements and add appropriate ARIA labels for accessibility.

### 3. Follow the Color System
Use the predefined color variables instead of hardcoding colors.

### 4. Maintain Consistent Spacing
Use the spacing scale for margins and padding to maintain visual consistency.

### 5. Use Utility Classes
Leverage utility classes for common styling patterns instead of writing custom CSS.

## File Structure

```
static/slide_analyzer/css/
└── main.css          # Main design system file

templates/
├── base.html         # Base template with navigation and footer
└── slides_analyzer/
    ├── home.html     # Home page
    ├── dashboard.html # User dashboard
    ├── upload.html   # Upload page
    └── ...           # Other page templates
```

## Best Practices

1. **Consistency**: Always use the design system components and utilities
2. **Accessibility**: Ensure proper contrast ratios and keyboard navigation
3. **Performance**: Minimize custom CSS and use utility classes
4. **Maintainability**: Keep styles centralized in the main.css file
5. **Responsiveness**: Test on multiple screen sizes and devices

## Getting Started

1. Include the main.css file in your template:
```html
<link rel="stylesheet" href="{% static 'slide_analyzer/css/main.css' %}">
```

2. Extend the base template:
```html
{% extends 'base.html' %}
```

3. Use the design system components and utilities in your content blocks.

## Support

For questions or issues with the design system, refer to this documentation or contact the development team. 