# AI Marketing Agent

This application helps automate marketing material generation using AI tools.

## ⚠️ Important Port Configuration

> **Critical:** The API server must run on port 8088 to work properly with the frontend.

To ensure everything works correctly:
- Use the quick-start script: `./start-with-correct-ports.sh`
- Or run manually: `uvicorn app.main:app --host 127.0.0.1 --port 8088 --reload`
- **Do not use port 8089** (previously documented incorrectly)

If you experience connection issues:
1. Run VS Code task "Check API Connection" or `./check_api_connection.sh`
2. Run VS Code task "Fix API Port Issues" or `./fix_api_server_port.sh` 
3. See [PORT_CONFIGURATION.md](PORT_CONFIGURATION.md) for detailed troubleshooting

## Corporate Environment Setup

If you're working in a corporate environment with proxy restrictions, use our special corporate startup script:

```bash
./start-corporate.sh
```

This script:
- Bypasses proxy settings for localhost connections
- Uses direct 127.0.0.1 connections instead of 0.0.0.0
- Sets up the frontend to connect to the correct API URL
- Provides detailed logs for troubleshooting

After running the script:
1. Access the frontend directly at: http://127.0.0.1:3900
2. Access the API docs directly at: http://127.0.0.1:9000/docs

## Database Setup

**⚠️ Important:** This application uses **MongoDB** as its primary database. The mock database system has been removed as of January 2025.

### Prerequisites

You need MongoDB installed and running on your system.

#### Install MongoDB

**Ubuntu/WSL:**
```bash
sudo apt-get update
sudo apt-get install -y mongodb
sudo service mongodb start
```

**macOS:**
```bash
brew install mongodb-community
brew services start mongodb-community
```

**Windows:**
- Download from [mongodb.com](https://www.mongodb.com/try/download/community)
- Install and start the MongoDB service

#### Verify MongoDB is Running

```bash
mongo --eval "db.version()"
```

### Initial Setup

1. **Start MongoDB:**
```bash
sudo service mongodb start  # Linux/WSL
brew services start mongodb-community  # macOS
```

2. **Run Migration Script** (first time only):
```bash
python scripts/migrate_to_mongodb.py
```

This will:
- Connect to MongoDB
- Create the `ai_marketing_agent` database
- Set up collections: users, companies, ai_providers, materials
- Create performance indexes
- Load initial test data (1 user, 1 company, 9 AI providers)

3. **Start the Application:**
```bash
uvicorn app.main:api_app --host 127.0.0.1 --port 8088 --reload
```

Or use VS Code task: "Run API (Mock Database)"

### Environment Configuration

Create a `.env` file (or update existing one):
```bash
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB=ai_marketing_agent
```

### Documentation

For detailed MongoDB architecture documentation, see:
- **Architecture Overview:** [docs/MONGODB_ARCHITECTURE.md](docs/MONGODB_ARCHITECTURE.md)
- **Migration Summary:** [docs/MIGRATION_SUMMARY.md](docs/MIGRATION_SUMMARY.md)
- **Cleanup Summary:** [docs/CLEANUP_SUMMARY.md](docs/CLEANUP_SUMMARY.md)

## Development Workflow

For the best development experience:

1. **Ensure MongoDB is Running:**
   ```bash
   sudo service mongodb status  # Linux/WSL
   brew services list | grep mongodb  # macOS
   ```

2. **Start the API:**
   - VS Code: Run task "Run API (Mock Database)"
   - Terminal: `uvicorn app.main:api_app --host 127.0.0.1 --port 8088 --reload`

3. **Start the Frontend:**
   - VS Code: Run task "Run Frontend (Dev)"
   - Terminal: `cd frontend && npm run dev`

4. **Access the Application:**
   - API: http://127.0.0.1:8088
   - API Docs: http://127.0.0.1:8088/docs
   - Frontend: http://127.0.0.1:3001

## Test User Credentials

The migration script creates a default test user:
- Email: demo@example.com
- Password: demo123

You can verify the user was created:
```bash
mongo ai_marketing_agent --eval "db.users.find().pretty()"
```
