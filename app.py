import streamlit as st
import pandas as pd
import plotly.express as px
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials

# Configura tus credenciales de Spotify
CLIENT_ID = 'bbabd18955d143f9b0839faee832f0f0'
CLIENT_SECRET = '1208ef2a6ebf4ddba1d02083297c16ef'
# Configura autenticación con la API de Spotify
auth_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = Spotify(auth_manager=auth_manager)

# Función para obtener canciones y artistas populares (Global o por región)
def obtener_top_canciones(region='Global', limite=10):
    """
    Obtiene las canciones más populares globalmente o en una región específica.
    Args:
        region (str): Código de región ISO (ej. 'US', 'MX') o 'Global' para datos globales.
        limite (int): Número de canciones a obtener.
    Returns:
        pd.DataFrame: DataFrame con los datos de canciones y artistas.
    """
    try:
        # Determina si la consulta es global o específica por región
        if region == 'Global':
            resultados = sp.search(q='top', type='track', limit=limite)
        else:
            resultados = sp.search(q='top', type='track', market=region, limit=limite)
        
        canciones = []
        for track in resultados.get('tracks', {}).get('items', []):
            canciones.append({
                'Canción': track['name'],
                'Artista': track['artists'][0]['name'],
                'Popularidad': track['popularity'],
                'URL': track['external_urls']['spotify']
            })
        
        if not canciones:
            st.warning("No se encontraron canciones para la configuración seleccionada.")
        return pd.DataFrame(canciones)
    
    except Exception as e:
        st.error(f"Error al obtener datos de Spotify: {str(e)}")
        return pd.DataFrame()

# Lista completa de códigos de región permitidos con opción Global
REGIONES = [
    "Global", "US", "MX", "ES", "FR", "BR", "AR", "CL", "CO", "PE", "UY", "VE",
    "DE", "GB", "IT", "NL", "AU", "CA", "SE", "NO", "FI", "DK", "IE", 
    "JP", "KR", "SG", "HK", "PH", "ID", "MY", "TH", "VN", "TW"
]

# Estilo general de la aplicación
st.set_page_config(page_title="Top Canciones en Spotify", page_icon="🎵", layout="wide")

# Inserción del logo de la universidad (modifica 'image.png' con el nombre del archivo proporcionado)
st.sidebar.image('image.png', use_column_width=True)

# Título y descripción de la aplicación con estilo ajustado
st.markdown("<h1 style='color: #002F6C;'>🎵 Top Canciones Populares en Spotify 🎵</h1>", unsafe_allow_html=True)
st.markdown("""
<div style='color: #002F6C; font-size: 18px;'>
Explora las canciones más populares en Spotify a nivel global o en diferentes regiones del mundo.
Selecciona una región o la opción "Global" para obtener resultados sin restricciones.
</div>
""", unsafe_allow_html=True)

# Configuración en la barra lateral con colores ajustados
st.sidebar.header("Configuración")
region = st.sidebar.selectbox("Selecciona una región", REGIONES)
limite = st.sidebar.slider("Número de canciones a mostrar", min_value=1, max_value=50, value=10)

# Botón para actualizar datos
if st.sidebar.button("Actualizar datos"):
    with st.spinner("Obteniendo datos desde Spotify..."):
        df_canciones = obtener_top_canciones(region, limite)

    if not df_canciones.empty:
        # Mostrar tabla de datos con estilo moderno
        st.subheader(f"Top {limite} canciones populares {'globalmente' if region == 'Global' else f'en la región {region}'}")
        st.dataframe(df_canciones.style.set_properties(**{'text-align': 'left'}).set_table_styles([dict(selector='th', props=[('text-align', 'left')])]))

        # Graficar popularidad de las canciones con Plotly, colores ajustados
        st.subheader("🎶 Gráfico Interactivo de Popularidad")
        fig = px.bar(
            df_canciones, 
            x='Popularidad', 
            y='Canción', 
            orientation='h', 
            color='Popularidad',
            color_continuous_scale=['#002F6C', '#D4AF37'], 
            title="Popularidad de las Canciones",
            height=600  # Aumenta la altura del gráfico
        )
        fig.update_layout(
            yaxis={'categoryorder': 'total ascending'}, 
            plot_bgcolor='#FFFFFF',
            paper_bgcolor='#FFFFFF',
            font_color='#002F6C'
        )
        st.plotly_chart(fig, use_container_width=True)  # Expande el gráfico al ancho completo

        # Cálculos Estadísticos
        promedio_popularidad = df_canciones['Popularidad'].mean()
        desviacion_popularidad = df_canciones['Popularidad'].std()
        mediana_popularidad = df_canciones['Popularidad'].median()

        # Mostrar estadísticas calculadas
        st.markdown(f"### 📊 Estadísticas de Popularidad")
        st.write(f"**Promedio de Popularidad**: {promedio_popularidad:.2f}")
        st.write(f"**Desviación Estándar de Popularidad**: {desviacion_popularidad:.2f}")
        st.write(f"**Mediana de Popularidad**: {mediana_popularidad:.2f}")

        # Gráfico de Línea - Popularidad Promedio
        st.subheader("📈 Gráfico de Línea - Popularidad Promedio por Canción")
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(
            x=df_canciones['Canción'],
            y=[promedio_popularidad] * len(df_canciones),
            mode='lines',
            name='Promedio de Popularidad',
            line=dict(color='#D4AF37', dash='dash')
        ))
        fig_line.update_layout(
            title='Popularidad Promedio por Canción',
            xaxis_title='Canción',
            yaxis_title='Popularidad',
            plot_bgcolor='#FFFFFF',
            paper_bgcolor='#FFFFFF',
            font_color='#002F6C'
        )
        st.plotly_chart(fig_line, use_container_width=True)

        # Histograma - Distribución de la Popularidad
        st.subheader("📊 Histograma - Distribución de la Popularidad")
        fig_hist = px.histogram(
            df_canciones, 
            x='Popularidad', 
            nbins=10, 
            title='Distribución de la Popularidad de Canciones',
            color_discrete_sequence=['#002F6C']
        )
        fig_hist.update_layout(
            plot_bgcolor='#FFFFFF',
            paper_bgcolor='#FFFFFF',
            font_color='#002F6C'
        )
        st.plotly_chart(fig_hist, use_container_width=True)

        # Mostrar enlaces para escuchar canciones con estilo mejorado
        st.subheader("🎧 Escucha las canciones:")
        for _, row in df_canciones.iterrows():
            st.markdown(
                f"<div style='color: #002F6C; font-size: 16px; margin-bottom: 10px;'>"
                f"▶️ <a href='{row['URL']}' target='_blank' style='text-decoration: none; color: #D4AF37;'>"
                f"{row['Canción']} - {row['Artista']}</a></div>", 
                unsafe_allow_html=True
            )
    else:
        st.error("No se encontraron datos para la configuración seleccionada. Intenta con otra región o cantidad.")
