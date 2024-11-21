import streamlit as st

# Configuración de la aplicación
st.set_page_config(page_title="Estadísticas de Spotify", page_icon="🎵", layout="wide")

# Verificar el estado de autenticación
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

# Lógica para redirigir según el estado de autenticación
if st.session_state['authenticated']:
    from pages.statistics import mostrar_estadisticas
    mostrar_estadisticas()
else:
    from pages.login import mostrar_login
    mostrar_login()
