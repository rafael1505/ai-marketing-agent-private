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

## Database Setup Options

Due to certificate verification issues with Docker in corporate environments, we've provided multiple ways to set up the database for development:

### Option 1: Use the Mock Database (No MongoDB Required)

The application has been configured to use a mock database if MongoDB is unavailable. This is perfect for development and testing:

1. Start the application:
```bash
./start-dev.sh
```

Or use the VS Code task:
- Press `F1`, type "Tasks: Run Task", select "Run API (Mock Database)"

### Option 2: Install MongoDB Locally

For a full setup with a real MongoDB database:

1. Run the setup script:
```bash
./setup-local-db.sh
```

This script will:
- Check if MongoDB is installed
- Help you install MongoDB if needed
- Create the required database and collections
- Set up a test user account

2. Start the application:
```bash
./start-dev.sh
```

### Option 3: Docker Setup (If Docker Registry Access Is Fixed)

If your corporate certificate issues with Docker are resolved:

1. Start Docker:
```bash
sudo systemctl start docker
```

2. Run the application with Docker Compose:
```bash
docker compose up -d
```

## Development Workflow

For the best development experience:

1. Start the API:
   - VS Code: Run task "Run API (Mock Database)"
   - Terminal: `./start-dev.sh` 

2. Start the Frontend:
   - VS Code: Run task "Run Frontend (Dev)"
   - Terminal: `cd frontend && npm run dev`

3. Access the application:
   - API: http://localhost:8000
   - Frontend: http://localhost:3001

## Test User Credentials

When using the mock database or local MongoDB setup:
- Email: test@example.com
- Password: password
