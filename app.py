import streamlit as st

# Set the page configuration
st.set_page_config(page_title="Spotify Statistics", page_icon="🎵", layout="wide")

# Check if the user is logged in
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

# Logic to redirect based on authentication status
if st.session_state['authenticated']:
    from pages.statistics import show_statistics
    show_statistics()
else:
    from pages.login import show_login
    show_login()
