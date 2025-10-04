import streamlit as st
import streamlit_shadcn_ui as ui
from config.sources import NEWS_SOURCES
from utils.database import save_preferences
from utils.scraper import scrape_sources
from utils.ai_curator import curate_newsletter
from utils.email_sender import send_newsletter
from utils.auth import (
    init_auth, sign_up, sign_in, sign_out, reset_password,
    get_current_user, is_authenticated, get_user_email, handle_auth_state_change
)


st.set_page_config(page_title="AI Newsletter MVP", page_icon="📰", layout="wide")

# Initialize authentication
init_auth()
handle_auth_state_change()

def show_auth_page():
    """Show authentication page"""
    st.title("📰 AI Newsletter MVP")
    st.caption("Get curated AI insights delivered to your inbox every morning")
    
    # Authentication tabs
    auth_tab, signup_tab = st.tabs(["Sign In", "Sign Up"])
    
    with auth_tab:
        st.subheader("Sign In")
        with st.form("signin_form"):
            email = st.text_input("Email", placeholder="your@email.com")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Sign In")
            
            if submit:
                if email and password:
                    result = sign_in(email, password)
                    if result["success"]:
                        st.success(result["message"])
                        st.rerun()
                    else:
                        st.error(result["message"])
                else:
                    st.error("Please fill in all fields")
        
        # Password reset
        if st.button("Forgot Password?"):
            reset_email = st.text_input("Enter your email for password reset", placeholder="your@email.com")
            if reset_email:
                result = reset_password(reset_email)
                if result["success"]:
                    st.success(result["message"])
                else:
                    st.error(result["message"])
    
    with signup_tab:
        st.subheader("Sign Up")
        with st.form("signup_form"):
            new_email = st.text_input("Email", placeholder="your@email.com", key="signup_email")
            new_password = st.text_input("Password", type="password", key="signup_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm")
            submit_signup = st.form_submit_button("Sign Up")
            
            if submit_signup:
                if new_email and new_password and confirm_password:
                    if new_password == confirm_password:
                        if len(new_password) >= 6:
                            result = sign_up(new_email, new_password)
                            if result["success"]:
                                st.success(result["message"])
                            else:
                                st.error(result["message"])
                        else:
                            st.error("Password must be at least 6 characters long")
                    else:
                        st.error("Passwords do not match")
                else:
                    st.error("Please fill in all fields")

def show_main_app():
    """Show main newsletter application"""
    user = get_current_user()
    user_email = get_user_email()
    
    # Header with user info and sign out
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("📰 Your Personalized AI Newsletter")
        st.caption(f"Welcome back, {user_email}!")
    with col2:
        if st.button("Sign Out", type="secondary"):
            sign_out()
            st.rerun()
    
    # Step 1: Topic Selection
    st.subheader("1. Choose Your Topics")
    selected_categories = ui.tabs(
        options=list(NEWS_SOURCES.keys()), 
        default_value='AI', 
        key="topic_tabs"
    )
    
    st.write(f"You selected: {selected_categories}")
    
    # Step 2: Generate Button (email is automatically user's email)
    if ui.button("Generate My Newsletter", key="generate_btn"):
        with st.spinner("🔍 Scraping sources..."):
            articles = scrape_sources(selected_categories)
        
        with st.spinner("🤖 AI is curating your newsletter..."):
            newsletter_content = curate_newsletter(articles, [selected_categories])
        
        with st.spinner("📧 Sending email..."):
            save_preferences(user_email, [selected_categories])
            send_newsletter(user_email, newsletter_content)
        
        st.success("✅ Newsletter sent! Check your inbox.")
        st.markdown("### Preview:")
        st.markdown(newsletter_content)

# Main app logic
if is_authenticated():
    show_main_app()
else:
    show_auth_page()


