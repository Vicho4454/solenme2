import json
import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
import matplotlib.pyplot as plt
from streamlit_cookies_manager import EncryptedCookieManager

# Configuración de cookies con el password de encriptación desde secrets
passwrd = st.secrets["cookies"]["password"]

# Inicializa el administrador de cookies
cookies = EncryptedCookieManager(prefix="spotify_app", password=passwrd)
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
                st.write("No hay imagen de
