import streamlit as st


def apply_styles():
    st.markdown(
        """
        <style>
        .stApp {
            max-width: 1100px;
            margin: 0 auto;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
