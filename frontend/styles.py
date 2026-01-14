import streamlit as st

def apply_custom_styles(mode="Light"):
    """
    Injects CSS variables based on the selected theme (Light/Dark).
    """
    
    # --- COLOR PALETTES ---
    if mode == "Dark":
        # Cyberpunk / Engineering Dark
        colors = {
            "bg_main": "#0e1117",
            "bg_panel": "#161b22",
            "sidebar_bg": "#010409",
            "text_primary": "#e6edf3",      # High contrast white
            "text_secondary": "#8b949e",    # Soft grey
            "border_color": "#30363d",
            "accent_primary": "#1f6feb", 
            "input_bg": "#0d1117",          # Very dark for inputs
            "table_header_bg": "#21262d",   # Darker grey for table headers
            "table_border": "#30363d",
            "button_bg": "#21262d"          # Dark button background
        }
    else:
        # Precision Light (Default)
        colors = {
            "bg_main": "#f4f5f7",
            "bg_panel": "#ffffff",
            "sidebar_bg": "#091e42",
            "text_primary": "#172b4d",
            "text_secondary": "#5e6c84",
            "border_color": "#dfe1e6",
            "accent_primary": "#0052cc",
            "input_bg": "#ffffff",
            "table_header_bg": "#f4f5f7",
            "table_border": "#dfe1e6",
            "button_bg": "#ffffff"
        }

    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&family=JetBrains+Mono:wght@400;700&display=swap');

        /* --- DYNAMIC VARIABLES --- */
        :root {{
            --bg-main: {colors['bg_main']};
            --bg-panel: {colors['bg_panel']};
            --sidebar-bg: {colors['sidebar_bg']};
            --text-primary: {colors['text_primary']};
            --text-secondary: {colors['text_secondary']};
            --border-color: {colors['border_color']};
            --accent: {colors['accent_primary']};
            --input-bg: {colors['input_bg']};
            --table-header-bg: {colors['table_header_bg']};
            --table-border: {colors['table_border']};
            --button-bg: {colors['button_bg']};
        }}

        /* --- GLOBAL --- */
        .stApp {{
            background-color: var(--bg-main);
            color: var(--text-primary);
            font-family: 'Inter', sans-serif;
        }}
        
        /* --- SIDEBAR --- */
        section[data-testid="stSidebar"] {{
            background-color: var(--sidebar-bg);
        }}
        section[data-testid="stSidebar"] h1, 
        section[data-testid="stSidebar"] h2, 
        section[data-testid="stSidebar"] h3, 
        section[data-testid="stSidebar"] label, 
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] span,
        section[data-testid="stSidebar"] .stMarkdown {{
            color: #c9d1d9 !important; /* Always light text in sidebar */
        }}

        /* --- HEADERS --- */
        h1, h2, h3, h4, h5, h6 {{
            color: var(--text-primary) !important;
        }}
        h1 {{
            font-family: 'Inter', sans-serif;
            font-weight: 800;
            letter-spacing: -0.5px;
            text-transform: uppercase;
            text-align: center;
        }}
        h3 {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 1rem;
            text-transform: uppercase;
            letter-spacing: 2px;
            text-align: center;
        }}

        /* --- BUTTONS (FIX FOR DARK MODE VISIBILITY) --- */
        div.stButton > button, div.stDownloadButton > button {{
            background-color: var(--button-bg) !important;
            color: var(--text-primary) !important;
            border: 1px solid var(--border-color) !important;
        }}
        div.stButton > button:hover, div.stDownloadButton > button:hover {{
            border-color: var(--accent) !important;
            color: var(--accent) !important;
        }}
        /* Primary Buttons (Like 'New Inspection') */
        button[kind="primary"] {{
            background-color: var(--accent) !important;
            color: white !important;
            border: none !important;
        }}

        /* --- PANELS & CHAT --- */
        div[data-testid="stFileUploader"] {{
            background-color: var(--bg-panel);
            border: 2px dashed var(--accent);
            border-radius: 8px;
            padding: 30px;
        }}
        
        /* Chat Input Field */
        .stChatInputContainer textarea {{
            background-color: var(--input-bg) !important;
            color: var(--text-primary) !important;
            border: 1px solid var(--border-color) !important;
        }}
        
        /* Message Bubbles */
        div[data-testid="stChatMessage"] {{
            background-color: var(--bg-panel);
            border: 1px solid var(--border-color);
        }}
        div[data-testid="stChatMessage"] p {{
            color: var(--text-primary) !important;
        }}
        div[data-testid="stMarkdownContainer"] p {{
            color: var(--text-primary) !important;
        }}
        div[data-testid="stMarkdownContainer"] li {{
            color: var(--text-primary) !important;
        }}
        div[data-testid="stMarkdownContainer"] strong {{
            color: var(--text-primary) !important;
            font-weight: 700;
        }}

        /* --- TABLES --- */
        div[data-testid="stMarkdownContainer"] table {{
            color: var(--text-primary) !important;
            border-color: var(--table-border) !important;
            width: 100%;
        }}
        div[data-testid="stMarkdownContainer"] th {{
            background-color: var(--table-header-bg) !important;
            color: var(--text-primary) !important;
            border-bottom: 1px solid var(--table-border) !important;
            font-weight: 600;
        }}
        div[data-testid="stMarkdownContainer"] td {{
            color: var(--text-primary) !important;
            border-bottom: 1px solid var(--table-border) !important;
        }}
        div[data-testid="stMarkdownContainer"] tr {{
            background-color: transparent !important;
        }}

        /* --- METRICS PILLS --- */
        .tech-pill {{
            background: var(--bg-main);
            color: var(--text-secondary);
            border: 1px solid var(--border-color);
            padding: 2px 8px;
            border-radius: 4px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.75rem;
            display: inline-block;
            margin-right: 8px;
        }}
    </style>
    """, unsafe_allow_html=True)