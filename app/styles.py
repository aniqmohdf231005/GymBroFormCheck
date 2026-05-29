import streamlit as st


def apply_styles():
    st.markdown(
        """
        <style>
        /* General Layout */
        .stApp {
            max-width: 1100px;
            margin: 0 auto;
        }
        
        /* Modern Glassmorphic Coach Card */
        .coach-card {
            background: linear-gradient(135deg, rgba(28, 30, 41, 0.85) 0%, rgba(16, 18, 27, 0.95) 100%);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-left: 5px solid #00ffd0;
            border-radius: 16px;
            padding: 24px;
            margin-top: 15px;
            margin-bottom: 25px;
            backdrop-filter: blur(12px);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
            transition: all 0.3s ease;
        }
        
        .coach-header {
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 16px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
            padding-bottom: 12px;
        }
        
        .coach-avatar {
            font-size: 36px;
            animation: pulse 2s infinite alternate;
        }
        
        .coach-title {
            font-size: 22px;
            font-weight: 800;
            color: #00ffd0;
            letter-spacing: 0.5px;
            margin: 0;
            text-shadow: 0 0 10px rgba(0, 255, 208, 0.2);
        }
        
        .coach-subtitle {
            font-size: 12px;
            color: #8a92b2;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            margin-top: 2px;
        }
        
        .coach-feedback {
            font-size: 16px;
            line-height: 1.7;
            color: #e2e8f0;
            font-weight: 400;
            margin: 0;
        }
        
        /* Badges & Metrics Grid */
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 16px;
            margin-top: 20px;
        }
        
        .metric-item {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            padding: 16px;
            text-align: center;
            transition: transform 0.2s ease;
        }
        
        .metric-item:hover {
            transform: translateY(-2px);
            background: rgba(255, 255, 255, 0.05);
        }
        
        .metric-label {
            font-size: 12px;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 6px;
        }
        
        .metric-value {
            font-size: 24px;
            font-weight: 700;
            color: #f8fafc;
        }
        
        .metric-status {
            display: inline-block;
            margin-top: 8px;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
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
        
        @keyframes pulse {
            0% { transform: scale(1); }
            100% { transform: scale(1.08); }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
