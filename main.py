import ast
import zipfile
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import jupyter as jp
import os
from collections import Counter


# print('\n'.join(z.namelist()[:10]))

if not os.path.exists('data/'):
    os.makedirs('data/')

try:
    with zipfile.ZipFile('steam_games.zip', 'r') as zip_ref:
        zip_ref.extractall('data/')
except Exception:
    raise


df = pd.read_csv('data/steam_games.csv')

# print(df.columns)  ---- Se necessário, pode printar no terminal o Index de todas as colunas para melhor organização e criação do código;


# PERGUNTA #1

df['Release date'] = pd.to_datetime(df['Release date'], errors='coerce')

# Filtra jogos com pontuação válida
df_metacritic_validos = df.dropna(subset=['Metacritic score'])

# Ordena por Score (decrescente) e Data (crescente)
top_10_ordenado = df_metacritic_validos.sort_values(
    by=['Metacritic score', 'Release date'], 
    ascending=[False, True]
).head(10)

colunas_para_mostrar_p1 = ['Name', 'Metacritic score', 'Release date', 'Developers']

print("--- PERGUNTA 1: TOP 10 JOGOS NO STEAM ---")
print(top_10_ordenado[colunas_para_mostrar_p1])
print('\n')



### PERGUNTA 2 

df_tags_valid = df.dropna(subset=['Tags']).copy()   ## Drop linhas incompletas na coluna 'Tags', cria uma cópia para processamento
df_tags_valid['Tags'] = df_tags_valid['Tags'].str.split(',') ## Separa os objetos da coluna para melhor processamento

filtered_rpg = df_tags_valid[df_tags_valid['Tags'].apply(lambda x: 'RPG' in x)].copy() ## Filtra os jogos de Role-play, cria uma cópia para processamento

rpg_data = filtered_rpg[['DLC count', 'Positive', 'Negative', 'Screenshots', 'Movies']].copy()  ## Colunas de interesse para os jogos já filtrados

rpg_data['Screenshots'] = rpg_data['Screenshots'].fillna('').str.split(',').apply(len)
rpg_data['Movies'] = rpg_data['Movies'].fillna('').str.split(',').apply(len)

rpg_data['Materias de Demo'] = rpg_data['Screenshots'] + rpg_data['Movies']

final_data = rpg_data[['DLC count', 'Positive', 'Negative', 'Materias de Demo']]

print("--- PERGUNTA 2: MÉDIAS PARA JOGOS DE ROLE-PLAY ---")
print(final_data.mean())
print('\n')

print("--- PERGUNTA 2: MÁXIMAS PARA JOGOS DE ROLE-PLAY ---")
print(final_data.max())
print('\n')


# PERGUNTA 3

jogos_pagos = df[df['Price'] > 0]  ## Filtra jogos pagos 

num_of_games_by_publisher = jogos_pagos.groupby(['Publishers'], as_index=False).size() 
top5 = num_of_games_by_publisher.sort_values('size', ascending=False).head(5)   ## Ordena as empresas por ordem decrescente 

print("--- PERGUNTA 3: TOP 5 EMPRESAS COM MAIS JOGOS PAGOS NA PLATAFORMA ---")
print(top5)
print('\n')

jogos_pagos_top5 = jogos_pagos[jogos_pagos['Publishers'].isin(top5['Publishers'])]

print("--- PERGUNTA 3: MÉDIA DE AVALIAÇÕES POSITIVAS PARA O TOP 5 ---")
print(jogos_pagos_top5.groupby('Publishers')['Positive'].mean())
print('\n')

print("--- PERGUNTA 3: MEDIANA DE AVALIAÇÕES POSITIVAS PARA O TOP 5 ---")
print(jogos_pagos_top5.groupby('Publishers')['Positive'].median())
print('\n')




### PERGUNTA 4 

jogos_linux = df[df['Linux'] == True]
jogos_linux2022 = jogos_linux[jogos_linux['Release date'].dt.year == 2022]
jogos_linux2018 = jogos_linux[jogos_linux['Release date'].dt.year == 2018]

print("--- PERGUNTA 4: CRESCIMENTO DE JOGOS QUE SUPORTAM LINUX, DE 2018 À 2022 ---")
print(len(jogos_linux2022) - len(jogos_linux2018))
print('\n')

#### PERGUNTA 5 

df['Supported languages'] = df['Supported languages'].str.replace("K'iche", "'Kiche") ###correção de problema interno na tabela 
df['Supported languages'] = df['Supported languages'].apply(ast.literal_eval)

idiomas_suportados = []
for x in df['Supported languages']:
    idiomas_suportados += x

idiomas_calc = dict(Counter(idiomas_suportados))

novo_dict = {
    'Idioma': list(idiomas_calc.keys()),
    'Soma': list(idiomas_calc.values())
}

top_5_idiomas = pd.DataFrame(novo_dict).sort_values('Soma', ascending=False).head(5)

print("--- PERGUNTA 5: TOP 5 IDIOMAS MAIS COMUNS NOS JOGOS DA PLATAFORMA ---")
print(top_5_idiomas)
print('\n')



###GRÁFICO 1

num_of_mac = (df['Mac'] == True).sum()
num_of_wind = (df['Windows'] == True).sum()
num_of_linux = (df['Linux'] == True).sum()

total = num_of_mac + num_of_wind + num_of_linux

prcnt_mac = (num_of_mac / total) * 100
prcnt_wind = (num_of_wind / total) * 100
prcnt_linux = (num_of_linux / total) * 100

labels = ['Mac', 'Windows', 'Linux']
percents = [prcnt_mac, prcnt_wind, prcnt_linux]

plt.pie(percents, labels=labels, autopct='%1.1f%%', startangle=90)
plt.axis('equal')
plt.title('Percent of Operation Systems')
plt.show()


