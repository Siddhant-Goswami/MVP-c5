"""
Supabase authentication utilities for the AI Newsletter MVP
"""

import streamlit as st
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Supabase client
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

def init_auth():
    """Initialize authentication session state"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'user_email' not in st.session_state:
        st.session_state.user_email = None

def sign_up(email: str, password: str):
    """Sign up a new user"""
    try:
        response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        
        if response.user:
            return {
                "success": True,
                "message": "Account created successfully! Please check your email to verify your account.",
                "user": response.user
            }
        else:
            return {
                "success": False,
                "message": "Failed to create account. Please try again."
            }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error creating account: {str(e)}"
        }

def sign_in(email: str, password: str):
    """Sign in an existing user"""
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        if response.user:
            # Update session state
            st.session_state.authenticated = True
            st.session_state.user = response.user
            st.session_state.user_email = response.user.email
            
            return {
                "success": True,
                "message": "Signed in successfully!",
                "user": response.user
            }
        else:
            return {
                "success": False,
                "message": "Invalid email or password."
            }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error signing in: {str(e)}"
        }

def sign_out():
    """Sign out the current user"""
    try:
        supabase.auth.sign_out()
        # Clear session state
        st.session_state.authenticated = False
        st.session_state.user = None
        st.session_state.user_email = None
        return True
    except Exception as e:
        st.error(f"Error signing out: {str(e)}")
        return False

def reset_password(email: str):
    """Send password reset email"""
    try:
        supabase.auth.reset_password_email(email)
        return {
            "success": True,
            "message": "Password reset email sent! Check your inbox."
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error sending reset email: {str(e)}"
        }

def get_current_user():
    """Get current authenticated user"""
    return st.session_state.user if st.session_state.authenticated else None

def is_authenticated():
    """Check if user is authenticated"""
    return st.session_state.authenticated

def get_user_email():
    """Get current user's email"""
    return st.session_state.user_email if st.session_state.authenticated else None

def handle_auth_state_change():
    """Handle authentication state changes"""
    try:
        # Check if there's a session in the URL (for email verification)
        session = supabase.auth.get_session()
        if session:
            st.session_state.authenticated = True
            st.session_state.user = session.user
            st.session_state.user_email = session.user.email
    except:
        # No valid session found
        pass
