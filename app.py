import streamlit as st
import pandas as pd
import os
import base64
import ast
import plotly.graph_objects as go

# Hide sidebar completely
st.set_page_config(page_title="Pokémon App", layout="centered", initial_sidebar_state="collapsed")
hide_sidebar = """
    <style>
        [data-testid="stSidebar"] {display: none;}
    </style>
"""
st.markdown(hide_sidebar, unsafe_allow_html=True)

# Load data once
@st.cache_data
def load_data():
    return pd.read_csv("pokemon.csv")

df = load_data()

# Page control using session_state
if "page" not in st.session_state:
    st.session_state.page = "home"

# Navigation Functions
def go_home():
    st.session_state.page = "home"

def go_individual():
    st.session_state.page = "individual"

def go_comparative():
    st.session_state.page = "comparative"

def go_battle():
    st.session_state.page = "battle"

# Radial plot function
def create_radial_plot(pokemon):
    stats = ['attack', 'defense', 'hp', 'sp_attack', 'sp_defense', 'speed']
    values = [pokemon[stat] for stat in stats]
    fig = go.Figure(data=go.Scatterpolar(r=values, theta=stats, fill='toself'))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True)), showlegend=False)
    return fig

# Home Page
if st.session_state.page == "home":
    st.title("Welcome")
    st.subheader("You can do 3 things – View Individual Stats, Comparative Stats, Battle Simulation")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Individual"):
            go_individual()
    with col2:
        if st.button("Comparative"):
            go_comparative()
    with col3:
        if st.button("Battle"):
            go_battle()

# Individual Page
elif st.session_state.page == "individual":
    st.title("Individual Pokémon Stats")
    if st.button("Back to Home"):
        go_home()

    search_name = st.text_input("Enter Pokémon Name:", placeholder="e.g., Pikachu")

    if search_name:
        result = df[df['name'].str.lower() == search_name.lower()]
        if not result.empty:
            pokemon = result.iloc[0]
            pokemon_name = pokemon['name']
            type1 = pokemon['type1'].capitalize() if pd.notna(pokemon['type1']) else "N/A"
            type2 = pokemon['type2'].capitalize() if pd.notna(pokemon['type2']) else "N/A"

            try:
                abilities_list = ast.literal_eval(pokemon['abilities'])
                abilities_clean = ", ".join(abilities_list)
            except:
                abilities_clean = pokemon['abilities']

            col_img, col_info = st.columns([1, 2])
            with col_img:
                image_path = f"images/pokemon/{pokemon_name.lower()}.png"
                if os.path.exists(image_path):
                    st.image(image_path, caption=pokemon_name)
                else:
                    st.warning(f"No image found for {pokemon_name}")

            with col_info:
                st.markdown(f"""
                <b>Primary Type:</b> {type1}  \n
                <b>Secondary Type:</b> {type2}  \n
                <b>Abilities:</b> {abilities_clean}
                """)

            st.markdown("### Radial Chart")
            st.plotly_chart(create_radial_plot(pokemon), use_container_width=True)
        else:
            st.error("Pokémon not found! Please check the name.")

# Comparative Page Placeholder
elif st.session_state.page == "comparative":
    st.title("Comparative Stats (Coming Soon)")
    if st.button("Back to Home"):
        go_home()

# Battle Page Placeholder
elif st.session_state.page == "battle":
    st.title("Battle Simulation (Coming Soon)")
    if st.button("Back to Home"):
        go_home()
