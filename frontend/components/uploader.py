import streamlit as st

def render_uploader():
    """Renders the file upload widget."""
    return st.file_uploader(
        "Upload Industrial Component Image", 
        type=["jpg", "png", "jpeg"],
        help="Supports PCB, Metal tools, and Machinery parts."
    )