import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from PIL import Image
import streamlit as st
import pandas as pd
import os
import plotly.graph_objects as go
import ast  # For safely evaluating list-like strings
import base64

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
        showlegend=False,
        title=f"Stats for {pokemon['name']}",
        height=400
    )
    
    return fig

# Individual Page
def individual():
    st.button("Back to Home", on_click=go_home)
    # Search bar (Live search, no button)
    search_name = st.text_input("Enter Pokémon Name:", placeholder="e.g., Pikachu")

    if search_name:
        st.session_state.search_name = search_name
    else:
        st.session_state.search_name = ""

    # Display Pokémon details if valid search
    if st.session_state.search_name:
        result = df[df['name'].str.lower() == st.session_state.search_name.lower()]
    
    if not result.empty:
        pokemon = result.iloc[0]
        pokemon_name = pokemon['name']
        type1 = pokemon['type1'].capitalize() if pd.notna(pokemon['type1']) else "N/A"
        type2 = pokemon['type2'].capitalize() if pd.notna(pokemon['type2']) else "N/A"

        # Parse abilities safely
        try:
            abilities_list = ast.literal_eval(pokemon['abilities'])
            abilities_clean = ", ".join(abilities_list)
        except:
            abilities_clean = pokemon['abilities']

        st.markdown("---")

        # Layout: Image on Left, Info on Right
        col_img, col_info = st.columns([1, 2])
        with col_img:
            image_path = f"images/pokemon/{pokemon_name.lower()}.png"
            if os.path.exists(image_path):
                st.markdown(f"""
                        <div style='background-color:#f0f0f0; padding:10px; border-radius:8px; text-align:center'>
                        <img src='data:image/png;base64,{base64.b64encode(open(image_path, "rb").read()).decode()}' 
                        style='max-width:100%; height:auto;' alt='{pokemon_name}'>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.warning(f"No image found for {pokemon_name}")

        with col_info:
            st.markdown(f"""
            <table style='border-collapse: collapse; width: 100%;'>
                <tr>
                    <td style='border: 1px solid black; padding: 8px;'><b>Pokémon Name</b></td>
                    <td style='border: 1px solid black; padding: 8px;'>{pokemon_name}</td>
                </tr>
                <tr>
                    <td style='border: 1px solid black; padding: 8px;'><b>Primary Type</b></td>
                    <td style='border: 1px solid black; padding: 8px;'>{type1}</td>
                </tr>
                <tr>
                    <td style='border: 1px solid black; padding: 8px;'><b>Secondary Type</b></td>
                    <td style='border: 1px solid black; padding: 8px;'>{type2}</td>
                </tr>
                <tr>
                    <td style='border: 1px solid black; padding: 8px;'><b>Abilities</b></td>
                    <td style='border: 1px solid black; padding: 8px;'>{abilities_clean}</td>
                </tr>
            </table>
            """, unsafe_allow_html=True)

            st.markdown("<br><b>Radial Chart:</b>", unsafe_allow_html=True)
            st.plotly_chart(create_radial_plot(pokemon), use_container_width=True)

        st.markdown("---")

    else:
        st.error("Pokémon not found! Please check the name.")


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
