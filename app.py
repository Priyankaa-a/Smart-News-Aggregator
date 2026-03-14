import streamlit as st
from src.db import init_db, add_user, validate_user, store_articles
from src.scraper import scrape_news_by_category
from src.clustering import cluster_articles, get_top_article_per_cluster
from src.summarizer import ArticleSummarizer
import time
import base64

# ========== PAGE CONFIG ==========
st.set_page_config(
    page_title="📰 IntelliDigest",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ========== BACKGROUND IMAGE SETUP ==========
def get_base64_image(image_path):
    """Convert image to base64 for embedding in CSS."""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    except:
        return None

bg_image = get_base64_image("bg.jpg")

# ========== CUSTOM DARK THEME CSS WITH BG IMAGE ==========
if bg_image:
    background_css = f"background: linear-gradient(rgba(0, 26, 77, 0.6), rgba(0, 60, 120, 0.6)), url('data:image/jpeg;base64,{bg_image}') no-repeat center center fixed;"
else:
    background_css = "background: linear-gradient(135deg, #001a4d 0%, #003d7a 50%, #0066cc 100%);"

st.markdown(f"""
<style>
    /* Background */
    .stApp {{
        {background_css}
        background-size: cover;
        background-attachment: fixed;
    }}
    
    body {{
        {background_css}
        background-size: cover;
        background-attachment: fixed;
    }}
    
    /* Main container */
    .main {{
        background: transparent;
    }}
    
    /* Text colors */
    .stMarkdown, .stText, p {{
        color: white;
    }}
    
    h1, h2, h4, h5, h6 {{
        color: white !important;
    }}
    
    /* Header bar & Sidebar */
    [data-testid="stHeader"], [data-testid="collapsedControl"] {{
        background: transparent;
        display: none;
    }}
    
    /* Columns */
    [data-testid="column"] {{
        background: transparent;
    }}

    /* Input fields - White theme inside dark card */
    input[type="text"], input[type="password"], input[type="email"] {{
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #d1d5db !important;
        border-radius: 8px !important;
        padding: 15px 20px !important;
        font-size: 15px !important;
    }}
    
    input[type="text"]::placeholder, input[type="password"]::placeholder, input[type="email"]::placeholder {{
        color: #6b7280 !important;
    }}
    
    input[type="text"]:focus, input[type="password"]:focus, input[type="email"]:focus {{
        background-color: #ffffff !important;
        border-color: #4ade80 !important;
        box-shadow: 0 0 0 2px rgba(74, 222, 128, 0.3) !important;
    }}
    
    /* Primary Buttons (Login/Create Account) */
    button[kind="primary"] {{
        background: #4ade80 !important;
        color: #0f1115 !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 800 !important;
        padding: 12px 24px !important;
        transition: all 0.3s ease !important;
        font-size: 16px !important;
    }}
    
    button[kind="primary"]:hover {{
        background: #22c55e !important;
        transform: translateY(-2px) !important;
    }}

    /* Secondary Buttons (Switch links) */
    button[kind="secondary"] {{
        background: transparent !important;
        color: #bbf7d0 !important;
        border: none !important;
        font-weight: bold !important;
        padding: 0 !important;
        margin-top: -5px !important;
    }}

    button[kind="secondary"]:hover {{
        color: #4ade80 !important;
        text-decoration: underline !important;
    }}

    /* AUTHENTICATION CARD STYLE */
    div[data-testid="column"]:has(.auth-card-marker) {{
        background-color: #0b0e14 !important;
        border: 2px solid #4ade80 !important; 
        border-radius: 16px !important;
        padding: 40px !important;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5), 0 0 15px rgba(74, 222, 128, 0.2) !important;
    }}
    
    /* Selectbox */
    [data-testid="stSelectbox"] {{
        color: white;
    }}
    
    .stSelectbox [data-baseweb="select"] {{
        background-color: rgba(255, 255, 255, 0.1) !important;
    }}
    
    /* Messages & UI Elements */
    .stAlert, .stSuccess {{
        background: rgba(45, 212, 191, 0.2) !important;
        color: #2dd4bf !important;
        border: 1px solid rgba(45, 212, 191, 0.5) !important;
        border-radius: 10px !important;
    }}
    
    .stInfo {{
        background: rgba(102, 204, 255, 0.15) !important;
        color: rgba(255, 255, 255, 0.9) !important;
        border: 1px solid rgba(102, 204, 255, 0.4) !important;
        border-radius: 10px !important;
    }}
    
    .stSpinner {{ color: #2dd4bf !important; }}
    hr {{ border-color: rgba(102, 204, 255, 0.2) !important; margin: 20px 0 !important; }}
    #MainMenu, footer, [data-testid="stDecoration"] {{ display: none; }}
    
    /* SLEEK NAVBAR STYLING */
    .navbar {{
        background: rgba(0, 0, 0, 0.7) !important;
        backdrop-filter: blur(10px) !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
        padding: 15px 50px !important;
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        margin: -100px -100px 30px -100px !important;
        padding-top: 25px !important;
        padding-bottom: 25px !important;
    }}
    
    .navbar-logo {{
        font-size: 28px !important;
        font-weight: 800 !important;
        color: white !important;
        letter-spacing: 1px !important;
    }}
    
    .navbar-buttons {{
        display: flex !important;
        gap: 15px !important;
    }}
    
    .navbar-btn {{
        padding: 10px 24px !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        border: none !important;
        cursor: pointer !important;
        transition: all 0.3s ease !important;
    }}
    
    .navbar-btn-login {{
        background: rgba(74, 222, 128, 0.2) !important;
        color: white !important;
        border: 2px solid rgba(74, 222, 128, 0.5) !important;
    }}
    
    .navbar-btn-login:hover {{
        background: rgba(74, 222, 128, 0.4) !important;
        border-color: #4ade80 !important;
    }}
    
    .navbar-btn-register {{
        background: #4ade80 !important;
        color: #0f1115 !important;
        border: none !important;
    }}
    
    .navbar-btn-register:hover {{
        background: #22c55e !important;
        transform: scale(1.05) !important;
    }}
</style>
""", unsafe_allow_html=True)

# ========== INITIALIZE ==========
init_db()

if 'summarizer' not in st.session_state:
    st.session_state.summarizer = ArticleSummarizer(use_ai=True)

# ========== SESSION STATE ==========
if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "landing"
if "show_login" not in st.session_state:
    st.session_state.show_login = False
if "show_register" not in st.session_state:
    st.session_state.show_register = False
if "show_news" not in st.session_state:
    st.session_state.show_news = False
if "articles" not in st.session_state:
    st.session_state.articles = []
if "selected_category" not in st.session_state:
    st.session_state.selected_category = "Tech"

CATEGORIES = ["Tech", "Political", "Sports", "Economic", "Education", "Major headlines of the day"]

def landing_page():
    """Landing page with sleek black navbar."""
    
    # SLEEK NAVBAR
    st.markdown("""
    <div class="navbar">
        <div style="flex: 1;"></div>
        <div class="navbar-logo">IntelliDigest</div>
        <div style="flex: 1;"></div>
        <div class="navbar-buttons">
    """, unsafe_allow_html=True)
    
    col_login, col_register = st.columns([1, 1])
    with col_login:
        if st.button("Login", key="header_login", use_container_width=True):
            st.session_state.show_login = True
            st.session_state.show_register = False
            st.rerun()
        st.markdown('<style>button:nth-child(1) { background: rgba(74, 222, 128, 0.2) !important; color: white !important; border: 2px solid rgba(74, 222, 128, 0.5) !important; }</style>', unsafe_allow_html=True)
    
    with col_register:
        if st.button("Register", key="header_register", use_container_width=True):
            st.session_state.show_register = True
            st.session_state.show_login = False
            st.rerun()
        st.markdown('<style>button:nth-child(2) { background: #4ade80 !important; color: #0f1115 !important; }</style>', unsafe_allow_html=True)
    
    st.markdown("</div></div>", unsafe_allow_html=True)
    
    # Main content
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([0.2, 1.6, 0.2])
    with col2:
        st.markdown("""
        <div style="background: rgba(0, 0, 0, 0.2); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 20px; padding: 60px 50px; text-align: center;">
            <h1 style="font-size: 48px; color: white; margin-bottom: 20px; font-weight: 700;">Welcome to IntelliDigest</h1>
            <p style="font-size: 16px; color: rgba(255, 255, 255, 0.8); line-height: 1.6; max-width: 800px; margin: 0 auto;">
                Experience the future of news with IntelliDigest. Our advanced AI goes beyond headlines, mathematically clustering global stories 
                to eliminate noise and delivering concise, high-impact summaries. Stop doom-scrolling and start knowing. IntelliDigest: Where 
                machine intelligence meets your daily brief. Your world, decoded and simplified in seconds.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Features
    col_left, col_right = st.columns(2, gap="large")
    with col_left:
        st.markdown("""
        <div style="background: #e9e4cc; border-radius: 20px; padding: 35px; color: #000;">
            <h3 style="text-align: center; margin-top: 0;">📝Features</h3>
            <ul style="list-style: none; padding: 0;text-align: center;">
                <li style="margin: 8px 0;">🖍️ Clustered stories for clarity and focus</li>
                <li style="margin: 8px 0;">✨ Powered by advanced AI models</li>
                <li style="margin: 8px 0;">🔗 Articles from BBC, Reuters, The Guardian & more</li>
                <li style="margin: 8px 0;">🎯 6 news categories</li>
                <li style="margin: 8px 0;">📱 Clean, intuitive interface</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
    with col_right:
        st.markdown("""
        <div style="background: #d4ede4; border-radius: 20px; padding: 35px; color: #000;">
            <h3 style="text-align: center; margin-top: 0;">Discover News Intelligently</h3>
            <p style="text-align: center; margin-bottom: 10px; color: black;">Our platform automatically:</p>
            <ul style="list-style: none; padding: 0;text-align: center;">
                <li style="margin: 8px 0;">🔍 Crawls multiple news sources</li>
                <li style="margin: 8px 0;">🤖 Groups similar articles together</li>
                <li style="margin: 8px 0;">📝 Generates AI-powered summaries</li>
                <li style="margin: 8px 0;">📊 Organizes by category</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

# ========== LOGIN PAGE ==========
def login_page():
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.2, 1])
    
    with col2:
        st.markdown('<div class="auth-card-marker"></div>', unsafe_allow_html=True)
        st.markdown('<h2 style="color: #bbf7d0; text-align: center; font-size: 30px; margin-bottom: 30px; font-weight: bold;">🔐 Welcome Back</h2>', unsafe_allow_html=True)
        
        email = st.text_input("Email", key="login_email", placeholder="📧   Email", label_visibility="collapsed")
        password = st.text_input("Password", type="password", key="login_password", placeholder="🔒   Password", label_visibility="collapsed")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("✅ Login", use_container_width=True, type="primary", key="login_submit"):
            if email and password:
                if validate_user(email, password):
                    st.session_state.user = email
                    st.session_state.show_login = False
                    st.session_state.page = "main"
                    st.rerun()
                else:
                    st.error("❌ Invalid email or password!")
            else:
                st.error("❌ Please fill all fields!")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col_text, col_btn = st.columns([1.5, 1])
        with col_text:
            st.markdown('<p style="text-align: right; color: #9ca3af; font-size: 15px; margin-top: 5px;">Don\'t have an account?</p>', unsafe_allow_html=True)
        with col_btn:
            if st.button("Register", type="secondary", key="switch_to_register"):
                st.session_state.show_login = False
                st.session_state.show_register = True
                st.rerun()

# ========== REGISTER PAGE ==========
def register_page():
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.2, 1])
    
    with col2:
        st.markdown('<div class="auth-card-marker"></div>', unsafe_allow_html=True)
        st.markdown('<h2 style="color: #bbf7d0; text-align: center; font-size: 30px; margin-bottom: 30px; font-weight: bold;">✨ Register Here</h2>', unsafe_allow_html=True)
        
        fullname = st.text_input("Full Name", key="register_fullname", placeholder="👤   Full name", label_visibility="collapsed")
        email = st.text_input("Email", key="register_email", placeholder="📧   Email", label_visibility="collapsed")
        password = st.text_input("Password", type="password", key="register_password", placeholder="🔒   Password", label_visibility="collapsed")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("✅ Create Account", use_container_width=True, type="primary", key="register_submit"):
            if not fullname or not email or not password:
                st.error("❌ Please fill all fields!")
            elif len(password) < 4:
                st.error("❌ Password must be at least 4 characters!")
            elif add_user(email, password):
                st.success("✅ Account created! Please log in.")
                time.sleep(1)
                st.session_state.show_register = False
                st.session_state.show_login = True
                st.rerun()
            else:
                st.error("❌ Email already exists!")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col_text, col_btn = st.columns([1.5, 1])
        with col_text:
            st.markdown('<p style="text-align: right; color: #fbbf24; font-size: 15px; margin-top: 5px;">Already have an account?</p>', unsafe_allow_html=True)
        with col_btn:
            if st.button("Login", type="secondary", key="switch_to_login"):
                st.session_state.show_register = False
                st.session_state.show_login = True
                st.rerun()

# ========== MAIN NEWS PAGE ==========
def main_page():
    """Main news aggregator page."""
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_logo, col_spacer, col_buttons = st.columns([1, 2, 1])
    with col_logo:
        st.markdown(f"### 📰 IntelliDigest")
        st.markdown(f"**{st.session_state.user}**")
    with col_buttons:
        if st.button("🚪 Logout", use_container_width=True, type="primary"):
            st.session_state.user = None
            st.session_state.show_news = False
            st.session_state.articles = []
            st.session_state.show_login = False
            st.session_state.page = "landing"
            st.rerun()
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([2, 1.5, 1])
    with col1:
        st.session_state.selected_category = st.selectbox(
            "📁 Select Category",
            CATEGORIES,
            index=CATEGORIES.index(st.session_state.selected_category)
        )
    with col3:
        st.write("")
        fetch_button = st.button("🔄 Fetch News", use_container_width=True, type="primary")
    
    if fetch_button:
        with st.spinner(f"📥 Fetching news for {st.session_state.selected_category}..."):
            articles = scrape_news_by_category(st.session_state.selected_category)
            if not articles:
                st.error("❌ No articles found. Try another category.")
                return
            st.success(f"✅ Fetched {len(articles)} articles!")
            store_articles(articles)
        
        if len(articles) > 1:
            with st.spinner("🔗 Grouping similar articles..."):
                clustered = cluster_articles(articles)
                top_articles = get_top_article_per_cluster(clustered)
                with st.spinner("🧠 Generating summaries..."):
                    st.session_state.articles = []
                    for cluster_id, article in top_articles.items():
                        summary = st.session_state.summarizer.summarize(article.get('content', ''))
                        article['summary'] = summary
                        st.session_state.articles.append(article)
                    st.success(f"✅ Generated {len(st.session_state.articles)} summaries!")
                    st.session_state.show_news = True
        else:
            with st.spinner("🧠 Generating summary..."):
                summary = st.session_state.summarizer.summarize(articles[0].get('content', ''))
                articles[0]['summary'] = summary
                st.session_state.articles = articles
                st.success("✅ Summary generated!")
                st.session_state.show_news = True
    
    if st.session_state.show_news and st.session_state.articles:
        st.markdown("---")
        st.markdown(f"## 📌 {st.session_state.selected_category} News")
        st.markdown(f"**{len(st.session_state.articles)} article(s) grouped and summarized**")
        st.markdown("")
        
        for idx, article in enumerate(st.session_state.articles, 1):
            with st.container():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"### {idx}. {article.get('headline', 'No Title')}")
                    st.markdown("**📝 AI Summary:**")
                    st.info(article.get('summary', 'No summary available'))
                    col_source, col_link = st.columns(2)
                    with col_source:
                        st.markdown(f"**🔗 Source:** `{article.get('source', 'Unknown')}`")
                    with col_link:
                        if article.get('url'):
                            st.markdown(f"[📄 **Read Full Article**]({article.get('url')})")
                with col2:
                    if article.get('image'):
                        try:
                            st.image(article.get('image'), use_column_width=True)
                        except:
                            st.markdown("📸 *Image unavailable*")
                st.markdown("---")
    elif not st.session_state.show_news:
        st.info("👆 Select a category and click 'Fetch News' to get started!")

# ========== MAIN ROUTING ==========

if st.session_state.user is None:
    if st.session_state.show_login:
        login_page()
    elif st.session_state.show_register:
        register_page()
    else:
        landing_page()
else:
    main_page()