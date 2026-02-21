# save as check_routes.py
from thor_engine import app

print("📋 All registered routes:")
for route in app.routes:
    print(f"   {route.methods} - {route.path}")
