import streamlit as st
import base64

# Function to embed local image as base64 in CSS
def set_bg_from_local(image_path):
    with open(image_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode()
    st.markdown(
        f"""
        <style>
        [data-testid="stAppViewContainer"] {{
            background-image: url("data:image/jpg;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }}
        h1 {{
            color: #ffcb05;
            text-align: center;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Apply background image from local file
set_bg_from_local("images/pokeball.jpg")

# Streamlit title
st.title("Pokémon Study")
