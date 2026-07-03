import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium

st.set_page_config(layout="wide")

st.title("Painel de Fiscalização IPEM/RJ - Mapa de Calor")

# Dicionário de suporte para coordenadas
COORDENADAS_BAIRROS = {
    'Centro': [-22.9068, -43.1729], 'Copacabana': [-22.9714, -43.1886],
    'Ipanema': [-22.9836, -43.2044], 'Botafogo': [-22.9519, -43.1807],
    'Flamengo': [-22.9376, -43.1764], 'Tijuca': [-22.9329, -43.2372],
    'Méier': [-22.8997, -43.2778], 'Madureira': [-22.8741, -43.3395],
    'Ilha do Governador': [-22.8145, -43.2104], 'Barra da Tijuca': [-23.0003, -43.3659],
    'Jacarepaguá': [-22.9543, -43.3404], 'Campo Grande': [-22.8944, -43.5514],
    'Bangu': [-22.8764, -43.4648], 'Santa Cruz': [-22.9157, -43.6848]
}

# --- NOVA ÁREA DE UPLOAD DA PLANILHA ---
st.sidebar.header("Configurações de Dados")
arquivo_carregado = st.sidebar.file_uploader(
    "Carregue sua planilha de fiscalizações (Excel ou CSV)", 
    type=["csv", "xlsx"]
)

# Função modificada para processar o arquivo vindo da memória (Upload)
def processar_dados_carregados(arquivo):
    if arquivo.name.endswith('.csv'):
        df = pd.read_csv(arquivo)
    else:
        df = pd.read_excel(arquivo)
        
    df.columns = df.columns.str.strip().str.lower()
    
    if 'estabelecimento' not in df.columns or 'bairro' not in df.columns:
        st.error("A planilha precisa conter as colunas 'estabelecimento' e 'bairro'.")
        return pd.DataFrame(), pd.DataFrame()
        
    df['bairro_busca'] = df['bairro'].astype(str).str.strip().str.title()
    df['latitude'] = df['bairro_busca'].map(lambda x: COORDENADAS_BAIRROS.get(x, [None, None])[0])
    df['longitude'] = df['bairro_busca'].map(lambda x: COORDENADAS_BAIRROS.get(x, [None, None])[1])
    
    df_filtrado = df.dropna(subset=['latitude', 'longitude'])
    return df, df_filtrado

# --- FLUXO DE EXECUÇÃO SEGURO ---
if arquivo_carregado is not None:
    df_original, df_mapa = processar_dados_carregados(arquivo_carregado)
    
    if not df_mapa.empty:
        coordenadas_rj = [-22.9068, -43.1729]
        mapa = folium.Map(location=coordenadas_rj, zoom_start=11)
        
        dados_calor = df_mapa[['latitude', 'longitude']].values.tolist()
        HeatMap(dados_calor, radius=25, blur=15, min_opacity=0.4).add_to(mapa)
        
        st_folium(mapa, width=1100, height=550)
        
        st.subheader("Dados Carregados")
        st.dataframe(df_original[['estabelecimento', 'bairro']], use_container_width=True)
else:
    st.info("👋 Para visualizar o mapa de calor, utilize a barra lateral à esquerda para carregar o seu arquivo de fiscalizações (.csv ou .xlsx).")
