import streamlit as st
from streamlit_lottie import st_lottie
import json

def App():
    print('lotti')
    st.set_page_config(page_title="Realtime Activity Mapping", page_icon=None, layout="centered",)
    # st.markdown("# User Not recognized")
    hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True) 
    
    lottie_json = json.load(open("Streamlit_App/Data/lottie-files/5451-search-file.json"))
    # col_temp = st.columns(3)
    # with col_temp[1]:
    st.markdown("# User Not Authorized")
    st_lottie(lottie_json, width=500)
    
