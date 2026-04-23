import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from math import pi

# 1. DADOS BRUTOS DO EXCEL
try:
    df = pd.read_excel('dados_brutos.xlsx', index_col=0)
except FileNotFoundError:
    print("Erro: O arquivo 'dados.xlsx' não foi encontrado. Verifique o nome e a pasta.")
    exit()

# 2. NORMALIZAÇÃO LINEAR (Soma)
df_norm = df.copy().astype(float)

# Inverter critérios de Custo (Preço e Qualidade)
df_norm['Preço (R$)'] = 1 / df_norm['Preço (R$)']
df_norm['Qualidade (μm)'] = 1 / df_norm['Qualidade (μm)']

# Dividir cada valor pela soma da sua respectiva coluna
df_norm = df_norm / df_norm.sum()

# 3. CÁLCULO DOS PESOS GAUSSIANOS
medias = df_norm.mean()
desvios = df_norm.std(ddof=0) 
fator_gauss = desvios / medias
pesos = fator_gauss / fator_gauss.sum()

# 4. RANKING FINAL
ranking = df_norm.dot(pesos).sort_values(ascending=False)

# --- EXIBIÇÃO DE TABELAS NO TERMINAL ---
print("\n--- MATRIZ NORMALIZADA ---")
print(df_norm.round(4))

print("\n--- TABELA DE PESOS GAUSSIANOS ---")
df_pesos = pd.DataFrame({
    'Média': medias,
    'Desvio Padrão': desvios,
    'Fator L (Gauss)': fator_gauss,
    'Peso Final (%)': pesos * 100
})
print(df_pesos.round(4))

print("\n--- RANKING FINAL ---")
print(ranking.round(4))

# --- GRÁFICO 1: RANKING DE BARRAS ---
plt.figure(figsize=(10, 6))
colors = []
for nome in ranking.index:
    if 'Bambu' in nome:
        colors.append('royalblue')
    else:
        colors.append('lightgrey')

ranking_plot = ranking.sort_values(ascending=True)
colors_plot = []
for nome in ranking_plot.index:
    if 'Bambu' in nome:
        colors_plot.append('royalblue')
    else:
        colors_plot.append('lightgrey')

ranking_plot.plot(kind='barh', color=colors_plot)

plt.title('Ranking Final das Impressoras 3D (AHP Gaussiano)')
plt.xlabel('Pontuação Global')
plt.grid(axis='x', linestyle='--', alpha=0.6)
plt.tight_layout()
plt.savefig('ranking_final.png')

# --- GRÁFICO 2: RADAR (DESEMPENHO POR CRITÉRIO) ---
labels = list(df_norm.columns)
num_vars = len(labels)
top_labels = [ranking.index[0], ranking.index[1], 'Elegoo Saturn 4U']

plt.figure(figsize=(8, 8))
ax = plt.subplot(111, polar=True)
angles = [n / float(num_vars) * 2 * pi for n in range(num_vars)]
angles += angles[:1]

for i, imp in enumerate(top_labels):
    if imp in df_norm.index:
        values = df_norm.loc[imp].tolist()
        values += values[:1]
        ax.plot(angles, values, linewidth=2, label=imp)
        ax.fill(angles, values, alpha=0.1)

ax.set_theta_offset(pi / 2)
ax.set_theta_direction(-1)
plt.xticks(angles[:-1], labels)
plt.title('Perfil de Desempenho por Critério')
plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
plt.tight_layout()
plt.savefig('radar_desempenho.png')

# Exportar imagem para excel
ranking.to_excel("resultado_ranking.xlsx")

#Exportar tabelas para excel
with pd.ExcelWriter('Resultados_AHP_Gaussiano.xlsx') as writer:
    df_norm.to_excel(writer, sheet_name='Matriz Normalizada')
    df_pesos.to_excel(writer, sheet_name='Tabela de Pesos Gaussianos')