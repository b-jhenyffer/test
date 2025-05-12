import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

# Carregar o arquivo CSV
df_la_ = pd.read_csv('/Users/jhenyfferborges/Documents/DSW_analysis/projeto_dsw/clean_data/df_la_2025-05-10.csv')

# Certifique-se de que a coluna de datas esteja no formato datetime
df_la_['Sales Order Date'] = pd.to_datetime(df_la_['Sales Order Date'])

# Criar mapeamento de meses
meses_ordem = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
#########
# Sidebar com filtro de país
# Sidebar com filtro de país
st.sidebar.header("Filtros")
paises_disponiveis = sorted(df_la_['Sold To Country Code Description'].dropna().unique())
opcoes_filtro = ['Latin America'] + paises_disponiveis
pais_selecionado = st.sidebar.selectbox("Selecione a região", opcoes_filtro)

# Aplicar filtro (ou não) com base na seleção
if pais_selecionado == 'Latin America':
    df_filtrado = df_la_.copy()
else:
    df_filtrado = df_la_[df_la_['Sold To Country Code Description'] == pais_selecionado]

# ---------------------------
# Adicionando o filtro de Ano
# ---------------------------

# Extraindo o ano da coluna 'Sales Order Date'
df_filtrado['Ano'] = pd.DatetimeIndex(df_filtrado['Sales Order Date']).year

# Definindo as opções para o filtro de ano
anos_disponiveis = sorted(df_filtrado['Ano'].unique())
opcoes_anos = ["2024 - 2025"] + anos_disponiveis

# Inserindo o filtro de ano no sidebar
ano_selecionado_sidebar = st.sidebar.selectbox("Selecione o Ano", opcoes_anos)

# Aplicando o filtro de ano
if ano_selecionado_sidebar == "2024 - 2025":
    df_filtrado = df_filtrado[df_filtrado['Ano'].isin([2024, 2025])]
else:
    df_filtrado = df_filtrado[df_filtrado['Ano'] == int(ano_selecionado_sidebar)]


########


# Definir os períodos
inicio_periodo_24 = '2024-01-01'
fim_periodo_24 = '2024-12-31'
inicio_periodo_25 = '2025-01-01'
fim_periodo_25 = '2025-12-31'

# Filtrar por ano
df_24 = df_filtrado[(df_filtrado['Sales Order Date'] >= inicio_periodo_24) & (df_filtrado['Sales Order Date'] <= fim_periodo_24)].copy()
df_25 = df_filtrado[(df_filtrado['Sales Order Date'] >= inicio_periodo_25) & (df_filtrado['Sales Order Date'] <= fim_periodo_25)].copy()

# Adicionar coluna de mês
df_24['Mes'] = pd.Categorical(df_24['Sales Order Date'].dt.strftime('%b'), categories=meses_ordem, ordered=True)
df_25['Mes'] = pd.Categorical(df_25['Sales Order Date'].dt.strftime('%b'), categories=meses_ordem, ordered=True)

# Agrupar e contar ordens únicas por mês
ordens_24 = df_24.groupby('Mes')['SAP Sales Order Number'].nunique()
ordens_25 = df_25.groupby('Mes')['SAP Sales Order Number'].nunique()

valores_24 = [ordens_24.get(mes, 0) for mes in meses_ordem]
valores_25 = [ordens_25.get(mes, 0) for mes in meses_ordem]

#-----------------------------------------------------------------------

# Calcular o valor máximo de ordens (sem filtro) para fixar o eixo Y
df_la_['Mes'] = pd.Categorical(df_la_['Sales Order Date'].dt.strftime('%b'), categories=meses_ordem, ordered=True)
ordens_max_24 = df_la_[(df_la_['Sales Order Date'] >= inicio_periodo_24) & (df_la_['Sales Order Date'] <= fim_periodo_24)].groupby('Mes')['SAP Sales Order Number'].nunique()
ordens_max_25 = df_la_[(df_la_['Sales Order Date'] >= inicio_periodo_25) & (df_la_['Sales Order Date'] <= fim_periodo_25)].groupby('Mes')['SAP Sales Order Number'].nunique()
y_max = max(ordens_max_24.max(), ordens_max_25.max()) * 1.2  # margem de 20% para os rótulos

