import streamlit as st


def apply_styles():
    st.markdown(
        """
        <style>
        :root {
            --bg: #090d14;
            --panel: #101622;
            --panel-soft: #151c2a;
            --panel-lift: #1a2232;
            --line: rgba(148, 163, 184, 0.18);
            --text: #f8fafc;
            --muted: #94a3b8;
            --muted-strong: #cbd5e1;
            --cyan: #18e6c4;
            --blue: #4f8cff;
            --orange: #f59e0b;
            --red: #fb7185;
            --green: #34d399;
            --radius: 8px;
        }

        .stApp {
            background: linear-gradient(145deg, #070a10 0%, #0d1118 48%, #16181f 100%);
            color: var(--text);
        }

        .block-container {
            max-width: 1180px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        header[data-testid="stHeader"] {
            background: transparent;
        }

        [data-testid="stToolbar"] {
            right: 1rem;
        }

        h1, h2, h3 {
            color: var(--text);
            letter-spacing: 0;
        }

        h1 {
            font-size: clamp(2.2rem, 5vw, 4rem);
            line-height: 1;
            margin-bottom: 0.6rem;
        }

        h2, h3 {
            margin-top: 1.8rem;
        }

        p, label, span, div {
            letter-spacing: 0;
        }

        .app-hero {
            display: grid;
            grid-template-columns: 1.35fr 0.65fr;
            gap: 18px;
            align-items: stretch;
            margin-bottom: 22px;
        }

        .hero-copy {
            border: 1px solid var(--line);
            border-radius: var(--radius);
            background: linear-gradient(135deg, rgba(16, 22, 34, 0.92), rgba(12, 17, 26, 0.92));
            padding: 28px;
            box-shadow: 0 18px 60px rgba(0, 0, 0, 0.28);
        }

        .eyebrow {
            color: var(--cyan);
            font-size: 0.78rem;
            font-weight: 800;
            text-transform: uppercase;
            margin-bottom: 12px;
        }

        .hero-copy h1 {
            margin: 0;
        }

        .hero-copy p {
            color: var(--muted-strong);
            font-size: 1.03rem;
            line-height: 1.65;
            max-width: 760px;
            margin: 14px 0 0;
        }

        .hero-panel {
            border: 1px solid var(--line);
            border-radius: var(--radius);
            background: linear-gradient(180deg, rgba(26, 34, 50, 0.96), rgba(13, 19, 29, 0.96));
            padding: 20px;
            display: grid;
            align-content: center;
            gap: 14px;
        }

        .hero-stat {
            border-bottom: 1px solid var(--line);
            padding-bottom: 12px;
        }

        .hero-stat:last-child {
            border-bottom: 0;
            padding-bottom: 0;
        }

        .stat-value {
            color: var(--text);
            font-size: 1.45rem;
            font-weight: 850;
        }

        .stat-label {
            color: var(--muted);
            font-size: 0.78rem;
            font-weight: 700;
            text-transform: uppercase;
            margin-top: 4px;
        }

        .workflow {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 12px;
            margin-bottom: 24px;
        }

        .workflow-step {
            border: 1px solid var(--line);
            border-radius: var(--radius);
            background: rgba(16, 22, 34, 0.72);
            padding: 14px 16px;
        }

        .workflow-step strong {
            color: var(--text);
            display: block;
            font-size: 0.98rem;
            margin-bottom: 4px;
        }

        .workflow-step span {
            color: var(--muted);
            font-size: 0.86rem;
        }

        [data-testid="stFileUploader"] {
            border: 1px solid var(--line);
            border-radius: var(--radius);
            background: rgba(16, 22, 34, 0.78);
            padding: 16px;
        }

        [data-testid="stFileUploader"] section {
            border: 1px dashed rgba(24, 230, 196, 0.45);
            border-radius: var(--radius);
            background: rgba(24, 230, 196, 0.05);
        }

        [data-testid="stFileUploader"] small,
        [data-testid="stFileUploader"] span {
            color: var(--muted);
        }

        div[data-baseweb="select"] > div {
            background-color: var(--panel-soft);
            border-color: var(--line);
            border-radius: var(--radius);
        }

        .stButton > button,
        .stDownloadButton > button {
            border: 0;
            border-radius: var(--radius);
            background: linear-gradient(135deg, var(--cyan), var(--blue));
            color: #061018;
            font-weight: 850;
            min-height: 46px;
            box-shadow: 0 12px 30px rgba(24, 230, 196, 0.18);
        }

        .stButton > button:hover,
        .stDownloadButton > button:hover {
            color: #061018;
            filter: brightness(1.06);
            transform: translateY(-1px);
        }

        .stProgress > div > div {
            background-color: rgba(148, 163, 184, 0.18);
        }

        .stProgress > div > div > div {
            background: linear-gradient(90deg, var(--cyan), var(--blue));
        }

        [data-testid="stVideo"] {
            border: 1px solid var(--line);
            border-radius: var(--radius);
            overflow: hidden;
            background: #020617;
            box-shadow: 0 18px 48px rgba(0, 0, 0, 0.35);
        }

        .stAlert {
            border-radius: var(--radius);
        }

        .section-label {
            color: var(--cyan);
            font-size: 0.78rem;
            font-weight: 850;
            text-transform: uppercase;
            margin: 18px 0 6px;
        }

        .coach-card {
            background: linear-gradient(135deg, rgba(20, 27, 40, 0.98), rgba(12, 17, 26, 0.98));
            border: 1px solid rgba(24, 230, 196, 0.24);
            border-left: 5px solid var(--cyan);
            border-radius: var(--radius);
            padding: 24px;
            margin-top: 12px;
            margin-bottom: 24px;
            box-shadow: 0 18px 48px rgba(0, 0, 0, 0.32);
        }

        .coach-header {
            display: flex;
            align-items: center;
            gap: 14px;
            margin-bottom: 16px;
            border-bottom: 1px solid var(--line);
            padding-bottom: 14px;
        }

        .coach-avatar {
            width: 46px;
            height: 46px;
            border-radius: var(--radius);
            display: grid;
            place-items: center;
            background: linear-gradient(135deg, var(--cyan), var(--blue));
            color: #061018;
            font-size: 22px;
            font-weight: 900;
        }

        .coach-title {
            font-size: 1.25rem;
            font-weight: 850;
            color: var(--text);
            margin: 0;
        }

        .coach-subtitle {
            font-size: 0.72rem;
            color: var(--muted);
            text-transform: uppercase;
            font-weight: 800;
            margin-top: 3px;
        }

        .coach-feedback {
            font-size: 1rem;
            line-height: 1.75;
            color: #e2e8f0;
            margin: 0;
        }

        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
            gap: 14px;
            margin-top: 18px;
        }

        .metric-item {
            background: linear-gradient(180deg, rgba(26, 34, 50, 0.92), rgba(16, 22, 34, 0.92));
            border: 1px solid var(--line);
            border-radius: var(--radius);
            padding: 18px;
            min-height: 142px;
            display: grid;
            align-content: center;
            transition: transform 0.18s ease, border-color 0.18s ease;
        }

        .metric-item:hover {
            transform: translateY(-2px);
            border-color: rgba(24, 230, 196, 0.42);
        }

        .metric-label {
            font-size: 0.72rem;
            color: var(--muted);
            text-transform: uppercase;
            font-weight: 850;
            margin-bottom: 8px;
        }

        .metric-value {
            font-size: 2rem;
            line-height: 1;
            font-weight: 900;
            color: var(--text);
        }

        .metric-status {
            width: fit-content;
            margin-top: 14px;
            padding: 6px 10px;
            border-radius: 999px;
            font-size: 0.7rem;
            font-weight: 850;
            text-transform: uppercase;
        }

        .status-optimal {
            background: rgba(52, 211, 153, 0.14);
            color: var(--green);
            border: 1px solid rgba(52, 211, 153, 0.36);
        }

        .status-deviation {
            background: rgba(251, 113, 133, 0.14);
            color: var(--red);
            border: 1px solid rgba(251, 113, 133, 0.36);
        }

        .status-info {
            background: rgba(79, 140, 255, 0.14);
            color: #93c5fd;
            border: 1px solid rgba(79, 140, 255, 0.36);
        }

        .stExpander {
            border: 1px solid var(--line);
            border-radius: var(--radius);
            overflow: hidden;
            background: rgba(16, 22, 34, 0.72);
        }

        [data-testid="stDataFrame"] {
            border: 1px solid var(--line);
            border-radius: var(--radius);
            overflow: hidden;
        }

        hr {
            border-color: var(--line);
            margin: 2rem 0 1rem;
        }

        @media (max-width: 820px) {
            .app-hero,
            .workflow {
                grid-template-columns: 1fr;
            }

            .hero-copy,
            .hero-panel {
                padding: 18px;
            }

            .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
            }
        }

        /* Modern Custom Loading Animations */
        .loading-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 38px 24px;
            background: linear-gradient(135deg, rgba(20, 27, 40, 0.96), rgba(12, 17, 26, 0.96));
            border: 1px solid var(--line);
            border-left: 4px solid var(--cyan);
            border-radius: var(--radius);
            margin: 22px 0;
            text-align: center;
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3);
        }

        .loading-pulse {
            width: 54px;
            height: 54px;
            border-radius: 50%;
            background-color: var(--cyan);
            box-shadow: 0 0 15px rgba(24, 230, 196, 0.6);
            animation: pulse-ring 1.6s cubic-bezier(0.455, 0.03, 0.515, 0.955) infinite;
            margin-bottom: 20px;
        }

        @keyframes pulse-ring {
            0% {
                transform: scale(0.7);
                opacity: 0.9;
                box-shadow: 0 0 15px rgba(24, 230, 196, 0.6);
            }
            50% {
                transform: scale(1.15);
                opacity: 0.45;
                box-shadow: 0 0 35px rgba(79, 140, 255, 0.85);
            }
            100% {
                transform: scale(0.7);
                opacity: 0.9;
                box-shadow: 0 0 15px rgba(24, 230, 196, 0.6);
            }
        }

        .loading-text {
            color: var(--text);
            font-size: 1.15rem;
            font-weight: 850;
            letter-spacing: 0.4px;
            margin: 0;
        }

        .loading-subtext {
            color: var(--muted);
            font-size: 0.82rem;
            margin: 6px 0 0;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.8px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
