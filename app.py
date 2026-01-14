import streamlit as st
import uuid
import os
import sys
sys.path.append(os.getcwd())

from frontend.styles import apply_custom_styles
from frontend.sidebar import render_sidebar
from backend.api_client import chat_with_industrial_ai
from backend.utils import generate_pdf_report
from backend.database import init_db, create_session, add_message, get_session_history, update_session_image, get_session_meta
from backend.schemas import GUARDRAIL_PROMPT

st.set_page_config(page_title="Apex Industrial AI", layout="wide", page_icon="⚙️")

ASSETS_DIR = os.path.join("frontend", "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)

def render_metrics(u):
    """Helper to render the 3-pill metric row safely."""
    # Handle DB Dictionary vs API Object
    if isinstance(u, dict):
        tokens = u.get('total_tokens', 0)
        latency = u.get('latency', 0.0)
        speed = u.get('throughput', 0.0)
    else:
        tokens = getattr(u, 'total_tokens', 0)
        latency = getattr(u, 'latency', 0.0)
        speed = getattr(u, 'throughput', 0.0)
    
    st.markdown(f"""
    <div style="display: flex; gap: 10px; margin-top: 10px;">
        <div class='tech-pill'>🪙 {tokens} TOKENS</div>
        <div class='tech-pill'>⏱ {latency}s</div>
        <div class='tech-pill'>⚡ {speed} T/s</div>
    </div>
    """, unsafe_allow_html=True)

def main():
    init_db()
    
    if "active_session_id" not in st.session_state:
        st.session_state.active_session_id = str(uuid.uuid4())
        create_session(st.session_state.active_session_id)
        
    if st.session_state.get("trigger_new_chat"):
        st.session_state.active_session_id = str(uuid.uuid4())
        create_session(st.session_state.active_session_id)
        st.session_state.trigger_new_chat = False

    current_messages = get_session_history(st.session_state.active_session_id)
    if "messages" not in st.session_state or st.session_state.messages != current_messages:
        st.session_state.messages = current_messages

    session_meta = get_session_meta(st.session_state.active_session_id)

    base_instruction, user_requirements, selected_theme = render_sidebar()
    apply_custom_styles(mode=selected_theme)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h1>APEX INDUSTRIAL AI</h1>", unsafe_allow_html=True)
    st.markdown("<h3>PRECISION DIAGNOSTICS SUITE</h3>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    col_visual, col_chat = st.columns([1, 2], gap="large")

    with col_visual:
        st.markdown("#### 1. COMPONENT SCAN")
        saved_image_path = session_meta.get('image_path') if session_meta else None
        uploaded_file = st.file_uploader("Upload", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
        
        active_image = None
        if uploaded_file:
            file_path = os.path.join(ASSETS_DIR, f"{st.session_state.active_session_id}.png")
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            update_session_image(st.session_state.active_session_id, file_path)
            active_image = uploaded_file
            st.success("✔ IMAGE SAVED")
        elif saved_image_path and os.path.exists(saved_image_path):
            active_image = saved_image_path
            st.info("📂 LOADED FROM ARCHIVE")

        if active_image:
            st.image(active_image, width="stretch")
        else:
            st.markdown("""<div style="text-align:center; padding: 40px; border: 2px dashed var(--border-color); color: var(--text-secondary);">No visual data source.</div>""", unsafe_allow_html=True)

    with col_chat:
        c1, c2 = st.columns([3, 1])
        with c1: st.markdown("#### 3. ANALYSIS LOG")
        with c2:
            if st.session_state.messages:
                pdf_bytes = generate_pdf_report(st.session_state.messages)
                st.download_button("📥 EXPORT PDF", data=pdf_bytes, file_name=f"Report.pdf", mime="application/pdf", width="stretch")

        chat_container = st.container(height=600, border=True)
        with chat_container:
            if not st.session_state.messages:
                st.markdown("<div style='text-align: center; color: var(--text-secondary); padding-top: 50px;'>SYSTEM STANDBY.</div>", unsafe_allow_html=True)
            
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
                    if msg.get("usage"):
                        render_metrics(msg["usage"])

        if prompt := st.chat_input("Enter diagnostic command..."):
            if not active_image:
                st.toast("⚠️ ERR: NO VISUAL INPUT DETECTED", icon="🚫")
            else:
                st.session_state.messages.append({"role": "user", "content": prompt})
                add_message(st.session_state.active_session_id, "user", prompt)
                
                with chat_container:
                    with st.chat_message("user"):
                        st.markdown(prompt)

                final_system_prompt = f"{base_instruction}\n\n{GUARDRAIL_PROMPT}"
                if user_requirements:
                    final_system_prompt += f"\n\nADDITIONAL OPERATOR INSTRUCTIONS:\n{user_requirements}"

                with chat_container:
                    with st.chat_message("assistant"):
                        message_placeholder = st.empty()
                        with st.spinner("PROCESSING..."):
                            try:
                                if isinstance(active_image, str):
                                    img_for_api = open(active_image, "rb")
                                    import io
                                    img_bytes = io.BytesIO(img_for_api.read())
                                    img_for_api.close()
                                else:
                                    img_bytes = active_image
                                
                                response = chat_with_industrial_ai(
                                    current_question=prompt,
                                    image_file=img_bytes,
                                    chat_history=st.session_state.messages[:-1],
                                    system_prompt=final_system_prompt
                                )
                                message_placeholder.markdown(response.content)
                                usage_dict = response.usage.model_dump()
                                
                                render_metrics(response.usage) # <--- NEW DISPLAY

                                add_message(st.session_state.active_session_id, "assistant", response.content, usage_dict)
                                st.session_state.messages.append({"role": "assistant", "content": response.content, "usage": usage_dict})

                            except Exception as e:
                                st.error(f"SYSTEM FAILURE: {str(e)}")

if __name__ == "__main__":
    main()