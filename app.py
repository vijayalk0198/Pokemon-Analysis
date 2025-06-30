import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from PIL import Image

# Load the Pokémon dataset
@st.cache_data
def load_data():
    return pd.read_csv("data/pokemon.csv")

df = load_data()


# Streamlit App Setup
st.set_page_config(page_title="Pokemon Analysis", layout="centered")

# Navigation
if 'page' not in st.session_state:
    st.session_state.page = 'home'

def go_home():
    st.session_state.page = 'home'

def go_individual():
    st.session_state.page = 'individual'

def go_comparative():
    st.session_state.page = 'comparative'

def go_battle():
    st.session_state.page = 'battle'

# Home Page
def home():
    st.title('Welcome')
    st.subheader('You can do 3 things – View individual stats, comparative stats, battle simulation')

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
def individual():
    st.button("Back to Home", on_click=go_home)
    st.header("Enter Pokémon Name:")
    name = st.text_input("", key="search")

    if name:
        filtered = df[df['name'].str.lower() == name.lower()]

        if filtered.empty:
            st.error("Pokémon not found!")
        else:
            poke = filtered.iloc[0]

            col1, col2 = st.columns(2)
            with col1:
                try:
                    img = Image.open(f"images/{poke['name'].lower()}.png")
                    st.image(img, use_container_width=True)
                except:
                    st.write("Image not available")

            with col2:
                st.table({
                    "Pokémon Name": poke['name'],
                    "Primary Type": poke['type1'],
                    "Secondary Type": poke['type2'] if pd.notna(poke['type2']) else "N/A",
                    "Abilities": poke['abilities']
                })

            st.write("**Radial Chart:**")
            stats = [poke['hp'], poke['attack'], poke['defense'], poke['sp_attack'], poke['sp_defense'], poke['speed']]
            labels = ['HP', 'Attack', 'Defense', 'Sp. Atk', 'Sp. Def', 'Speed']

            fig = go.Figure(data=go.Scatterpolar(r=stats, theta=labels, fill='toself'))
            fig.update_layout(polar=dict(radialaxis=dict(visible=True)), showlegend=False)
            st.plotly_chart(fig)

# Comparative Page
def comparative():
    st.button("Back to Home", on_click=go_home)
    st.header("Comparative Stats")
    st.write("Select two Pokémon to compare")

    col1, col2 = st.columns(2)
    with col1:
        poke1 = st.selectbox("First Pokémon", sorted(df['name'].unique()), key='poke1')
    with col2:
        poke2 = st.selectbox("Second Pokémon", sorted(df['name'].unique()), key='poke2')

    if poke1 and poke2:
        df1 = df[df['name'] == poke1].iloc[0]
        df2 = df[df['name'] == poke2].iloc[0]

        stats = ['hp', 'attack', 'defense', 'sp_attack', 'sp_defense', 'speed']

        fig = go.Figure()
        fig.add_trace(go.Bar(x=stats, y=[df1[s] for s in stats], name=poke1))
        fig.add_trace(go.Bar(x=stats, y=[df2[s] for s in stats], name=poke2))

        fig.update_layout(barmode='group', title="Stat Comparison")
        st.plotly_chart(fig)

# Battle Simulation Page
def battle():
    st.button("Back to Home", on_click=go_home)
    st.header("Battle Simulation")
    st.write("Select two Pokémon to simulate a battle")

    col1, col2 = st.columns(2)
    with col1:
        poke1 = st.selectbox("First Pokémon", sorted(df['name'].unique()), key='battle1')
    with col2:
        poke2 = st.selectbox("Second Pokémon", sorted(df['name'].unique()), key='battle2')

    if poke1 and poke2:
        df1 = df[df['name'] == poke1].iloc[0]
        df2 = df[df['name'] == poke2].iloc[0]

        total1 = df1['base_total']
        total2 = df2['base_total']

        st.write(f"**{poke1} Total Stats:** {total1}")
        st.write(f"**{poke2} Total Stats:** {total2}")

        if total1 > total2:
            st.success(f"{poke1} is likely to win!")
        elif total2 > total1:
            st.success(f"{poke2} is likely to win!")
        else:
            st.info("It's a tie!")

# App Router
if st.session_state.page == 'home':
    home()
elif st.session_state.page == 'individual':
    individual()
elif st.session_state.page == 'comparative':
    comparative()
elif st.session_state.page == 'battle':
    battle()
