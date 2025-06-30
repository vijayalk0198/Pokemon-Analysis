import streamlit as st
import pandas as pd
import os

#Setting the page title here
st.set_page_config(page_title="Pokémon Search App", layout="centered")

# Load the Pokémon dataset
@st.cache_data
def load_data():
    return pd.read_csv("data/pokemon.csv")
df = load_data()

# App title
st.title("Pokémon Search App")

# Search bar
search_name = st.text_input("Enter Pokémon Name:", placeholder="e.g., Pikachu")

if search_name:
    # Filter data based on search input (case-insensitive)
    result = df[df['name'].str.lower() == search_name.lower()]
    
    if not result.empty:
        # Get Pokémon details
        pokemon = result.iloc[0]
        type1 = pokemon['type1']
        type2 = pokemon['type2'] if pd.notna(pokemon['type2']) else "None"
        pokemon_name = pokemon['name']
        
        # Display Pokémon details
        st.subheader(f"{pokemon_name}")
        st.write(f"**Primary Type:** {type1}")
        st.write(f"**Secondary Type:** {type2}")
        
        # Image path
        image_path = f"images/pokemon/{pokemon_name.lower()}.png"
        
        # Check if image exists and display it
        if os.path.exists(image_path):
            st.image(image_path, caption=f"{pokemon_name}", use_column_width=True)
        else:
            st.warning(f"No image found for {pokemon_name}")
    else:
        st.error("Pokémon not found! Please check the name and try again.")