# Criar gráfico de ordens por mês
fig1 = go.Figure()
fig1.add_trace(go.Bar(x=meses_ordem, y=valores_25, name='Ordens (2025)', marker_color='#0070C0', text=valores_25, textposition='outside'))
fig1.add_trace(go.Bar(x=meses_ordem, y=valores_24, name='Ordens (2024)', marker_color='#e9e9e9', text=valores_24, textposition='outside'))

# Atualizar layout com eixo Y fixo
fig1.update_layout(
    barmode='group',
    title=f'Total de Ordens por Mês (2024 vs 2025) - {pais_selecionado}',
    title_x=0,
    template='plotly_white',
    legend_title='',
    legend=dict(x=0, y=1, orientation='h', xanchor='center', yanchor='bottom'),
    xaxis_showgrid=False,
    yaxis_showgrid=False,
    yaxis_visible=False,
    yaxis_range=[0, y_max],  # Eixo Y fixo
    margin=dict(t=100)  # Aumentar margem superior para criar espaço
)


#-------------------------------------------------------------------


# Criar gráfico de ordens por setor (barras horizontais empilhadas)
ordens_setor_24 = df_filtrado[df_filtrado['Sales Order Date'].dt.year == 2024].groupby('Setor')['SAP Sales Order Number'].nunique().sort_values(ascending=True) # Ordenar por valor
ordens_setor_25 = df_filtrado[df_filtrado['Sales Order Date'].dt.year == 2025].groupby('Setor')['SAP Sales Order Number'].nunique().sort_values(ascending=True) # Ordenar por valor

fig_setor_empilhado = go.Figure()
fig_setor_empilhado.add_trace(go.Bar(
    x=ordens_setor_24.values,
    y=ordens_setor_24.index,
    orientation='h', # barras horizontais
    marker_color='rgba(0, 112, 192, 0.2)', # Cor com 50% de transparência
    name='Ordens (2024)',
    text=ordens_setor_24.values,
    textposition='inside'
))

fig_setor_empilhado.add_trace(go.Bar(
    x=ordens_setor_25.values,
    y=ordens_setor_25.index,
    orientation='h',  # barras horizontais
    marker_color='#0070C0',
    name='Ordens (2025)',
    text=ordens_setor_25.values,
    textposition='inside'
))

fig_setor_empilhado.update_layout(
    barmode='stack',
    title=f'Total de Ordens por Setor - {pais_selecionado}',
    title_x=0,
    template='plotly_white',
    legend_title='',
    legend=dict(x=0, y=1, orientation='h', xanchor='center', yanchor='bottom'),
    xaxis_showgrid=False,
    yaxis_showgrid=False,
    xaxis_visible=False, # Ocultar eixo X
    margin=dict(l=100, r=40, t=100, b=40),  # Aumentar margem superior para criar espaço
    height=500
)

#----------------------------------------------------------------------


# Criar gráfico de ordens por produto (barras horizontais empilhadas)
ordens_produto_24 = df_filtrado[df_filtrado['Sales Order Date'].dt.year == 2024].groupby('Product Name')['SAP Sales Order Number'].nunique().sort_values(ascending=False) # Ordenar por valor
ordens_produto_25 = df_filtrado[df_filtrado['Sales Order Date'].dt.year == 2025].groupby('Product Name')['SAP Sales Order Number'].nunique().sort_values(ascending=False) # Ordenar por valor

# Consolidar os dados de 2024 e 2025 em um DataFrame único
df_consolidado = pd.DataFrame({
    '2024': ordens_produto_24,
    '2025': ordens_produto_25
}).fillna(0)  # Preencher com 0 onde não há valor

# Adicionar uma coluna com o total de ordens para facilitar a ordenação
df_consolidado['Total'] = df_consolidado['2024'] + df_consolidado['2025']

# Ordenar os produtos pelo total de ordens de forma decrescente
df_consolidado = df_consolidado.sort_values(by='Total', ascending=True)

