import requests
import pandas as pd
import streamlit as st
import plotly.express as px

# Configura tu API Key de Last.fm
API_KEY = 'fa1a9c506fba9490a68538c90dc27767'  # Sustituye con tu clave de API de Last.fm
BASE_URL = 'http://ws.audioscrobbler.com/2.0/'

# Función para obtener canciones populares
def obtener_top_canciones(region='Global', limite=10):
    """
    Obtiene canciones populares desde Last.fm API.
    Args:
        region (str): Región para la consulta ('Global' o nombre del país en inglés).
        limite (int): Número de canciones a obtener.
    Returns:
        pd.DataFrame: DataFrame con datos de canciones y artistas.
    """
    try:
        if region == 'Global':
            endpoint = f"{BASE_URL}?method=chart.gettoptracks&api_key={API_KEY}&format=json&limit={limite}"
        else:
            endpoint = f"{BASE_URL}?method=geo.gettoptracks&country={region}&api_key={API_KEY}&format=json&limit={limite}"

        response = requests.get(endpoint)
        if response.status_code == 200:
            data = response.json()
            tracks = data['tracks']['track'] if region == 'Global' else data['toptracks']['track']

            canciones = [{
                'Canción': track['name'],
                'Artista': track['artist']['name'],
                'URL': track['url'],
                'Reproducciones': track.get('playcount', 'N/A')
            } for track in tracks]

            return pd.DataFrame(canciones)
        else:
            st.error("Error al obtener datos de Last.fm.")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error al procesar los datos: {str(e)}")
        return pd.DataFrame()

# Lista de regiones disponibles (puedes ampliar según tus necesidades)
REGIONES = [
    "Global", "United States", "Mexico", "Spain", "France", "Brazil", "Argentina", 
    "Chile", "Colombia", "Peru", "Germany", "United Kingdom", "Italy", "Canada", 
    "Australia", "Japan", "South Korea"
]

# Configuración de la aplicación Streamlit
st.set_page_config(page_title="Top Canciones en Last.fm", page_icon="🎵", layout="wide")

# Barra lateral para configuración
st.sidebar.header("Configuración")
region = st.sidebar.selectbox("Selecciona una región", REGIONES)
limite = st.sidebar.slider("Número de canciones a mostrar", min_value=1, max_value=50, value=10)

# Botón para actualizar datos
if st.sidebar.button("Actualizar datos"):
    with st.spinner("Obteniendo datos desde Last.fm..."):
        df_canciones = obtener_top_canciones(region, limite)

    if not df_canciones.empty:
        # Mostrar tabla de datos
        st.subheader(f"Top {limite} canciones populares {'globalmente' if region == 'Global' else f'en {region}'}")
        st.dataframe(df_canciones)

        # Gráfico interactivo con Plotly
        st.subheader("🎶 Gráfico de Popularidad")
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

        # Enlaces para escuchar canciones
        st.subheader("🎧 Escucha las canciones:")
        for _, row in df_canciones.iterrows():
            st.markdown(
                f"▶️ [**{row['Canción']}** - {row['Artista']}]({row['URL']})",
                unsafe_allow_html=True
            )
    else:
        st.error("No se encontraron datos para la configuración seleccionada.")
