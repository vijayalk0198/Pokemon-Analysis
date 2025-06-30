import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# Load datasets
def load_data():
    pokemon = pd.read_csv("data/pokemon.csv")
    combats = pd.read_csv("data/combats.csv")
    return pokemon, combats

# Type advantage table
def create_type_advantage_table():
    types = ['Normal', 'Fire', 'Water', 'Electric', 'Grass', 'Ice', 'Fighting', 'Poison', 
             'Ground', 'Flying', 'Psychic', 'Bug', 'Rock', 'Ghost', 'Dragon', 'Dark', 'Steel', 'Fairy']
    advantage_data = {
        'Normal': [1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1],
        'Fire': [1, 0.5, 2, 1, 0.5, 0.5, 1, 1, 2, 1, 1, 0.5, 2, 1, 1, 1, 0.5, 0.5],
        'Water': [1, 0.5, 0.5, 2, 2, 0.5, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0.5, 1],
        'Electric': [1, 1, 1, 0.5, 1, 1, 1, 1, 2, 0.5, 1, 1, 1, 1, 1, 1, 0.5, 1],
        'Grass': [1, 2, 0.5, 0.5, 0.5, 2, 1, 2, 0.5, 2, 1, 2, 1, 1, 1, 1, 1, 1],
        'Ice': [1, 2, 1, 1, 1, 0.5, 2, 1, 1, 1, 1, 1, 2, 1, 1, 1, 2, 1],
        'Fighting': [1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 0.5, 0.5, 1, 1, 0.5, 1, 2],
        'Poison': [1, 1, 1, 1, 0.5, 1, 0.5, 0.5, 2, 1, 2, 0.5, 1, 1, 1, 1, 1, 0.5],
        'Ground': [1, 1, 2, 0, 2, 2, 1, 0.5, 1, 1, 1, 1, 0.5, 1, 1, 1, 1, 1],
        'Flying': [1, 1, 1, 2, 0.5, 2, 0.5, 1, 0, 1, 1, 0.5, 2, 1, 1, 1, 1, 1],
        'Psychic': [1, 1, 1, 1, 1, 1, 0.5, 1, 1, 1, 0.5, 2, 1, 2, 1, 2, 1, 1],
        'Bug': [1, 2, 1, 1, 0.5, 1, 0.5, 1, 0.5, 2, 1, 1, 2, 1, 1, 1, 1, 1],
        'Rock': [0.5, 0.5, 2, 1, 2, 1, 2, 0.5, 2, 0.5, 1, 1, 1, 1, 1, 1, 2, 1],
        'Ghost': [0, 1, 1, 1, 1, 1, 0, 0.5, 1, 1, 1, 0.5, 1, 2, 1, 2, 1, 1],
        'Dragon': [1, 0.5, 0.5, 0.5, 0.5, 2, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 2],
        'Dark': [1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 0, 2, 1, 0.5, 1, 0.5, 1, 2],
        'Steel': [0.5, 2, 1, 1, 0.5, 0.5, 2, 0, 2, 0.5, 0.5, 0.5, 0.5, 1, 0.5, 1, 0.5, 0.5],
        'Fairy': [1, 1, 1, 1, 1, 1, 0.5, 2, 1, 1, 1, 0.5, 1, 1, 0, 0.5, 2, 1]
    }
    return pd.DataFrame(advantage_data, index=types)

# Calculate type advantage
def get_type_advantage(type1, type2, type_table):
    if pd.isna(type1) or pd.isna(type2):
        return 'normal'
    val = type_table.loc[type1, type2]
    if val == 0:
        return 'no effect'
    elif val == 0.5:
        return 'not too effective'
    elif val == 1:
        return 'normal'
    elif val == 2:
        return 'effective'

