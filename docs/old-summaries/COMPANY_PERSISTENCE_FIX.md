# Company Data Persistence Fix Guide

## Problem Summary

The AI Marketing Agent application was experiencing an issue where company information (such as logo and brand colors) could be saved without errors, but when navigating away from the company settings page and returning, the changes wouldn't persist - the default information would be displayed instead. This was due to the following issues:

1. **In-Memory Database**: The `SimpleMockDatabase` used for development stored all data in memory, which was lost when the API server restarted.
2. **Missing Persistence Layer**: There was no mechanism to save the database state to disk.
3. **FormData Array Handling**: The frontend sent `brand_colors` as array elements (`brand_colors[0]`, `brand_colors[1]`, etc.), which may have been parsed incorrectly by the API.
4. **Inconsistent ID Handling**: The company could be referred to by both numeric ID (`2`) and string ID (`test_company`).

## Solution Implemented

We've implemented a comprehensive fix with the following components:

### 1. Database Persistence Enhancement

The `SimpleMockDatabase` class was enhanced to persist data to disk:

- Added a persistence layer that saves company data to JSON files in the `app/db/data` directory
- Implemented automatic loading of data from disk at startup
- Added backup mechanism that creates timestamped backups in `app/db/data/backups` before each write

### 2. Company ID Standardization

- Ensured that the company is always accessed using the string ID `"test_company"`
- Fixed the database ID lookup to handle both string IDs and ObjectIDs
- Added special handling for the test company in the `CompanyDB` class

### 3. Automatic Integration

- The persistence patch is automatically applied when the API server starts
- No manual intervention is required to maintain persistence between restarts

## Using the Fix

The fix is automatically applied when the application starts. However, there are a few things to know:

### When Starting from Scratch

If you're starting with a fresh database (no previous data), the application will:

1. Create an empty in-memory database
2. Create default company data if none exists
3. Save this data to disk for future use

### After a Server Restart

When the API server restarts:

1. The persistence patch is automatically applied
2. The application loads any existing company data from disk
3. Normal operations continue with the loaded data

### Manual Data Recovery (if needed)

If you ever need to manually recover or inspect the database:

1. Check the JSON files in the `app/db/data` directory
2. Use the `fix_persistence.py` script to rebuild or repair the database
3. Backups are stored in `app/db/data/backups` with timestamps

## Technical Details

### Files Modified/Added:

1. **Added `app/core/persistence_patch.py`**
   - Contains the monkey patching logic to add persistence to `SimpleMockDatabase`

2. **Modified `app/main.py`**
   - Imports and applies the persistence patch at startup

3. **Added Helper Scripts**
   - `fix_persistence.py`: Manual application of the persistence fix
   - `create_test_company.py`: Creates/updates the test company
   - `direct_db_check.py`: Direct inspection of database files
   - `debug_company_api.py`: For testing API endpoints with proper authentication

### Data Flow:

1. Frontend sends company update request with FormData
2. API processes the request and updates the in-memory database
3. Enhanced database methods automatically persist changes to disk
4. When the API restarts, it loads data from disk

## Troubleshooting

If you encounter issues with company data persistence:

1. **Check if the API server is running**
   ```bash
   ss -tulnp | grep 8088
   ```

2. **Ensure the database directory exists and is writable**
   ```bash
   ls -la app/db/data/
   ```

3. **Manually run the persistence fix script**
   ```bash
   python fix_persistence.py
   ```

4. **Check the API logs for persistence-related messages**
   ```bash
   grep -i "persistence" api_server.log
   ```

5. **Test the company API directly**
   ```bash
   python debug_company_api.py
   ```

## Testing the Fix

We've created scripts to verify the company persistence fix:

1. **Basic Database Test**:
   ```bash
   python direct_db_check.py
   ```

2. **Apply Persistence Fix**:
   ```bash
   python fix_persistence.py
   ```

3. **Create Test Company**:
   ```bash
   python create_test_company.py
   ```

4. **Debug API Connection**:
   ```bash
   python debug_company_api.py
   ```

---

*This fix resolves the issue of company data not persisting between API server restarts and ensures that the company settings page properly displays the saved information.*