# Recriar o gráfico com a nova ordem
fig_produto_empilhado = go.Figure()

fig_produto_empilhado.add_trace(go.Bar(
    x=df_consolidado['2024'].values,
    y=df_consolidado.index,
    orientation='h',
    marker_color='rgba(0, 112, 192, 0.2)',
    name='Ordens (2024)',
    text=df_consolidado['2024'].values,
    textposition='inside'
))

fig_produto_empilhado.add_trace(go.Bar(
    x=df_consolidado['2025'].values,
    y=df_consolidado.index,
    orientation='h',
    marker_color='#0070C0',
    name='Ordens (2025)',
    text=df_consolidado['2025'].values,
    textposition='inside'
))

fig_produto_empilhado.update_layout(
    barmode='stack',
    title=f'Total de Ordens por Produto - {pais_selecionado}',
    title_x=0,
    template='plotly_white',
    legend_title='',
    legend=dict(x=0, y=1, orientation='h', xanchor='center', yanchor='bottom'),
    xaxis_showgrid=False,
    yaxis_showgrid=False,
    xaxis_visible=False,
    margin=dict(l=100, r=40, t=100, b=40),
    height=500
)
#----------------------------------------------------------------------
import streamlit as st
import plotly.express as px
import pandas as pd

# 🔍 **Removendo duplicidades de ordens**
# Cada combinação de 'Product Name' e 'SAP Sales Order Number' deve ser única
df_filtrado = df_filtrado.drop_duplicates(subset=['Product Name', 'SAP Sales Order Number'])

# Contando o número total de vendas por setor, nome do produto e ano
df_total = df_filtrado.groupby(['Setor', 'Product Name', 'Ano'])['SAP Sales Order Number'].count().reset_index()

# Calculando a proporção de vendas dentro de cada setor e ano
df_total['Proporção'] = df_total.groupby(['Setor', 'Ano'])['SAP Sales Order Number'].transform(lambda x: x / x.sum())

# Definindo um mapa de cores personalizado
color_map = {
    'SPSS Statistics': '#005A9E',
    'Aspera': '#0070C0',
    'Cognos Analytics': '#3399FF',
    'Blueworks Live': '#D3D3D3',
    'MaaS360': '#D3D3D3',
    'ILOG CPLEX': '#D3D3D3',
    'Learning - Data Science': '#D3D3D3'
}

# Definindo a ordem das categorias
category_orders = {
    'Setor': ['Distribution Sector', 'Communication Sector', 'Public Sector', 'Health', 'Education', 'Financial Services'],
    'Product Name': ['SPSS Statistics', 'Aspera', 'Cognos Analytics', 'Blueworks Live', 'MaaS360', 'ILOG CPLEX', 'Learning - Data Science']
}

# Filtrando o DataFrame com base no ano selecionado no sidebar
if ano_selecionado_sidebar == "2024 - 2025":
    df_total = df_total[df_total['Ano'].isin([2024, 2025])]
else:
    df_total = df_total[df_total['Ano'] == int(ano_selecionado_sidebar)]

# Criando o gráfico de barras empilhadas 100%
fig = px.bar(df_total, 
             x='Proporção', 
             y='Setor', 
             color='Product Name', 
             orientation='h', 
             title=f'Proporção de Vendas por Setor e Produto - {ano_selecionado_sidebar}', 
             text='SAP Sales Order Number', 
             color_discrete_map=color_map, 
             category_orders=category_orders)

# Removendo os títulos dos eixos
fig.update_layout(
    xaxis_title=None,
    yaxis_title=None
)

# -------------------------
# ORDENS ÚNICAS POR PRODUTO
# -------------------------

if ano_selecionado_sidebar == "2024 - 2025":
    # Contar ordens únicas para ambos os anos
    ordens_unicas = df_filtrado[df_filtrado['Ano'].isin([2024, 2025])].groupby('Product Name')['SAP Sales Order Number'].nunique().sort_values(ascending=False)
else:
    # Contar ordens únicas para o ano selecionado
    ordens_unicas = df_filtrado[df_filtrado['Ano'] == int(ano_selecionado_sidebar)].groupby('Product Name')['SAP Sales Order Number'].nunique().sort_values(ascending=False)

