import streamlit as st
import pandas as pd
import os

# Set page configuration with white background
st.markdown(
    """
    <style>
    [data-testid="stAppViewContainer"] {{
        background-color: white;
    }}
    [data-testid="stMarkdownContainer"] h1 {{
        color: black !important;
        text-align: center;
    }}
    .stButton>button {{
        background-color: #ffcb05;
        color: black;
        border-radius: 10px;
        font-weight: bold;
        margin: 10px;
        padding: 10px 20px;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# Streamlit title
st.title("Pokémon Individual Analysis")

# Load the pokemon.csv file
@st.cache_data
def load_data():
    return pd.read_csv("data/pokemon.csv")

df = load_data()

# Search bar for Pokémon name
pokemon_name = st.text_input("Search Pokémon by Name", placeholder="Enter Pokémon name...")

# Initialize variables
pokemon_image = None
pokemon_info = None

if pokemon_name:
    # Filter data based on input
    pokemon_data = df[df['name'].str.lower() == pokemon_name.lower()]
    
    if not pokemon_data.empty:
        pokemon_info = pokemon_data.iloc[0]
        # Construct image path
        image_path = f"images/pokemon/{pokemon_info['name'].lower()}.png"
        if os.path.exists(image_path):
            pokemon_image = image_path
        else:
            st.warning(f"No image found for {pokemon_name}")

# Create two columns for layout
col1, col2 = st.columns([1, 1])

with col1:
    # Display Pokémon image if available
    if pokemon_image:
        st.image(pokemon_image, caption=pokemon_name, width=300)
    else:
        st.write("No Pokémon selected or image not found.")

with col2:
    # Display Pokémon information
    if pokemon_info is not None:
        st.subheader(pokemon_info['name'])
        st.write(f"**Type 1**: {pokemon_info['type1']}")
    else:
        st.write("Enter a Pokémon name to see details.")

# Back button to home page
if st.button("Back to Home"):
    st.switch_page("app.py")