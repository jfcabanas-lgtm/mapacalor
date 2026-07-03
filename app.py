import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium

# Configura a página do Streamlit para usar a largura total da tela
st.set_page_config(layout="wide")

st.title("Painel de Fiscalização IPEM/RJ - Mapa de Calor")
st.markdown("Visualização geoespacial dos pontos fiscalizados pelo Instituto de Pesos e Medidas do Estado do Rio de Janeiro.")

# 1. Função para carregar os dados de fiscalização
# (Substitua esta simulação pelo carregamento real da sua planilha Excel ou CSV)
@st.cache_data
def carregar_dados_fiscalizacao():
    # Exemplo da estrutura de dados necessária (Latitude e Longitude são obrigatórias)
    dados = {
        'processo_sei': ['SEI-240001/0001', 'SEI-240001/0002', 'SEI-240001/0003', 'SEI-240001/0004'],
        'estabelecimento': ['Posto Combustível Alpha', 'Supermercado Beta', 'Balança Indústria Gama', 'Posto Combustível Delta'],
        'bairro': ['Centro', 'Copacabana', 'Madureira', 'Campo Grande'],
        'latitude': [-22.9068, -22.9714, -22.8808, -22.8944],  
        'longitude': [-43.1729, -43.1886, -43.2804, -43.5514],
        'irregularidades_encontradas': [2, 0, 5, 1] # Pode ser usado como o "peso" do calor
    }
    return pd.DataFrame(dados)

# Carrega o DataFrame
df_ipem = carregar_dados_fiscalizacao()

# 2. Configuração do mapa base centrado no Rio de Janeiro
coordenadas_rj = [-22.9068, -43.1729]
mapa = folium.Map(location=coordenadas_rj, zoom_start=11, tiles="OpenStreetMap")

# 3. Preparação dos dados para o Mapa de Calor
# Opção A: Calor por densidade simples (onde houve mais fiscalizações)
dados_calor = df_ipem[['latitude', 'longitude']].values.tolist()

# Opção B (Alternativa): Se quiser que o calor seja ditado pelo volume de irregularidades, descomente a linha abaixo:
# dados_calor = df_ipem[['latitude', 'longitude', 'irregularidades_encontradas']].values.tolist()

# 4. Adicionar a camada de calor ao mapa
HeatMap(
    data=dados_calor,
    radius=15,
    max_zoom=13,
    blur=10,
    min_opacity=0.5
).add_to(mapa)

# 5. Renderização dos elementos na interface do Streamlit
# Exibe o mapa interativo
st_folium(mapa, width=1100, height=550)

# Exibe a tabela de dados logo abaixo com opção de busca/filtro nativa
st.subheader("Dados Brutos das Fiscalizações")
st.dataframe(df_ipem, use_container_width=True)