# Convertendo para DataFrame para fácil manipulação
df_ordens_unicas = ordens_unicas.reset_index().rename(columns={'SAP Sales Order Number': 'Ordens Únicas'})

# Calculando o total de ordens únicas
total_ordens = df_ordens_unicas['Ordens Únicas'].sum()

# Adicionando uma linha com o total
df_total_row = pd.DataFrame([{'Product Name': 'Total', 'Ordens Únicas': total_ordens}])
df_ordens_unicas = pd.concat([df_ordens_unicas, df_total_row], ignore_index=True)

# Mostrando o resultado no Streamlit


#-------------------------------------


# # Filtrar apenas clientes novos e os anos de 2024 e 2025
# df_novos_clientes = df_filtrado[(df_filtrado['Unique'] == 'y') & 
#                                 (df_filtrado['Sales Order Date'].dt.year.isin([2024, 2025]))]

# # Remover duplicidades de ordens
# df_novos_clientes = df_novos_clientes.drop_duplicates(subset=['SAP Sales Order Number'])

# # Contar as ordens únicas por ano
# ordens_2024 = df_novos_clientes[df_novos_clientes['Sales Order Date'].dt.year == 2024]['SAP Sales Order Number'].nunique()
# ordens_2025 = df_novos_clientes[df_novos_clientes['Sales Order Date'].dt.year == 2025]['SAP Sales Order Number'].nunique()

# # Definir o valor máximo do eixo Y com uma margem de 10%
# y_max = max(ordens_2024, ordens_2025) * 1.1

# # Criar o gráfico
# fig_novos_clientes = go.Figure()

# # Barras empilhadas para cada ano
# fig_novos_clientes.add_trace(go.Bar(
#     x=['2024'],
#     y=[ordens_2024],
#     name='Ordens 2024',
#     marker_color='rgba(0, 112, 192, 0.2)',  # Cor atualizada para 2024
#     text=[ordens_2024],
#     textposition='inside'
# ))

# fig_novos_clientes.add_trace(go.Bar(
#     x=['2025'],
#     y=[ordens_2025],
#     name='Ordens 2025',
#     marker_color='#0070C0',  # Cor atualizada para 2025
#     text=[ordens_2025],
#     textposition='inside'
# ))

# # Layout do gráfico no padrão que você pediu, ajustando o eixo X
# fig_novos_clientes.update_layout(
#     barmode='group',
#     title=f'Total de Ordens por Ano (2024 vs 2025) - {pais_selecionado}',
#     title_x=0,
#     template='plotly_white',
#     legend_title='',
#     legend=dict(x=0, y=1, orientation='h', xanchor='center', yanchor='bottom'),
#     xaxis_showgrid=False,
#     yaxis_showgrid=False,
#     yaxis_visible=False,
#     yaxis_range=[0, y_max],  # Eixo Y fixo com margem
#     margin=dict(t=100, l=60)  # Aumentar margem superior e margem à esquerda
# )



#-----------------------------------------------------------------------



# Exibir gráficos no Streamlit com padrão alinhado
st.title("Ecommerce - Análise de Ordens")
st.divider()
st.plotly_chart(fig1, use_container_width=True)
st.text('Numero Total de ordens (Latin America) YtD: ')
st.text('2024: 44')
st.text('2025: 50')

# Expander para comentários do gráfico 1
#with st.expander("Comentários - Gráfico de Ordens por Mês"):
#    comentario1 = st.text_area('')

st.divider()
st.plotly_chart(fig_setor_empilhado, use_container_width=True)

# Expander para comentários do gráfico 2
#with st.expander("Comentários - Gráfico de Ordens por Setor"):
#    comentario2 = st.text_area(" ")
st.divider()
st.plotly_chart(fig_produto_empilhado, use_container_width=True)



st.plotly_chart(fig)
# Mostrando os resultados no Streamlit
st.dataframe(ordens_unicas.reset_index().rename(columns={'SAP Sales Order Number': 'Ordens Únicas'}))


