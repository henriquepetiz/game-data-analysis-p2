
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import zipfile
import os

z = zipfile.ZipFile('steam_games.zip')

print('\n'.join(z.namelist()[:10]))

if not os.path.exists('data/'):
    os.makedirs('data/')

try:
    with zipfile.ZipFile('steam_games.zip', 'r') as zip_ref:
        zip_ref.extractall('data/')
except FileNotFoundError:
    pass
except Exception:
    pass


### Printa as colunas para melhor organização do código

df = pd.read_csv('data/steam_games.csv')
print(df.columns)


# 1. Limpeza e Padronização de Colunas Essenciais
df['Release date'] = pd.to_datetime(df['Release date'], errors='coerce')
df.rename(columns={'Release date': 'release_date'}, inplace=True)
df['Metacritic score'] = pd.to_numeric(df['Metacritic score'], errors='coerce')

# Limpeza e criação de colunas para P2 (Role-playing)
df['DLC count'] = pd.to_numeric(df['DLC count'], errors='coerce')
df['Positive'] = pd.to_numeric(df['Positive'], errors='coerce')
df['Negative'] = pd.to_numeric(df['Negative'], errors='coerce')
df['Screenshots'] = pd.to_numeric(df['Screenshots'], errors='coerce').fillna(0)
df['Movies'] = pd.to_numeric(df['Movies'], errors='coerce').fillna(0)

# Coluna 'Materiais de Demonstração' (criação crucial antes do 'explode')
df['Materiais de Demonstração'] = df['Screenshots'] + df['Movies']

# Separa gêneros em listas e cria o DF explodido para análises baseadas em gênero
df['Genres'] = df['Genres'].str.split(';').str.strip()
df_exploded_genres = df.explode('Genres')




# Filtra jogos com pontuação válida
df_metacritic_validos = df.dropna(subset=['Metacritic score']).copy()

# Ordena por Score (decrescente) e Data (crescente)
top_10_ordenado = df_metacritic_validos.sort_values(
    by=['Metacritic score', 'release_date'], 
    ascending=[False, True]
).head(10)

# 3. Exibe o resultado
colunas_para_mostrar_p1 = ['Name', 'Metacritic score', 'release_date', 'Developers']

print("--- PERGUNTA 1: TOP 10 JOGOS NO STEAM ---")
with pd.option_context('display.max_columns', None, 'display.width', 1000):
    print(top_10_ordenado[colunas_para_mostrar_p1])

# 1. Filtra jogos de Role-playing (usa o DF explodido)
df_rpg = df_exploded_genres[df_exploded_genres['Genres'] == 'Role-playing'].copy()

# 2. Colunas para cálculo
metricas_rpg = ['DLC count', 'Positive', 'Negative', 'Materiais de Demonstração']

# 3. Calcula e exibe Média e Máximo
print("\n\n--- PERGUNTA 2: DADOS DE ROLE-PLAYING GAMES ---")
print("Média:")
print(df_rpg[metricas_rpg].mean().round(1)) 
print("\nMáximo:")
print(df_rpg[metricas_rpg].max())
