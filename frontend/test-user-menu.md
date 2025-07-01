# UserMenu Integration Test Plan

## Test Scenarios

### 1. Unauthenticated State
- [ ] Visit http://localhost:3000
- [ ] Verify that the navbar shows "Login" button instead of UserMenu
- [ ] Verify that language switcher (EN/PT) is visible

### 2. Authentication Flow
- [ ] Click "Login" button
- [ ] Should redirect to login page
- [ ] Enter test credentials (test@example.com / password123)
- [ ] Upon successful login, should redirect to dashboard
- [ ] Verify that UserMenu appears in top-right corner

### 3. UserMenu Functionality
- [ ] Verify UserMenu shows user avatar/initials
- [ ] Verify username is displayed (or hidden on mobile)
- [ ] Click UserMenu to open dropdown
- [ ] Verify dropdown contains:
  - [ ] "My Profile" 
  - [ ] "Account Settings"
  - [ ] "Preferences"
  - [ ] "Help & Support"
  - [ ] "Logout"

### 4. UserMenu Interactions
- [ ] Click "My Profile" - should navigate to profile page
- [ ] Click "Account Settings" - should navigate to settings page
- [ ] Click "Preferences" - should navigate to preferences page
- [ ] Click "Help & Support" - should navigate to help page
- [ ] Click "Logout" - should log out and redirect to login page

### 5. Language Support
- [ ] Switch to Portuguese (PT) 
- [ ] Verify UserMenu items are translated
- [ ] Switch back to English (EN)
- [ ] Verify UserMenu items are in English

### 6. Responsive Design
- [ ] Test on mobile view (< 768px)
- [ ] Verify username is hidden on mobile
- [ ] Verify dropdown still works on mobile

### 7. Edge Cases
- [ ] Click outside dropdown to close it
- [ ] Press Escape key to close dropdown
- [ ] Test with mock/test token
- [ ] Test with invalid token (should fallback gracefully)

## Expected User Experience

The new UserMenu should provide a modern, professional user account control similar to applications like:
- Google Workspace
- Microsoft Office 365  
- GitHub
- Notion

### Visual Design
- Clean, minimalist dropdown
- Proper hover states
- Smooth animations
- Consistent with app's design system
- Professional icons for each menu item

### Functionality
- Instant dropdown on click
- Clear visual hierarchy
- Logical grouping of options
- Easy access to common actions
- Secure logout functionality
