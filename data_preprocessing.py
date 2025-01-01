import pandas as pd
from datetime import datetime

def load_and_preprocess_data(file_path: str):
    df = pd.read_csv(file_path)

    # Convert birthdate and calculate age
    df['Birthdate'] = pd.to_datetime(df['Birthdate'], errors='coerce')
    df['Age'] = 2024 - df['Birthdate'].dt.year

    # Extract Year and Month from 'Patient Visit Date'
    df['Year'] = pd.to_datetime(df['Patient Visit Date'], format='%d-%m-%Y %H:%M').dt.year
    df['Month'] = pd.to_datetime(df['Patient Visit Date'], format='%d-%m-%Y %H:%M').dt.month

    # Create a new column 'Nationality_Group'
    df['Nationality_Group'] = ['Kuwaiti' if nat == 'Kuwaiti' else 'Non-Kuwaiti' for nat in df['Nationality']]

    return df

def filter_data(df, genders, years, nationalities):
    filtered_df = df[df['Year'].isin(years) & df['Sex'].isin(genders) & df['Nationality_Group'].isin(nationalities)]
    return filtered_df
