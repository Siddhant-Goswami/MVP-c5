from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

def save_preferences(email: str, topics: list):
    """Save or update user preferences"""
    try:
        # First check if the email exists
        existing = supabase.table('user_preference').select('id').eq('email', email).execute()
        
        if existing.data:
            # Update existing record
            data = supabase.table('user_preference').update({
                'topics': topics
            }).eq('email', email).execute()
        else:
            # Insert new record
            data = supabase.table('user_preference').insert({
                'email': email,
                'topics': topics
            }).execute()
        
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def get_preferences(email: str):
    """Get user preferences by email"""
    try:
        response = supabase.table('user_preference')\
            .select("*")\
            .eq('email', email)\
            .execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error: {e}")
        return None