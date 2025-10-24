# Obsolete Mock Database Scripts

**Status:** ⚠️ ARCHIVED - DO NOT USE  
**Date Archived:** January 2025  
**Reason:** Migration from SimpleMockDatabase to real MongoDB completed

---

## What's in This Directory

This directory contains test, debug, and utility scripts that were used with the **obsolete SimpleMockDatabase** system. These scripts are no longer functional and have been archived for historical reference only.

### Files Archived

1. **startup_server.py** - Old server startup script with SimpleMockDatabase initialization
2. **verify_persistence_fix.py** - Verification script for JSON file persistence
3. **verify_company_persistence.py** - Company data persistence tests
4. **test_database_setup.py** - Database setup tests for mock DB
5. **simple_db_test.py** - Simple mock database functionality tests
6. **simple_company_fix.py** - Company data fix script for mock DB
7. **verify_persistence_verification.py** - Additional persistence verification

### Why These Are Obsolete

**The SimpleMockDatabase system has been completely removed** and replaced with **real MongoDB**. This migration was necessary because:

1. SimpleMockDatabase used in-memory dictionaries with JSON file persistence
2. It violated the business rule requiring "database-driven" architecture
3. Manual `save_collection()` calls were error-prone
4. No proper indexing or query optimization
5. Not production-ready

### What Replaced It

- **MongoDB Connection:** `app/db/mongodb.py`
- **Migration Script:** `scripts/migrate_to_mongodb.py`
- **Architecture Docs:** `docs/MONGODB_ARCHITECTURE.md`
- **Migration Summary:** `docs/MIGRATION_SUMMARY.md`

### If You Need to Reference These Scripts

**DO NOT RUN THEM** - They will fail because:
- `app/db/simple_mock_db.py` has been deleted
- `app/core/persistence_patch.py` has been deleted
- `app/db/data/*.json` files have been deleted
- All data has been migrated to MongoDB

**Instead:**
- Use `scripts/migrate_to_mongodb.py` for data migration
- Use MongoDB queries directly: `mongo ai_marketing_agent`
- Use Python scripts with `app/db/mongodb.py` connection

---

## Migration Details

**Data Migrated:**
- 1 user → `users` collection
- 1 company → `companies` collection
- 9 AI providers → `ai_providers` collection

**Indexes Created:**
- `users.email` (unique)
- `ai_providers(user_id, id)` (composite unique)
- `companies.user_id`
- `ai_providers.isActive`

**Verification:**
```bash
mongo ai_marketing_agent
> db.users.count()
1
> db.companies.count()
1
> db.ai_providers.count()
9
```

---

## For Historical Reference Only

If you absolutely need to understand what these scripts did, they demonstrate:
- How SimpleMockDatabase worked (in-memory + JSON persistence)
- How persistence patches applied auto-save functionality
- How test data was created and managed
- The pain points that led to the MongoDB migration

**Do not attempt to resurrect this system.** Use real MongoDB instead.

---

**Last Updated:** January 2025  
**Migration Status:** ✅ Complete  
**These Scripts:** ⚠️ Obsolete and Non-Functional
