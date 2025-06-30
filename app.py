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
            st.session_state.battle_stage = "heading"  # Reset battle stage
            st.session_state.poke1 = None
            st.session_state.poke2 = None
            st.session_state.winner_message = None
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
    # Initialize session state for battle stages
    if 'battle_stage' not in st.session_state:
        st.session_state.battle_stage = "heading"
        st.session_state.poke1 = None
        st.session_state.poke2 = None
        st.session_state.winner_message = None
        st.session_state.selection_time = None

    # CSS and JavaScript for timed visibility
    st.markdown("""
    <style>
        .hidden { display: none; }
        .visible { display: block; }
        .fade-in {
            animation: fadeIn 0.5s ease-in-out forwards;
        }
        @keyframes fadeIn {
            0% { opacity: 0; }
            100% { opacity: 1; }
        }
    </style>
    <script>
        function showElement(id, delay) {
            setTimeout(() => {
                document.getElementById(id).classList.remove('hidden');
                document.getElementById(id).classList.add('visible', 'fade-in');
            }, delay);
        }
        function hideElement(id, delay) {
            setTimeout(() => {
                document.getElementById(id).classList.remove('visible');
                document.getElementById(id).classList.add('hidden');
            }, delay);
        }
    </script>
    """, unsafe_allow_html=True)

    # Heading
    st.markdown("<h1 id='battle-heading' class='visible'>Let's see who wins</h1>", unsafe_allow_html=True)

    # Show selection dropdowns after 5 seconds
    if st.session_state.battle_stage in ["heading", "selection"]:
        st.markdown("""
        <script>
            showElement('battle-selection', 5000);
        </script>
        """, unsafe_allow_html=True)
        
        with st.container():
            st.markdown("<div id='battle-selection' class='hidden'>", unsafe_allow_html=True)
            st.session_state.battle_stage = "selection"
            col1, col2 = st.columns(2)
            with col1:
                poke1 = st.selectbox("First Pokémon", sorted(df['name'].unique()), key='battle1', index=None)
                if poke1:
                    st.session_state.poke1 = poke1
            with col2:
                poke2 = st.selectbox("Second Pokémon", sorted(df['name'].unique()), key='battle2', index=None)
                if poke2:
                    st.session_state.poke2 = poke2
            st.markdown("</div>", unsafe_allow_html=True)

    # Once both Pokémon are selected, hide dropdowns and show names after 5 seconds
    if st.session_state.poke1 and st.session_state.poke2 and st.session_state.battle_stage in ["selection", "names"]:
        if st.session_state.battle_stage == "selection":
            st.session_state.battle_stage = "names"
            st.session_state.selection_time = True
        
        st.markdown("""
        <script>
            hideElement('battle-selection', 5000);
            showElement('battle-names', 5000);
        </script>
        """, unsafe_allow_html=True)
        
        st.markdown(f"<div id='battle-names' class='hidden' style='text-align: center; font-size: 24px;'>"
                    f"{st.session_state.poke1} vs {st.session_state.poke2}</div>", unsafe_allow_html=True)

        # Calculate winner
        winner, message = predict_battle(st.session_state.poke1, st.session_state.poke2, model, scaler, numerical_cols, type_table, df)
        st.session_state.winner_message = message

    # Show winner after 5 seconds
    if st.session_state.battle_stage == "names" and st.session_state.winner_message:
        st.markdown("""
        <script>
            showElement('battle-result', 5000);
        </script>
        """, unsafe_allow_html=True)
        
        st.markdown("<div id='battle-result' class='hidden'>", unsafe_allow_html=True)
        if st.session_state.winner_message.startswith("One or both"):
            st.error(st.session_state.winner_message)
        else:
            st.success(st.session_state.winner_message)
        st.session_state.battle_stage = "result"
        st.markdown("</div>", unsafe_allow_html=True)

    # Show back button after 2 seconds
    if st.session_state.battle_stage == "result":
        st.markdown("""
        <script>
            showElement('battle-back', 2000);
        </script>
        """, unsafe_allow_html=True)
        
        st.markdown("<div id='battle-back' class='hidden'>", unsafe_allow_html=True)
        if st.button("Back to Home"):
            st.session_state.page = "home"
            st.session_state.battle_stage = "heading"
            st.session_state.poke1 = None
            st.session_state.poke2 = None
            st.session_state.winner_message = None
            st.session_state.selection_time = None
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# Main app logic
if 'page' not in st.session_state:
    st.session_state.page = "home"

if st.session_state.page == "home":
    home_page()
elif st.session_state.page == "card":
    card_page()
elif st.session_state.page == "battle":
    battle_page()