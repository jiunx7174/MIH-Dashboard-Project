import streamlit as st


def App():
    st.markdown("# Activity Mapping")
    st.write(st.session_state)
    st.stop()