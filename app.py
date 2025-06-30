import streamlit as st
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go
import ast
from battle_model import train_model, predict_battle

# Set page configuration
st.set_page_config(page_title="Pokémon Analysis App", layout="wide")

# Load the Pokémon dataset
@st.cache_data
def load_data():
    return pd.read_csv("data/Pokemon.csv")

# Load data
df = load_data()

# Train battle model
@st.cache_resource
def load_battle_model():
    return train_model()

model, scaler, numerical_cols, type_table = load_battle_model()

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

# Home page
def home_page():
    st.markdown("<h1 style='text-align: center;'>Welcome</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align: center;'>Explore the world of Pokémon with interactive analytics! "
        "View individual Pokémon stats, compare types, or simulate epic battles.</p>",
        unsafe_allow_html=True
    )
    
    # Generation distribution pie chart
    gen_counts = df['generation'].value_counts().sort_index()
    fig_pie = px.pie(
        names=gen_counts.index,
        values=gen_counts.values,
        title="Pokémon Distribution by Generation",
        hole=0.3
    )
    fig_pie.update_layout(margin=dict(t=50, b=50))
    st.plotly_chart(fig_pie, use_container_width=True)
    
    # Type effectiveness heatmap
    type_cols = [col for col in df.columns if col.startswith('against_')]
    types = [col.replace('against_', '').capitalize() for col in type_cols]
    type_data = df.groupby('type1')[type_cols].mean().reset_index()
    type_data['type1'] = type_data['type1'].str.capitalize()
    type_data.columns = ['Type'] + types
    fig_heatmap = go.Figure(data=go.Heatmap(
        z=type_data[types].values,
        x=types,
        y=type_data['Type'],
        colorscale='Viridis',
        zmin=0,
        zmax=2,
        hoverongaps=False
    ))
    fig_heatmap.update_layout(
        title="Type Effectiveness Heatmap (Average Multiplier)",
        xaxis_title="Defending Type",
        yaxis_title="Attacking Type",
        height=500
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # Navigation buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Card"):
            st.session_state.page = "card"
            st.rerun()
    with col2:
        if st.button("Battle"):
            st.session_state.page = "battle"
            st.rerun()

# Card page
def card_page():
    st.title("Pokémon Card")
    
    if 'submitted' not in st.session_state:
        st.session_state.submitted = False
        st.session_state.search_name = ""
    
    if not st.session_state.submitted:
        with st.container():
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
                    st.rerun()
    
    if st.session_state.submitted:
        search_name = st.session_state.search_name
        result = df[df['name'].str.lower() == search_name.lower()]
        
        if not result.empty:
            pokemon = result.iloc[0]
            pokemon_name = pokemon['name']
            type1 = pokemon['type1'].capitalize()
            type2 = pokemon['type2'].capitalize() if pd.notna(pokemon['type2']) else None
            abilities = ast.literal_eval(pokemon['abilities']) if isinstance(pokemon['abilities'], str) else pokemon['abilities']
            abilities_clean = ", ".join(abilities) if isinstance(abilities, list) else abilities
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                image_path = f"images/pokemon/{pokemon_name.lower()}.png"
                if os.path.exists(image_path):
                    st.image(image_path, caption=f"{pokemon_name}", use_column_width=True)
                else:
                    st.warning(f"No image found for {pokemon_name}")
            
            with col2:
                st.subheader(f"{pokemon_name}")
                st.write(f"**Primary Type:** {type1}")
                if type2:
                    st.write(f"**Secondary Type:** {type2}")
                st.write(f"**Abilities:** {abilities_clean}")
                st.plotly_chart(create_radial_plot(pokemon), use_container_width=True)
            
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
    
    if st.button("Back to Home"):
        st.session_state.page = "home"
        st.session_state.submitted = False
        st.session_state.search_name = ""
        st.rerun()

# Battle page
def battle_page():
    st.title("Pokémon Battle Simulation")
    st.write("Select two Pokémon to simulate a battle")
    
    col1, col2 = st.columns(2)
    with col1:
        poke1 = st.selectbox("First Pokémon", sorted(df['name'].unique()), key='battle1')
    with col2:
        poke2 = st.selectbox("Second Pokémon", sorted(df['name'].unique()), key='battle2')
    
    if poke1 and poke2:
        winner, message = predict_battle(poke1, poke2, model, scaler, numerical_cols, type_table, df)
        if winner:
            st.success(message)
        else:
            st.error(message)
    
    if st.button("Back to Home"):
        st.session_state.page = "home"
        st.rerun()

# Main app logic
if 'page' not in st.session_state:
    st.session_state.page = "home"

if st.session_state.page == "home":
    home_page()
elif st.session_state.page == "card":
    card_page()
elif st.session_state.page == "battle":
    battle_page()