# Train decision tree model
def train_model():
    pokemon, combats = load_data()
    type_table = create_type_advantage_table()
    
    # Prepare data
    combats['First_pokemon_name'] = combats['First_pokemon'].map(pokemon.set_index('pokedex_number')['name'])
    combats['Second_pokemon_name'] = combats['Second_pokemon'].map(pokemon.set_index('pokedex_number')['name'])
    combats['winner_first_label'] = (combats['Winner'] == combats['First_pokemon']).map({True: 'yes', False: 'no'})
    
    # Calculate stat differences
    for stat in ['attack', 'defense', 'hp', 'sp_attack', 'sp_defense', 'speed']:
        combats[f'First_{stat}'] = combats['First_pokemon_name'].map(pokemon.set_index('name')[stat])
        combats[f'Second_{stat}'] = combats['Second_pokemon_name'].map(pokemon.set_index('name')[stat])
        combats[f'Diff_{stat}'] = combats[f'First_{stat}'] - combats[f'Second_{stat}']
    
    # Type and legendary status
    combats['First_pokemon_type'] = combats['First_pokemon_name'].map(pokemon.set_index('name')['type1'])
    combats['Second_pokemon_type'] = combats['Second_pokemon_name'].map(pokemon.set_index('name')['type1'])
    combats['First_pokemon_legendary'] = combats['First_pokemon_name'].map(pokemon.set_index('name')['is_legendary']).astype(str)
    combats['Second_pokemon_legendary'] = combats['Second_pokemon_name'].map(pokemon.set_index('name')['is_legendary']).astype(str)
    combats['advantage'] = combats.apply(lambda x: get_type_advantage(x['First_pokemon_type'], x['Second_pokemon_type'], type_table), axis=1)
    
    # Prepare features
    features = ['Diff_attack', 'Diff_defense', 'Diff_hp', 'Diff_sp_attack', 'Diff_sp_defense', 'Diff_speed', 
                'First_pokemon_legendary', 'Second_pokemon_legendary', 'advantage']
    X = combats[features]
    X = pd.get_dummies(X, columns=['First_pokemon_legendary', 'Second_pokemon_legendary', 'advantage'], drop_first=True)
    y = combats['winner_first_label']
    
    # Scale numerical features
    scaler = StandardScaler()
    numerical_cols = ['Diff_attack', 'Diff_defense', 'Diff_hp', 'Diff_sp_attack', 'Diff_sp_defense', 'Diff_speed']
    X[numerical_cols] = scaler.fit_transform(X[numerical_cols])
    
    # Train model
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=2345)
    model = DecisionTreeClassifier(random_state=2345)
    model.fit(X_train, y_train)
    
    return model, scaler, numerical_cols, type_table

# Predict battle outcome
def predict_battle(pokemon1_name, pokemon2_name, model, scaler, numerical_cols, type_table, pokemon_df):
    # Get Pokémon data
    p1 = pokemon_df[pokemon_df['name'].str.lower() == pokemon1_name.lower()]
    p2 = pokemon_df[pokemon_df['name'].str.lower() == pokemon2_name.lower()]
    
    if p1.empty or p2.empty:
        return None, "One or both Pokémon not found!"
    
    p1, p2 = p1.iloc[0], p2.iloc[0]
    
    # Calculate features
    data = {
        'Diff_attack': p1['attack'] - p2['attack'],
        'Diff_defense': p1['defense'] - p2['defense'],
        'Diff_hp': p1['hp'] - p2['hp'],
        'Diff_sp_attack': p1['sp_attack'] - p2['sp_attack'],
        'Diff_sp_defense': p1['sp_defense'] - p2['sp_defense'],
        'Diff_speed': p1['speed'] - p2['speed'],
        'First_pokemon_legendary': str(p1['is_legendary']),
        'Second_pokemon_legendary': str(p2['is_legendary']),
        'advantage': get_type_advantage(p1['type1'], p2['type1'], type_table)
    }
    
    # Create DataFrame and encode categorical variables
    df = pd.DataFrame([data])
    df = pd.get_dummies(df, columns=['First_pokemon_legendary', 'Second_pokemon_legendary', 'advantage'], drop_first=True)
    
    # Ensure all columns from training are present
    expected_cols = model.feature_names_in_
    for col in expected_cols:
        if col not in df.columns:
            df[col] = 0
    df = df[expected_cols]
    
    # Scale numerical features
    df[numerical_cols] = scaler.transform(df[numerical_cols])
    
    # Predict
    prob = model.predict_proba(df)[0]
    winner = pokemon1_name if prob[1] > prob[0] else pokemon2_name
    confidence = max(prob)
    
    return winner, f"{winner} is likely to win with {confidence:.2%} confidence!"