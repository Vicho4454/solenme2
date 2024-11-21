import json
import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
import matplotlib.pyplot as plt
from streamlit_cookies_manager import EncryptedCookieManager

# Configuración de cookies con el password de encriptación desde secrets
password = st.secrets["cookies"]["password"]

# Inicializa el administrador de cookies
cookies = EncryptedCookieManager(prefix="spotify_app", password=password)
if not cookies.ready():
    st.stop()  # Esperar a que las cookies estén listas

# Configura tus credenciales de Spotify (deberías obtenerlas de Streamlit Secrets)
CLIENT_ID = st.secrets["spotify"]["client_id"]
CLIENT_SECRET = st.secrets["spotify"]["client_secret"]
REDIRECT_URI = 'https://solenme2-test.streamlit.app'  # Asegúrate de que esta sea la URI correcta

# Configuración de autenticación con OAuth
scope = 'user-top-read user-read-recently-played user-read-private'
sp_oauth = SpotifyOAuth(client_id=CLIENT_ID, 
                        client_secret=CLIENT_SECRET, 
                        redirect_uri=REDIRECT_URI, 
                        scope=scope)

# Título de la aplicación
st.title("Estadísticas Personales de Spotify")

# Función para autenticar al usuario
def autenticar_usuario():
    if 'token_info' not in cookies or not cookies['token_info']:
        # Si no hay token, pedir al usuario que inicie sesión
        auth_url = sp_oauth.get_authorize_url()
        st.markdown(f"[Haz clic aquí para iniciar sesión en Spotify]({auth_url})")
    else:
        # Recuperar token_info desde JSON almacenado en cookies
        token_info = json.loads(cookies['token_info'])
        sp = spotipy.Spotify(auth=token_info['access_token'])
        return sp

# Función para cerrar sesión
def cerrar_sesion():
    # Eliminar cualquier dato relacionado con la sesión de usuario
    if 'token_info' in cookies:
        del cookies['token_info']
        cookies.save()  # Guardar cambios en las cookies
    if 'authenticated' in st.session_state:
        del st.session_state['authenticated']
    st.experimental_set_query_params()  # Eliminar parámetros de la URL
    st.experimental_rerun()  # Recargar la página

# Función para cambiar de cuenta
def cambiar_cuenta():
    cerrar_sesion()  # Eliminar el token y resetear la sesión
    st.experimental_rerun()  # Recargar la página

# Verificar si el usuario está autenticado
def mostrar_informacion_usuario():
    if 'token_info' in cookies and cookies['token_info']:
        # Conexión a la API con el token de usuario
        token_info = json.loads(cookies['token_info'])
        sp = spotipy.Spotify(auth=token_info['access_token'])

        try:
            # Mostrar información del usuario
            user_profile = sp.me()
            st.header(f"¡Hola, {user_profile.get('display_name', 'Usuario')}!")
            
            # Mostrar imagen de perfil si está disponible
            if user_profile.get('images') and len(user_profile['images']) > 0:
                st.image(user_profile['images'][0]['url'], width=100)
            else:
                st.write("No hay imagen de perfil disponible.")
            
            # Botón para cambiar de cuenta
            if st.sidebar.button("Cambiar cuenta"):
                cambiar_cuenta()

            # Botón para cerrar sesión
            if st.sidebar.button("Cerrar sesión"):
                cerrar_sesion()

            # Obtener las canciones más escuchadas
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

            # Obtener los artistas más escuchados
            st.subheader("Tus artistas más escuchados")
            top_artists = sp.current_user_top_artists(limit=10, time_range='medium_term')
            artistas = []
            for artist in top_artists['items']:
                artistas.append({
                    'Artista': artist['name'],
                    'Popularidad': artist['popularity'],
                    'Géneros': ', '.join(artist['genres']),
                    'URL': artist['external_urls']['spotify']
                })
            df_artistas = pd.DataFrame(artistas)
            st.dataframe(df_artistas)

            # Graficar los artistas más escuchados
            st.subheader("Gráfico de Popularidad de Artistas")
            fig, ax = plt.subplots()
            df_artistas.plot(kind='bar', x='Artista', y='Popularidad', ax=ax, color='orange', legend=False)
            ax.set_ylabel("Popularidad")
            ax.set_title("Popularidad de tus artistas más escuchados")
            plt.xticks(rotation=45, ha='right')
            st.pyplot(fig)

        except Exception as e:
            st.error(f"Ocurrió un error al obtener la información del usuario: {e}")

    else:
        st.warning("Por favor, inicia sesión para ver tus estadísticas.")

# Función principal
def main():
    # Verificar si hay un código de autorización en la URL
    query_params = st.experimental_get_query_params()  # Obtener parámetros de la URL
    if 'code' in query_params and not st.session_state.get('authenticated', False):
        code = query_params['code'][0]
        try:
            # Obtener el token utilizando el código de autorización
            token_info = sp_oauth.get_access_token(code)
            
            # Guardar el token_info en las cookies como JSON
            cookies['token_info'] = json.dumps(token_info)
            cookies.save()  # Guardar cambios en las cookies
            st.session_state['authenticated'] = True
            st.experimental_rerun()  # Recargar la página para actualizar la sesión
        except Exception as e:
            st.error(f"Error al obtener el token: {e}")

    autenticar_usuario()  # Intentamos autenticar al usuario
    mostrar_informacion_usuario()  # Mostramos la información del usuario si está autenticado

# Ejecutar la aplicación
if __name__ == "__main__":
    main()



