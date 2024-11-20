import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
import matplotlib.pyplot as plt

# Configura tus credenciales de Spotify (se obtiene desde Streamlit Secrets)
CLIENT_ID = st.secrets["spotify"]["client_id"]
CLIENT_SECRET = st.secrets["spotify"]["client_secret"]
REDIRECT_URI = 'https://solenme2-test.streamlit.app'
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
    if 'token_info' not in st.session_state:
        # Si no hay token, pedir al usuario que inicie sesión
        auth_url = sp_oauth.get_authorize_url()
        st.markdown(f"[Haz clic aquí para iniciar sesión en Spotify]({auth_url})")
    else:
        token_info = st.session_state['token_info']
        sp = spotipy.Spotify(auth=token_info['access_token'])
        return sp

# Función para cerrar sesión
def cerrar_sesion():
    if 'token_info' in st.session_state:
        del st.session_state['token_info']  # Eliminar token de la sesión
    st.session_state['logout'] = True  # Marcar el estado de cierre de sesión
    st.rerun()  # Recarga la página

# Función para cambiar de cuenta
def cambiar_cuenta():
    cerrar_sesion()  # Eliminar el token y resetear la sesión
    st.session_state['change_account'] = True  # Marcar que el usuario quiere cambiar de cuenta
    st.rerun()  # Recargar la página

# Verificar si el usuario está autenticado
def mostrar_informacion_usuario():
    if 'token_info' in st.session_state:
        # Conexión a la API con el token de usuario
        token_info = st.session_state['token_info']
        sp = spotipy.Spotify(auth=token_info['access_token'])

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

    else:
        st.warning("Por favor, inicia sesión para ver tus estadísticas.")
# Función principal
def main():
    # Verificar si hay un código de autorización en la URL
    query_params = st.query_params  # Usamos st.query_params en lugar de experimental_get_query_params
    if 'code' in query_params:
        code = query_params['code']
        try:
            token_info = sp_oauth.get_access_token(code)
            st.session_state['token_info'] = token_info
            st.rerun()  # Recargar la página para actualizar la sesión
        except Exception as e:
            st.error(f"Error al obtener el token: {e}")
    
    autenticar_usuario()  # Intentamos autenticar al usuario
    mostrar_informacion_usuario()  # Mostramos la información del usuario si está autenticado

# Ejecutar la aplicación
if __name__ == "__main__":
    main()
