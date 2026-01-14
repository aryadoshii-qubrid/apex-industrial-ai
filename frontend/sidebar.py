import streamlit as st
from backend.schemas import PROMPTS
from backend.database import get_all_sessions, update_session_title, get_session_meta, delete_session, update_session_mode

def render_sidebar():
    with st.sidebar:
        st.markdown("## ⚙️ CONTROLS")
        st.markdown("---")
        
        # 1. NEW INSPECTION
        if st.button("➕ NEW INSPECTION", type="primary", width="stretch"):
            st.session_state.trigger_new_chat = True
            st.rerun()

        # 2. MANAGE SESSION
        current_mode = "General Analysis" # Default
        
        if "active_session_id" in st.session_state:
            active_id = st.session_state.active_session_id
            meta = get_session_meta(active_id)
            if meta:
                current_title = meta['title']
                
                # Fetch saved mode from DB (handle missing key gracefully)
                saved_mode = meta.get('mode')
                if saved_mode in PROMPTS:
                    current_mode = saved_mode

                with st.expander("⚙️ Session Options", expanded=False):
                    st.caption("Rename")
                    new_name = st.text_input("Name", value=current_title, label_visibility="collapsed")
                    if st.button("💾 Save", width="stretch"):
                        if new_name and new_name != current_title:
                            update_session_title(active_id, new_name)
                            st.rerun()
                    
                    st.caption("Delete")
                    if st.button("🗑 Delete", width="stretch"):
                        delete_session(active_id)
                        del st.session_state.active_session_id
                        st.rerun()

        st.markdown("---")

        # 3. PROTOCOL (Synced with Database)
        st.markdown("### 1. PROTOCOL")
        
        # Calculate index for the dropdown based on saved mode
        mode_options = list(PROMPTS.keys())
        try:
            default_index = mode_options.index(current_mode)
        except ValueError:
            default_index = 0

        selected_mode = st.selectbox(
            "Persona", 
            mode_options, 
            index=default_index, 
            label_visibility="collapsed"
        )
        
        # Logic: If user changes the dropdown, save it to DB immediately
        if "active_session_id" in st.session_state and selected_mode != current_mode:
            update_session_mode(st.session_state.active_session_id, selected_mode)
            st.rerun() # Refresh to confirm the lock

        base_instruction = PROMPTS[selected_mode]

        st.markdown("### 2. FOCUS")
        user_requirements = st.text_area("Instructions", height=80, placeholder="Check for cracks...", label_visibility="collapsed")
        
        st.markdown("### 3. ARCHIVES")
        sessions = get_all_sessions()
        if not sessions:
            st.caption("No history.")
        
        for s in sessions:
            is_active = s['id'] == st.session_state.get("active_session_id")
            icon = "🟢" if is_active else "📄"
            date_short = s['created_at'][5:10]
            btn_label = f"{icon} {date_short} | {s['title']}"
            if st.button(btn_label, key=s['id'], width="stretch"):
                st.session_state.active_session_id = s['id']
                st.rerun()

        st.markdown("---")
        
        # 4. THEME
        st.caption("INTERFACE THEME")
        selected_theme = st.selectbox(
            "Theme", 
            ["Light", "Dark"], 
            index=0, 
            label_visibility="collapsed"
        )

        return base_instruction, user_requirements, selected_theme