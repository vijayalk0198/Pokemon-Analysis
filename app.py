import streamlit as st
import pandas as pd
import os
import plotly.graph_objects as go
import ast

# Set page configuration
st.set_page_config(page_title="Pokémon Search App", layout="wide")

# Load the Pokémon dataset
@st.cache_data
def load_data():
    return pd.read_csv("data/pokemon.csv")

df = load_data()

# Initialize session state for search
if 'search_name' not in st.session_state:
    st.session_state.search_name = ""

# Function to create radial plot
def create_radial_plot(pokemon):
    categories = ['Attack', 'Defense', 'HP', 'Sp. Attack', 'Sp. Defense', 'Speed']
    values = [
        pokemon['attack'],
        pokemon['defense'],
        pokemon['hp'],
        pokemon['sp_attack'],
        pokemon['sp_defense'],
        pokemon['speed']
    ]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]],  # Close the loop
        theta=categories + [categories[0]],
        fill='toself',
        name=pokemon['name']
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, max(values) * 1.2]),
        ),
        showlegend=True,
        title=f"Stats for {pokemon['name']}",
        height=400
    )

    return fig

# App title
st.title("Pokémon Search App")

# Search bar
search_name = st.text_input("Search Pokémon by Name:", value=st.session_state.search_name, placeholder="e.g., Pikachu")

# Trigger search on typing
if search_name != st.session_state.search_name:
    st.session_state.search_name = search_name
    st.rerun()

# Display Pokémon details if search input provided
if st.session_state.search_name.strip() != "":
    search_name = st.session_state.search_name
    result = df[df['name'].str.lower() == search_name.lower()]

    if not result.empty:
        pokemon = result.iloc[0]
        pokemon_name = pokemon['name']
        type1 = pokemon['type1'].capitalize() if pd.notna(pokemon['type1']) else None
        type2 = pokemon['type2'].capitalize() if pd.notna(pokemon['type2']) else None

        # Parse abilities list string safely
        try:
            abilities_list = ast.literal_eval(pokemon['abilities'])
            abilities_clean = ", ".join(abilities_list)
        except:
            abilities_clean = pokemon['abilities']

        # Create two columns for image and specs
        col1, col2 = st.columns([1, 2])

        with col1:
            # Image path with light grey background
            image_path = f"images/pokemon/{pokemon_name.lower()}.png"
            st.markdown("""
            <div style='background-color: #f0f0f0; padding: 10px; border-radius: 8px; text-align: center;'>
            """, unsafe_allow_html=True)
            if os.path.exists(image_path):
                st.image(image_path, caption=pokemon_name, use_column_width=True)
            else:
                st.warning(f"No image found for {pokemon_name}")
            st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            # Display specs
            st.subheader(f"{pokemon_name}")
            st.write(f"**Primary Type:** {type1}")
            if pd.notna(type2):
                st.write(f"**Secondary Type:** {type2}")
            st.write(f"**Abilities:** {abilities_clean}")

            # Radial plot
            st.plotly_chart(create_radial_plot(pokemon), use_container_width=True)

        # Reset search option
        if st.button("Search Another Pokémon"):
            st.session_state.search_name = ""
            st.rerun()
    else:
        st.error("Pokémon not found! Please check the name and try again.")