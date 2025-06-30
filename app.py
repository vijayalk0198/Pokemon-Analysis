import streamlit as st
import pandas as pd
import os
import plotly.graph_objects as go

# Set page configuration
st.set_page_config(page_title="Pokémon Search App", layout="wide")

# Load the Pokémon dataset
@st.cache_data
def load_data():
    return pd.read_csv("data/pokemon.csv")

df = load_data()

# Initialize session state for search
if 'submitted' not in st.session_state:
    st.session_state.submitted = False
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

# Search bar with animation
if not st.session_state.submitted:
    with st.container():
        # Custom CSS for fade-out animation
        st.markdown("""
        <style>
        .fade-out {
            animation: fadeOut 0.5s ease-in-out forwards;
        }
        @keyframes fadeOut {
            0% { opacity: 1; }
            100% { opacity: 0; display: none; }
        }
        </style>
        """, unsafe_allow_html=True)
        
        search_name = st.text_input("Enter Pokémon Name:", placeholder="e.g., Pikachu", key="search_input")
        if st.button("Enter"):
            if search_name:
                st.session_state.search_name = search_name
                st.session_state.submitted = True
                # Force rerun to apply state change
                st.rerun()

# Display Pokémon details after search
if st.session_state.submitted:
    search_name = st.session_state.search_name
    # Filter data based on search input (case-insensitive)
    result = df[df['name'].str.lower() == search_name.lower()]
    
    if not result.empty:
        pokemon = result.iloc[0]
        pokemon_name = pokemon['name']
        type1 = pokemon['type1']
        type2 = pokemon['type2']
        abilities = pokemon['abilities']
        
        # Create two columns for image and specs
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Image path
            image_path = f"images/pokemon/{pokemon_name.lower()}.png"
            if os.path.exists(image_path):
                st.image(image_path, caption=f"{pokemon_name}", use_column_width=True)
            else:
                st.warning(f"No image found for {pokemon_name}")
        
        with col2:
            # Display specs
            st.subheader(f"{pokemon_name}")
            st.write(f"**Type 1:** {type1}")
            if pd.notna(type2):
                st.write(f"**Type 2:** {type2}")
            st.write(f"**Abilities:** {abilities}")
            
            # Radial plot
            st.plotly_chart(create_radial_plot(pokemon), use_container_width=True)
        
        # Button to reset search
        if st.button("Search Another Pokémon"):
            st.session_state.submitted = False
            st.session_state.search_name = ""
            st.rerun()
    else:
        st.error("Pokémon not found! Please check the name and try again.")
        if st.button("Try Again"):
            st.session_state.submitted = False
            st.session_state.search_name = ""
            st.rerun()