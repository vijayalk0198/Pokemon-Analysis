import streamlit as st

# Display background image
#st.image("images/pokeball.jpg", use_column_width=True)



# Load CSS for full-screen background
with open("css/app.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Placeholder content
st.title("Pokémon Study")