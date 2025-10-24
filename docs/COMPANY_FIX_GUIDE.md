# Company Persistence Fix Guide

This guide walks you through fixing the company information persistence issue in the AI Marketing Agent application.

## Problem Description

When company information (logo, colors, name, etc.) is saved in the settings page, the changes don't persist when navigating away and returning - the data reverts to default values.

## Root Causes

1. **ID Format Mismatch**: The API shows active company with ID "2", but frontend looks for "test_company"
2. **FormData Array Handling Issues**: Brand colors array is not properly processed
3. **Database Layer Inconsistencies**: Different ID formats not handled consistently
4. **Inconsistent Company Lookup Methods**: Multiple ways of looking up companies causing conflicts

## Solution Overview

The solution involves several components:

1. **Database Structure Fix**: Ensures consistent company structures with proper ID fields
2. **CompanyDB Class Patching**: Enhances methods to handle different ID formats and array data
3. **API Route Improvements**: Better handling of FormData arrays
4. **Startup Scripts**: Reliable API and frontend initialization

## Step-by-Step Fix Process

### Step 1: Apply Database Patches

First, apply the patch to fix the CompanyDB class:

```bash
# Make the patch script executable
chmod +x patch_company_db.py

# Run the patch script
./patch_company_db.py
```

This patch enhances the CompanyDB class to properly handle:
- String and numeric IDs
- Test company and active company fallbacks
- Brand colors array processing

### Step 2: Start the Fixed API Server

Use the provided script to start the API server with all fixes applied:

```bash
# Make the script executable
chmod +x start_fixed_api.sh

# Start the API server
./start_fixed_api.sh
```

This script:
- Applies all database patches
- Ensures proper authentication
- Sets up environment variables
- Starts the API server with company persistence fixes

### Step 3: Start the Frontend with Fixed Configuration

Use the provided script to start the frontend:

```bash
# Make the script executable
chmod +x start_fixed_frontend.sh

# Start the frontend
./start_fixed_frontend.sh
```

This script:
- Sets up the correct environment variables
- Ensures consistent API connectivity
- Configures the frontend to use the test_company ID

### Step 4: Verify the Fix

Use the verification script to confirm the fix works correctly:

```bash
# Run the verification script
python verify_company_persistence.py
```

The script checks:
- Database structure
- Company ID consistency
- Brand colors array handling
- End-to-end functionality

## Testing the Fix

1. Navigate to the Settings page: http://localhost:3000/en/settings
2. Update company information (name, logo, colors, etc.)
3. Save the changes
4. Navigate away from the page (e.g., to the Dashboard)
5. Return to the Settings page
6. Verify that all information persists correctly

## Technical Details

### Company ID Handling

The patch ensures consistent handling of company IDs by:
- Making both `_id` and `id` fields consistent
- Adding fallback from test_company to active company when needed
- Handling numeric ID conversion when necessary

### Brand Colors Array Handling

Color arrays are handled properly by:
- Ensuring brand_colors is always stored as a list
- Converting string values to array format when needed
- Proper handling of FormData with array values

### Database Structure

The database structure is enhanced to:
- Use a consistent string-based ID field across the application
- Handle both string and numeric IDs during lookups
- Ensure consistent structure between test_company and active company

## Troubleshooting

If you encounter issues:

1. **API Connection Problems**: Make sure the API is running on port 8088
2. **Data Not Persisting**: Check that patch_company_db.py has been applied
3. **Frontend Not Connecting**: Verify environment variables in .env.development.local

## Reset to Default

To reset the database to a clean state:

```bash
python -c 'from app.db.simple_mock_db import SimpleMockDatabase; db = SimpleMockDatabase(); db._data["companies"] = {}'
```

Then run the startup scripts again.
