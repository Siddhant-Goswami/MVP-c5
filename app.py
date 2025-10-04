import streamlit as st
import streamlit_shadcn_ui as ui
from config.sources import NEWS_SOURCES
from utils.database import save_preferences
from utils.scraper import scrape_sources
from utils.ai_curator import curate_newsletter
from utils.email_sender import send_newsletter


st.set_page_config(page_title="AI Newsletter MVP", page_icon="📰", layout="wide")

st.title("📰 Your Personalized AI Newsletter")
st.caption("Get curated AI insights delivered to your inbox every morning")

# Step 1: Topic Selection
st.subheader("1. Choose Your Topics")
selected_categories = ui.tabs(
    options=list(NEWS_SOURCES.keys()), 
    default_value='AI', 
    key="topic_tabs"
)

st.write(f"You selected: {selected_categories}")

# Step 2: Email Input
st.subheader("2. Enter Your Email")
user_email = ui.input(
    default_value="", 
    type="email",
    placeholder="your@email.com",
    key="email_input"
)

# Step 3: Generate Button
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


