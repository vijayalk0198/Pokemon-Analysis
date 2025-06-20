import streamlit as st
import pandas as pd
import os
import plotly.graph_objects as go
import time

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
    .pokemon-image {{
        border: 5px solid #ffcb05;
        border-radius: 15px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        background-color: #f0f0f0;
        padding: 10px;
        max-width: 300px;
        transition: all 0.5s ease-in-out;
    }}
    .search-bar {{
        transition: transform 0.5s ease-in-out;
    }}
    .pokemon-card {{
        opacity: 0;
        transform: translateY(50px);
        transition: all 0.5s ease-in-out;
    }}
    .pokemon-card.show {{
        opacity: 1;
        transform: translateY(0);
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
pokemon_name = st.text_input("Search Pokémon by Name", placeholder="Enter Pokémon name...", key="pokemon_search")

# Initialize variables
pokemon_image = None
pokemon_info = None

# Create placeholder for search bar and card
search_container = st.container()
card_container = st.container()

if pokemon_name:
    # Animate search bar moving out
    search_container.markdown(
        """
        <style>
        .search-bar {
            transform: translateY(-100px);
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
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
    
    # Show card with animation
    card_container.markdown(
        """
        <style>
        .pokemon-card {
            opacity: 1;
            transform: translateY(0);
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# Create two columns for layout
col1, col2 = card_container.columns([1, 1])

with col1:
    # Display Pokémon image if available
    if pokemon_image:
        st.markdown(
            f'<img src="file://{pokemon_image}" class="pokemon-image" style="image-rendering: pixelated;">',
            unsafe_allow_html=True
        )
    else:
        st.write("No Pokémon selected or image not found.")

with col2:
    # Display Pokémon information
    if pokemon_info is not None:
        st.subheader(pokemon_info['name'])
        st.write(f"**Primary Type**: {pokemon_info['type1']}")
        if not pd.isna(pokemon_info['type2']):
            st.write(f"**Secondary Type**: {pokemon_info['type2']}")
        st.write(f"**Generation**: {pokemon_info['generation']}")
        st.write(f"**Abilities**: {pokemon_info['abilities']}")

        # Radial chart for stats
        stats = ['hp', 'attack', 'defense', 'sp_attack', 'sp_defense', 'speed']
        values = [pokemon_info[stat] for stat in stats]
        
        fig = go.Figure(data=[
            go.Scatterpolar(
                r=values + [values[0]],
                theta=stats + [stats[0]],
                fill='toself',
                line=dict(color='#ffcb05')
            )
        ])
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, max(values) * 1.2]
                )
            ),
            showlegend=False,
            title="Pokémon Stats"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("Enter a Pokémon name to see details.")

# Back button to home page
if st.button("Back to Home"):
    st.switch_page("app.py")