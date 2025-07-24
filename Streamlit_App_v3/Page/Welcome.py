from streamlit_lottie import st_lottie
import streamlit as st
import requests
import json

def App():
    with open(r'Data/lottie-files/WelcomeLottie.json', 'r') as f:
    # lottie_json = json.loads(requests.get("https://assets4.lottiefiles.com/packages/lf20_ccvekmzu.json").text)
        lottie_json = json.load(f)
    col_temp = st.columns(3)
    with col_temp[1]:
        st_lottie(lottie_json, width=420, speed=1,key="hello")
    st.markdown("<h1 style='text-align: center; font-size: 100px;'>  Welcome !</h1>", unsafe_allow_html=True)
    st.stop()
    # st.stop()
    # col_temp = st.columns(3)
    # with col_temp[1]:
    