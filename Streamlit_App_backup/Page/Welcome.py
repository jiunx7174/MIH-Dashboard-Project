from streamlit_lottie import st_lottie
import streamlit as st
import requests
import json

def App():
    lottie_json = json.loads(requests.get("https://assets4.lottiefiles.com/packages/lf20_ccvekmzu.json").text)
    col_temp = st.columns(3)
    with col_temp[1]:
        st_lottie(lottie_json, width=500, speed=1)
    st.markdown("<h1 style='text-align: center; font-size: 100px;'>  Welcome !</h1>", unsafe_allow_html=True)
    # col_temp = st.columns(3)
    # with col_temp[1]:
    