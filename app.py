import streamlit as st

with open("css/app.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("Pokémon Study")