"""VulnPrior entry point: page config, shared styling and navigation.

Run with:  streamlit run app.py
"""
import streamlit as st

from ui import footer, inject_css

st.set_page_config(page_title="VulnPrior", page_icon="🛡️", layout="wide")
inject_css()

pages = [
    st.Page("views/home.py", title="Home", icon="🏠", default=True),
    st.Page("views/prioritizer.py", title="Prioritizer", icon="🛡️"),
]
page = st.navigation(pages, position="top")
page.run()

footer()