df_category_valid = df.dropna(subset=['Categories']).copy()
df_category_valid['Categories'] = df_category_valid['Categories'].apply(
    lambda x: x.split(',') if isinstance(x, str) else []
)

df_single_player = df_category_valid[
    df_category_valid['Categories'].apply(lambda x: 'Single-player' in x)
].copy()

df_single_player.dropna(subset=['Genres'], inplace=True)
df_single_player['Genres'] = df_single_player['Genres'].apply(
    lambda x: x.split(',') if isinstance(x, str) else []
)

df_sp_2010_2020 = df_single_player[
    (df_single_player['Release date'].dt.year >= 2010) & 
    (df_single_player['Release date'].dt.year <= 2020)
].copy()

def count_genre_by_year(df_data, genre_name):
    df_filtered = df_data[
        df_data['Genres'].apply(lambda x: genre_name in x)
    ]
    count_series = df_filtered['Release date'].dt.year.value_counts().sort_index()
    years = range(2010, 2021)
    df_count = pd.DataFrame(
        {'Year': years, genre_name: [count_series.get(year, 0) for year in years]}
    ).set_index('Year')
    return df_count

df_indie_count = count_genre_by_year(df_sp_2010_2020, 'Indie')
df_strategy_count = count_genre_by_year(df_sp_2010_2020, 'Strategy')

df_chart2 = df_indie_count.join(df_strategy_count, how='outer').fillna(0)

###GRÁFICO 2

df_category_valid = df.dropna(subset=['Categories']).copy()
df_category_valid['Categories'] = df_category_valid['Categories'].apply(
    lambda x: x.split(',') if isinstance(x, str) else []
)

df_single_player = df_category_valid[
    df_category_valid['Categories'].apply(lambda x: 'Single-player' in x)
].copy()

df_single_player.dropna(subset=['Genres'], inplace=True)
df_single_player['Genres'] = df_single_player['Genres'].apply(
    lambda x: x.split(',') if isinstance(x, str) else []
)

df_sp_2010_2020 = df_single_player[
    (df_single_player['Release date'].dt.year >= 2010) & 
    (df_single_player['Release date'].dt.year <= 2020)
].copy()

def count_genre_by_year(df_data, genre_name):
    df_filtered = df_data[
        df_data['Genres'].apply(lambda x: genre_name in x)
    ]
    count_series = df_filtered['Release date'].dt.year.value_counts().sort_index()
    years = range(2010, 2021)
    df_count = pd.DataFrame(
        {'Year': years, genre_name: [count_series.get(year, 0) for year in years]}
    ).set_index('Year')
    return df_count

df_indie_count = count_genre_by_year(df_sp_2010_2020, 'Indie')
df_strategy_count = count_genre_by_year(df_sp_2010_2020, 'Strategy')

df_chart2 = df_indie_count.join(df_strategy_count, how='outer').fillna(0)

total_indie = df_chart2['Indie'].sum()
total_strategy = df_chart2['Strategy'].sum()

print("\n--- GRÁFICO 2: TENDÊNCIA DE JOGOS SINGLE-PLAYER INDIE E ESTRATÉGIA (2010-2020) ---")
print(f"Total de jogos Indie (2010-2020): {total_indie}")
print(f"Total de jogos Estratégia (2010-2020): {total_strategy}")

plt.figure(figsize=(10, 6))

plt.plot(
    df_chart2.index, 
    df_chart2['Indie'], 
    marker='o', 
    linestyle='-', 
    color='blue', 
    label='Gênero Indie'
)

plt.plot(
    df_chart2.index, 
    df_chart2['Strategy'], 
    marker='s', 
    linestyle='--', 
    color='red', 
    label='Gênero Estratégia'
)

plt.title('Lançamento de Jogos Single-Player Indie e Estratégia (2010-2020)', fontsize=14)
plt.xlabel('Ano de Lançamento', fontsize=12)
plt.ylabel('Número Total de Jogos Lançados', fontsize=12)
plt.xticks(df_chart2.index)
plt.legend(title='Gênero')
plt.grid(True, linestyle=':', alpha=0.7)
plt.show()

###GRÁFICO 3

jogos_pagos = df[df['Price'] > 0].copy()

df_pagos_pos_2020 = jogos_pagos[
    jogos_pagos['Release date'].dt.year >= 2021
].copy()

contagem_por_ano = df_pagos_pos_2020['Release date'].dt.year.value_counts().sort_index()

df_chart3 = contagem_por_ano.reset_index()
df_chart3.columns = ['Ano', 'Total de Jogos Pagos']

total_jogos_pagos_pos_2020 = df_chart3['Total de Jogos Pagos'].sum()

print("\n--- GRÁFICO 3: CONTAGEM DE JOGOS PAGOS LANÇADOS APÓS 2020 ---")

if df_chart3.empty:
    print("Não foram encontrados jogos pagos lançados após 2020 no conjunto de dados.")
else:
    print(f"Total de jogos pagos (a partir de 2021): {total_jogos_pagos_pos_2020}") 

    plt.figure(figsize=(8, 5))

    bars = plt.bar(
        df_chart3['Ano'].astype(str),
        df_chart3['Total de Jogos Pagos'], 
        color='green', 
        alpha=0.7
    )

    for bar in bars:
        yval = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width()/2.0, 
            yval + 50,
            int(yval), 
            ha='center', 
            va='bottom', 
            fontsize=10
        )

    plt.title('Número de Jogos Pagos Lançados no Steam (A partir de 2021)', fontsize=14)
    plt.xlabel('Ano de Lançamento', fontsize=12)
    plt.ylabel('Total de Jogos Pagos', fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.6)
    plt.show()