import streamlit as st


def apply_styles():
    st.markdown(
        """
        <style>
        /* Import premium Google Font */
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

        :root {
            --bg-base: #060913;
            --glass-bg: rgba(17, 25, 40, 0.65);
            --glass-border: rgba(255, 255, 255, 0.08);
            --glass-highlight: rgba(255, 255, 255, 0.12);
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --accent-primary: #3b82f6;
            --accent-glow: #60a5fa;
            --cyan-accent: #06b6d4;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --radius-lg: 16px;
            --radius-md: 12px;
        }

        /* Ambient animated background */
        .stApp {
            background-color: var(--bg-base);
            background-image: 
                radial-gradient(at 0% 0%, rgba(59, 130, 246, 0.15) 0px, transparent 50%),
                radial-gradient(at 100% 0%, rgba(6, 182, 212, 0.15) 0px, transparent 50%),
                radial-gradient(at 100% 100%, rgba(139, 92, 246, 0.1) 0px, transparent 50%);
            background-attachment: fixed;
            color: var(--text-main);
            font-family: 'Outfit', sans-serif !important;
        }

        /* Force Google Font everywhere */
        html, body, [class*="css"] {
            font-family: 'Outfit', sans-serif !important;
        }

        .block-container {
            max-width: 1100px;
            padding-top: 3rem;
            padding-bottom: 4rem;
        }

        /* Hide default Streamlit headers to look like a real web app */
        header[data-testid="stHeader"] {
            background: transparent !important;
            box-shadow: none !important;
        }

        h1, h2, h3 {
            font-weight: 700 !important;
            letter-spacing: -0.02em !important;
        }

        h1 {
            font-size: clamp(2.5rem, 5vw, 4rem) !important;
            background: linear-gradient(135deg, #ffffff 0%, #a8b2d1 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }

        /* Hero Section with Glassmorphism */
        .app-hero {
            display: grid;
            grid-template-columns: 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }
        
        @media (min-width: 850px) {
            .app-hero {
                grid-template-columns: 1.5fr 1fr;
            }
        }

        .hero-copy, .hero-panel {
            background: var(--glass-bg);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid var(--glass-border);
            border-radius: var(--radius-lg);
            padding: 32px;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.3);
            transition: transform 0.3s ease, border-color 0.3s ease;
        }

        .hero-copy:hover {
            border-color: var(--glass-highlight);
            transform: translateY(-2px);
        }

        .eyebrow {
            color: var(--cyan-accent);
            font-size: 0.85rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-bottom: 12px;
            display: inline-block;
            background: rgba(6, 182, 212, 0.1);
            padding: 4px 12px;
            border-radius: 20px;
            border: 1px solid rgba(6, 182, 212, 0.2);
        }

        .hero-copy p {
            color: var(--text-muted);
            font-size: 1.1rem;
            line-height: 1.6;
            margin-top: 16px;
        }

        .hero-panel {
            display: flex;
            flex-direction: column;
            justify-content: center;
            gap: 16px;
        }

        .hero-stat {
            display: flex;
            align-items: center;
            gap: 16px;
            padding-bottom: 16px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }

        .hero-stat:last-child {
            border-bottom: none;
            padding-bottom: 0;
        }

        .stat-value {
            font-size: 1.5rem;
            font-weight: 800;
            color: var(--text-main);
            background: linear-gradient(135deg, var(--accent-glow), var(--cyan-accent));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .stat-label {
            color: var(--text-muted);
            font-size: 0.9rem;
            font-weight: 500;
        }

        /* File Uploader override */
        [data-testid="stFileUploader"] {
            background: var(--glass-bg);
            backdrop-filter: blur(12px);
            border: 1px dashed var(--accent-primary);
            border-radius: var(--radius-lg);
            padding: 24px;
            transition: all 0.3s ease;
        }

        [data-testid="stFileUploader"]:hover {
            border-color: var(--accent-glow);
            box-shadow: 0 0 20px rgba(59, 130, 246, 0.2);
            background: rgba(17, 25, 40, 0.8);
        }

        /* Buttons */
        .stButton > button, .stDownloadButton > button {
            background: linear-gradient(135deg, #2563eb, #06b6d4) !important;
            color: white !important;
            border: none !important;
            border-radius: var(--radius-md) !important;
            font-weight: 600 !important;
            font-size: 1.05rem !important;
            padding: 0.75rem 1.5rem !important;
            height: auto !important;
            box-shadow: 0 4px 15px rgba(37, 99, 235, 0.4) !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }

        .stButton > button:hover, .stDownloadButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 25px rgba(37, 99, 235, 0.6) !important;
            filter: brightness(1.1) !important;
        }

        /* Video element */
        [data-testid="stVideo"] {
            border-radius: var(--radius-md);
            overflow: hidden;
            border: 1px solid var(--glass-border);
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
        }

        /* Custom Section Labels */
        .section-label {
            display: flex;
            align-items: center;
            gap: 10px;
            color: var(--text-muted);
            font-size: 0.9rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin: 40px 0 16px;
        }
        
        .section-label::after {
            content: "";
            flex: 1;
            height: 1px;
            background: linear-gradient(90deg, var(--glass-border), transparent);
        }

        /* AI Coach Card */
        .coach-card {
            background: linear-gradient(145deg, rgba(30, 41, 59, 0.7), rgba(15, 23, 42, 0.7));
            backdrop-filter: blur(16px);
            border: 1px solid var(--glass-border);
            border-left: 4px solid var(--accent-glow);
            border-radius: var(--radius-lg);
            padding: 28px;
            margin: 20px 0;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            position: relative;
            overflow: hidden;
        }
        
        /* Subtle glow effect behind the coach card */
        .coach-card::before {
            content: '';
            position: absolute;
            top: -50px;
            right: -50px;
            width: 150px;
            height: 150px;
            background: var(--accent-glow);
            filter: blur(80px);
            opacity: 0.15;
            border-radius: 50%;
            pointer-events: none;
        }

        .coach-header {
            display: flex;
            align-items: center;
            gap: 16px;
            margin-bottom: 20px;
        }

        .coach-avatar {
            width: 48px;
            height: 48px;
            border-radius: 12px;
            background: linear-gradient(135deg, #3b82f6, #8b5cf6);
            color: white;
            display: grid;
            place-items: center;
            font-size: 20px;
            font-weight: 800;
            box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);
        }

        .coach-title {
            font-size: 1.2rem;
            font-weight: 700;
            color: white;
            margin: 0;
        }

        .coach-subtitle {
            font-size: 0.8rem;
            color: var(--accent-glow);
            font-weight: 600;
        }

        .coach-feedback {
            font-size: 1.05rem;
            line-height: 1.7;
            color: #cbd5e1;
            font-style: italic;
        }

        /* Metrics Grid */
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 16px;
        }

        .metric-item {
            background: var(--glass-bg);
            backdrop-filter: blur(12px);
            border: 1px solid var(--glass-border);
            border-radius: var(--radius-md);
            padding: 24px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        .metric-item:hover {
            border-color: var(--glass-highlight);
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4);
        }

        .metric-label {
            font-size: 0.8rem;
            color: var(--text-muted);
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 12px;
        }

        .metric-value {
            font-size: 2.2rem;
            font-weight: 800;
            color: white;
            margin-bottom: 16px;
        }

        .metric-status {
            align-self: flex-start;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        .status-optimal {
            background: rgba(16, 185, 129, 0.15);
            color: #34d399;
            border: 1px solid rgba(16, 185, 129, 0.3);
        }

        .status-deviation {
            background: rgba(239, 68, 68, 0.15);
            color: #f87171;
            border: 1px solid rgba(239, 68, 68, 0.3);
        }

        .status-info {
            background: rgba(59, 130, 246, 0.15);
            color: #60a5fa;
            border: 1px solid rgba(59, 130, 246, 0.3);
        }

        /* Fancy Loader */
        .loading-container {
            background: var(--glass-bg);
            backdrop-filter: blur(16px);
            border: 1px solid var(--glass-border);
            border-radius: var(--radius-lg);
            padding: 40px;
            text-align: center;
            margin: 30px 0;
            position: relative;
            overflow: hidden;
        }

        .loading-pulse {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: linear-gradient(135deg, var(--accent-primary), var(--cyan-accent));
            margin: 0 auto 24px;
            animation: pulse-glow 1.5s ease-in-out infinite alternate;
        }

        @keyframes pulse-glow {
            0% { transform: scale(0.9); box-shadow: 0 0 10px rgba(59, 130, 246, 0.5); }
            100% { transform: scale(1.1); box-shadow: 0 0 30px rgba(6, 182, 212, 0.8); }
        }

        .loading-text {
            color: white;
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 8px;
        }

        .loading-subtext {
            color: var(--accent-glow);
            font-size: 0.85rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.1em;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
