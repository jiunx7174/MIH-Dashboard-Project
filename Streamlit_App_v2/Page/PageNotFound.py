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


    print("load modal")
    modal = Modal("Demo Modal", key='modal_test')
    open_modal = st.button("Open")
    if open_modal:
        print("open modal")
        modal.open()

    if modal.is_open():
        with modal.container():
            print("write modal")
            st.write("Text goes here")

            html_string = '''
            <h1>HTML string in RED</h1>

            <script language="javascript">
            document.querySelector("h1").style.color = "red";
            </script>
            '''
            components.html(html_string)

            st.write("Some fancy text")
            value = st.checkbox("Check me")
            st.write(f"Checkbox checked: {value}")
            st.write(f"st.button: {open_modal}")
