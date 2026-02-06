import streamlit as st
import os
from backend.chat_engine import ChatEngine
from dotenv import load_dotenv
from PIL import Image

# ---------------- CONFIGURATION ----------------
load_dotenv()

st.set_page_config(
    page_title="Remodel AI | Elite Design Concierge",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Premium "Glass-Modern" Dark Theme
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;700&family=Playfair+Display:ital,wght@0,700;1,700&display=swap');

    /* Global */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #020617 100%);
        color: #f8fafc;
    }

    [data-testid="stHeader"] {
        background: rgba(0,0,0,0);
    }

    /* Typography */
    .hero-title {
        font-family: 'Playfair Display', serif;
        font-size: 5rem !important;
        background: linear-gradient(to bottom, #ffffff 0%, #94a3b8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0px !important;
        font-weight: 700;
    }

    .hero-subtitle {
        font-family: 'Outfit', sans-serif;
        text-align: center;
        color: #64748b;
        font-size: 1.2rem;
        letter-spacing: 4px;
        text-transform: uppercase;
        margin-bottom: 3rem;
    }

    /* Layout Containers */
    .main-container {
        max-width: 1200px;
        margin: 0 auto;
    }

    /* Glass Cards */
    .glass-panel {
        background: rgba(255, 255, 255, 0.02);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 30px;
        padding: 40px;
        box-shadow: 0 20px 50px rgba(0,0,0,0.4);
    }

    /* Input Field */
    .stTextInput input {
        background: rgba(15, 23, 42, 0.8) !important;
        border: 2px solid rgba(99, 102, 241, 0.2) !important;
        border-radius: 100px !important;
        color: #f8fafc !important;
        padding: 1.5rem 2.5rem !important;
        font-size: 1.1rem !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .stTextInput input:focus {
        background: rgba(15, 23, 42, 0.9) !important;
        border-color: #6366f1 !important;
        box-shadow: 0 0 40px rgba(99, 102, 241, 0.3);
    }

    /* Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #2563eb 0%, #7c3aed 100%) !important;
        color: white !important;
        border-radius: 100px !important;
        padding: 0.8rem 3rem !important;
        font-weight: 700 !important;
        border: none !important;
        transition: all 0.3s ease !important;
        letter-spacing: 1px;
    }

    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 10px 25px rgba(37, 99, 235, 0.4);
    }

    /* Image Styling */
    .catalog-image {
        border-radius: 20px;
        transition: all 0.5s ease;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }

    .catalog-image:hover {
        transform: scale(1.03);
        box-shadow: 0 15px 30px rgba(0,0,0,0.6);
        border-color: rgba(59, 130, 246, 0.5);
    }

    .image-caption {
        font-family: 'Outfit', sans-serif;
        color: #94a3b8;
        font-size: 0.85rem;
        margin-top: 10px;
        text-align: center;
    }

    /* Badges */
    .status-badge {
        background: rgba(16, 185, 129, 0.1);
        color: #10b981;
        border: 1px solid rgba(16, 185, 129, 0.2);
        padding: 4px 12px;
        border-radius: 100px;
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------- INITIALIZATION ----------------
@st.cache_resource
def get_engine(version="1.2"):
    return ChatEngine()

engine = get_engine("v_strict_db_filter_v2")

# ---------------- HERO SECTION ----------------
st.markdown('<div class="main-container">', unsafe_allow_html=True)
st.markdown('<h1 class="hero-title">Infinia Interior</h1>', unsafe_allow_html=True)
st.markdown('<p class="hero-subtitle">Visual Intelligence & Architectural Discovery</p>', unsafe_allow_html=True)

# Search Logic
col1, col2, col3 = st.columns([1, 4, 1])
with col2:
    query = st.text_input("", placeholder="Explain your design vision... (e.g., 'Modern kitchen with grey cabinets')", label_visibility="collapsed")
    btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 1])
    with btn_col2:
        search_triggered = st.button("DISCOVER")

st.markdown("---")

# ---------------- RESULTS ----------------
if search_triggered or query:
    if query:
        with st.status("Analyzing catalog geometry...", expanded=False) as status:
            try:
                result = engine.ask(query)
                status.update(label="Architectural analysis complete", state="complete")
                
                # Layout
                left_col, right_col = st.columns([1, 1], gap="large")
                
                with left_col:
                    st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
                    st.markdown("### 🔍 AI Analysis")
                    st.write(result["answer"])
                    st.markdown('<br><span class="status-badge">CLIP-MATCHED</span> <span class="status-badge">VECTOR-VERIFIED</span>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with right_col:
                    st.markdown("### 🖼️ Catalog Discoveries")
                    images = result.get("images", [])
                    if images:
                        img_grid = st.columns(2)
                        for i, img_data in enumerate(images[:6]):
                            with img_grid[i % 2]:
                                rel_path = img_data["image_path"]
                                ocr = img_data.get("ocr_text", "")
                                filename = rel_path.split("/")[-1]
                                full_path = os.path.join("Data", "processed", "images", filename)
                                
                                if os.path.exists(full_path):
                                    st.image(full_path, use_container_width=True)
                                    score = img_data.get("score", 0)
                                    status_icon = "🔥" if score > 0.28 else "📎"
                                    ocr = img_data.get("ocr_text", "")
                                    if ocr:
                                        st.markdown(f'<p class="image-caption"><i>"{ocr[:40]}..."</i></p>', unsafe_allow_html=True)
                                    else:
                                        st.markdown(f'<p class="image-caption">Design Ref {i+1}</p>', unsafe_allow_html=True)
                                    pdf_src = str(img_data.get("pdf", "Catalog")).title()
                                    pg_num = img_data.get("page")
                                    pg_str = f"Pg {pg_num}" if pg_num else "Original"
                                    
                                    st.markdown(f'<p style="font-size:0.7rem; color:#94a3b8; text-align:center; margin-bottom:5px;">{pdf_src} • {pg_str} • {score:.2f} {status_icon}</p>', unsafe_allow_html=True)
                                    
                                    pdf_url = img_data.get("pdf_url")
                                    if pdf_url:
                                        st.markdown(f'''
                                            <div style="text-align:center; margin-top:2px;">
                                                <a href="{pdf_url}" target="_blank" 
                                                   style="background:rgba(59, 130, 246, 0.1); color:#60a5fa; border:1px solid rgba(59, 130, 246, 0.3); 
                                                   padding:3px 12px; border-radius:50px; text-decoration:none; font-size:0.65rem; font-weight:bold; 
                                                   display:inline-block; transition:all 0.3s ease;">
                                                   OPEN CATALOG 🔖
                                                </a>
                                            </div>''', unsafe_allow_html=True)
                                    
                                    st.markdown("<br>", unsafe_allow_html=True)
                    else:
                        st.info("The requested design geometry isn't in our immediate focus. Try a broader search.")
                
            except Exception as e:
                st.error(f"Neural linkage error: {e}")
    else:
        st.warning("Please provide a vision to begin discovery.")

st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("<br><br><br>", unsafe_allow_html=True)
st.markdown("<div style='text-align:center; color:#334155; letter-spacing:2px; font-size:0.7rem;'>INFINIA AI // POWERED BY CLIP MODEL // 2026 CATALOG V1</div>", unsafe_allow_html=True)
