import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium

st.set_page_config(layout="wide")

st.title("Painel de Fiscalização IPEM/RJ - Mapa de Calor Real")
st.markdown("Alimentado dinamicamente a partir da planilha de vistorias por bairro.")

# 1. Dicionário de Coordenadas dos Bairros do RJ (Centro geográfico aproximado)
# Adicione ou ajuste as coordenadas dos bairros conforme a sua planilha exigir
COORDENADAS_BAIRROS = {
    'Centro': [-22.9068, -43.1729],
    'Copacabana': [-22.9714, -43.1886],
    'Ipanema': [-22.9836, -43.2044],
    'Botafogo': [-22.9519, -43.1807],
    'Flamengo': [-22.9376, -43.1764],
    'Tijuca': [-22.9329, -43.2372],
    'Méier': [-22.8997, -43.2778],
    'Madureira': [-22.8741, -43.3395],
    'Ilha do Governador': [-22.8145, -43.2104],
    'Barra da Tijuca': [-23.0003, -43.3659],
    'Jacarepaguá': [-22.9543, -43.3404],
    'Campo Grande': [-22.8944, -43.5514],
    'Bangu': [-22.8764, -43.4648],
    'Santa Cruz': [-22.9157, -43.6848],
    'Bonsucesso': [-22.8617, -43.2554],
    'Penha': [-22.8436, -43.2796],
    'Irajá': [-22.8306, -43.3242],
    'Realengo': [-22.8783, -43.4312]
}

# 2. Função para carregar e converter os dados da sua planilha
@st.cache_data
def carregar_e_processar_dados():
    try:
        # Se sua planilha for Excel, use: pd.read_excel("fiscalizacoes.xlsx")
        # Se for CSV, use o comando abaixo:
        df = pd.read_csv("fiscalizacoes.csv")
    except FileNotFoundError:
        # Caso o arquivo não seja encontrado, exibe uma mensagem de aviso amigável
        st.error("Arquivo de planilha ('fiscalizacoes.csv') não encontrado na pasta do projeto.")
        return pd.DataFrame()

    # Padroniza o texto para evitar erros de digitação (letras maiúsculas/minúsculas)
    # Garante que a busca no dicionário funcione de forma resiliente
    df['bairro_busca'] = df['bairro'].str.strip().str.title()

    # Mapeia as coordenadas correspondentes baseadas no nome do bairro
    df['latitude'] = df['bairro_busca'].map(lambda x: COORDENADAS_BAIRROS.get(x, [None, None])[0])
    df['longitude'] = df['bairro_busca'].map(lambda x: COORDENADAS_BAIRROS.get(x, [None, None])[1])

    # Remove linhas onde o bairro não foi encontrado no dicionário ou está em branco
    df_filtrado = df.dropna(subset=['latitude', 'longitude'])
    
    return df, df_filtrado

df_original, df_mapa = carregar_e_processar_dados()

if not df_mapa.empty:
    # 3. Configuração do mapa base centrado no Rio de Janeiro
    coordenadas_rj = [-22.9068, -43.1729]
    mapa = folium.Map(location=coordenadas_rj, zoom_start=11, tiles="OpenStreetMap")

    # 4. Extração das coordenadas para a camada de calor
    dados_calor = df_mapa[['latitude', 'longitude']].values.tolist()

    # 5. Adicionar a camada de calor ao mapa
    # O 'radius' controla o tamanho do borrão de calor por bairro
    HeatMap(
        data=dados_calor,
        radius=25,
        max_zoom=12,
        blur=15,
        min_opacity=0.4
    ).add_to(mapa)

    # 6. Renderização no Streamlit
    st_folium(mapa, width=1100, height=550)

    # Alerta caso algum bairro da planilha não tenha sido mapeado nas coordenadas nativas
    bairros_nao_encontrados = df_original[df_original['latitude'].isna()]['bairro'].unique()
    if len(bairros_nao_encontrados) > 0:
        st.warning(f"Os seguintes bairros da sua planilha não possuem coordenadas cadastradas no script e não apareceram no mapa: {', '.join(bairros_nao_encontrados)}")

    # Exibe a tabela de dados
    st.subheader("Registros Carregados da Planilha")
    st.dataframe(df_original[['estabelecimento', 'bairro']], use_container_width=True)

else:
    st.info("Aguardando upload ou inserção correta do arquivo de dados para renderizar o mapa.")
