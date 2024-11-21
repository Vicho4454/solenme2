import json
import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from streamlit_cookies_manager import EncryptedCookieManager

# Configuración de cookies
password = st.secrets["cookies"]["password"]
cookies = EncryptedCookieManager(prefix="spotify_app", password=password)
if not cookies.ready():
    st.stop()

# Configura tus credenciales de Spotify
CLIENT_ID = st.secrets["spotify"]["client_id"]
CLIENT_SECRET = st.secrets["spotify"]["client_secret"]
REDIRECT_URI = 'https://solenme2-test.streamlit.app'
scope = 'user-top-read user-read-recently-played user-read-private'
sp_oauth = SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI, scope=scope)

def mostrar_login():
    st.title("Inicio de Sesión en Spotify")
    
    if 'token_info' not in cookies or not cookies['token_info']:
        auth_url = sp_oauth.get_authorize_url()
        st.markdown(f"[Haz clic aquí para iniciar sesión en Spotify]({auth_url})")
    else:
        # Si ya hay un token, redirigir a estadísticas
        token_info = json.loads(cookies['token_info'])
        st.session_state['authenticated'] = True
        st.experimental_rerun()  # Recargar la aplicación para mostrar estadísticas

    # Manejo del código de autorización
    query_params = st.experimental_get_query_params()
    if 'code' in query_params:
        code = query_params['code'][0]
        try:
            # Obtener el token utilizando el código de autorización
            token_info = sp_oauth.get_access_token(code)
            cookies['token_info'] = json.dumps(token_info)
            cookies.save()
            st.session_state['authenticated'] = True
            st.experimental_rerun()  # Recargar para mostrar estadísticas
        except Exception as e:
            st.error(f"Error al obtener el token: {e}")
