import streamlit as st
from streamlit_lottie import st_lottie
import json

from streamlit_modal import Modal

import streamlit.components.v1 as components

def App():
    print("load lottie")
    lottie_json = json.load(open("Streamlit_App/Data/lottie-files/5451-search-file.json"))

    Col = st.columns([1,1,1])

    with Col[1]:
        st.markdown("# Page Not Found")
        st_lottie(lottie_json, width=200)


