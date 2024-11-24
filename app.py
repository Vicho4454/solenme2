import pandas as pd
import requests
from bs4 import BeautifulSoup
import streamlit as st
import plotly.express as px

# Función para obtener canciones populares desde Spotify Charts
def obtener_top_spotify(region='global', tipo='daily', limite=10):
    """
    Extrae datos de Spotify Charts con Web Scraping.
    Args:
        region (str): Región para la consulta (ej. 'global', 'us').
        tipo (str): 'daily' o 'weekly'.
        limite (int): Número de canciones a obtener.
    Returns:
        pd.DataFrame: DataFrame con información de las canciones.
    """
    try:
        URL = f"https://spotifycharts.com/regional/{region}/{tipo}/latest"
        response = requests.get(URL)
        if response.status_code != 200:
            st.error(f"Error al acceder a Spotify Charts ({response.status_code}).")
            return pd.DataFrame()

        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find('table', {'class': 'chart-table'})
        if not table:
            st.error("No se encontró información en Spotify Charts.")
            return pd.DataFrame()

        rows = table.find_all('tr')[1:limite+1]  # Ignora la cabecera
        canciones = []
        for row in rows:
            cols = row.find_all('td')
            canciones.append({
                'Posición': cols[1].text.strip(),
                'Canción': cols[3].find('strong').text.strip(),
                'Artista': cols[3].find('span').text.strip(),
                'Reproducciones': cols[4].text.strip(),
                'URL': cols[3].find('a')['href']
            })

        return pd.DataFrame(canciones)
    except Exception as e:
        st.error(f"Error al procesar los datos: {str(e)}")
        return pd.DataFrame()

# Lista de regiones disponibles
REGIONES = [
    "global", "us", "mx", "es", "fr", "br", "ar", "cl", "co", "pe", "de", "gb",
    "it", "ca", "au", "jp", "kr", "se", "no", "fi"
]

# Configuración de la aplicación Streamlit
st.set_page_config(page_title="Top Canciones en Spotify Charts", page_icon="🎵", layout="wide")

# Barra lateral para configuración
st.sidebar.header("Configuración")
region = st.sidebar.selectbox("Selecciona una región", REGIONES)
tipo = st.sidebar.selectbox("Selecciona el tipo de lista", ["daily", "weekly"])
limite = st.sidebar.slider("Número de canciones a mostrar", min_value=1, max_value=50, value=10)

# Botón para actualizar datos
if st.sidebar.button("Actualizar datos"):
    with st.spinner("Obteniendo datos desde Spotify Charts..."):
        df_canciones = obtener_top_spotify(region, tipo, limite)

    if not df_canciones.empty:
        # Mostrar tabla de datos
        st.subheader(f"Top {limite} canciones {'globales' if region == 'global' else f'en {region}'} ({tipo})")
        st.dataframe(df_canciones)

        # Graficar popularidad de las canciones con Plotly
        st.subheader("🎶 Gráfico de Reproducciones")
        fig = px.bar(
            df_canciones,
            x='Reproducciones',
            y='Canción',
            orientation='h',
            color='Reproducciones',
            title="Reproducciones por Canción",
            height=600
        )
        fig.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            plot_bgcolor='#FFFFFF',
            paper_bgcolor='#FFFFFF',
            font_color='#002F6C'
        )
        st.plotly_chart(fig, use_container_width=True)

        # Mostrar enlaces para escuchar canciones
        st.subheader("🎧 Escucha las canciones:")
        for _, row in df_canciones.iterrows():
            st.markdown(
                f"▶️ [**{row['Canción']}** - {row['Artista']}]({row['URL']})",
                unsafe_allow_html=True
            )
    else:
        st.error("No se encontraron datos para la configuración seleccionada.")
