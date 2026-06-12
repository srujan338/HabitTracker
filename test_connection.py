from src.supabase_client import supabase

try:
    # Try to ping the table (doesn't matter if table exists, just checking connectivity)
    response = supabase.table("users").select("count", count="exact").execute()
    print("Connection Successful!")
except Exception as e:
    print(f"Connection Failed: {e}")
