import sys
import traceback

try:
    print("Starting API import test...")
    from app.main import api_app
    print("Import successful!")
    print(f"API app routes: {[route.path for route in api_app.routes]}")
except Exception as e:
    print(f"Error importing API app: {e}")
    traceback.print_exc()
    sys.exit(1)

print("API import test completed successfully.")
