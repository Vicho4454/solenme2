import json
import streamlit as st
import spotipy
import pandas as pd
import matplotlib.pyplot as plt
from streamlit_cookies_manager import EncryptedCookieManager

# Configuración de cookies
password = st.secrets["cookies"]["password"]
cookies = EncryptedCookieManager(prefix="spotify_app", password=password)
if not cookies.ready():
    st.stop()

def mostrar_estadisticas():
    if 'token_info' in cookies and cookies['token_info']:
        token_info = json.loads(cookies['token_info'])
        sp = spotipy.Spotify(auth=token_info['access_token'])

        st.title("Estadísticas Personales de Spotify")
        user_profile = sp.me()
        st.header(f"¡Hola, {user_profile.get('display_name', 'Usuario')}!")

        # Mostrar imagen de perfil
        if user_profile.get('images'):
            st.image(user_profile['images'][0]['url'], width=100)
        
        # Obtener y mostrar las canciones más escuchadas
        st.subheader("Tus canciones más escuchadas")
        top_tracks = sp.current_user_top_tracks(limit=10, time_range='medium_term')
        canciones = []
        for track in top_tracks['items']:
            canciones.append({
                'Canción': track['name'],
                'Artista': ', '.join([artist['name'] for artist in track['artists']]),
                'Popularidad': track['popularity'],
                'URL': track['external_urls']['spotify']
            })
        df_canciones = pd.DataFrame(canciones)
        st.dataframe(df_canciones)

        # Graficar las canciones más escuchadas
        st.subheader("Gráfico de Popularidad")
        fig, ax = plt.subplots()
        df_canciones.plot(kind='bar', x='Canción', y='Popularidad', ax=ax, color='green', legend=False)
        ax.set_ylabel("Popularidad")
        ax.set_title("Popularidad de tus canciones más escuchadas")
        plt.xticks(rotation=45, ha='right')
        st.pyplot(fig)

        # Botón para cerrar sesión
        if st.button("Cerrar sesión"):
            del cookies['token_info']  # Eliminar el token
            cookies.save()
            st.session_state['authenticated'] = False
            st.experimental_rerun()  # Recargar para mostrar la página de inicio de sesión
    else:
        st.warning("Por favor, inicia sesión para ver tus estadísticas.")
