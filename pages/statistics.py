import streamlit as st
import json
from streamlit_cookies_manager import EncryptedCookieManager

# Initialize cookie manager
password = st.secrets["cookies"]["password"]
cookies = EncryptedCookieManager(prefix="spotify_app", password=password)
if not cookies.ready():
    st.stop()

def show_statistics():
    if 'token_info' in cookies and cookies['token_info']:
        token_info = json.loads(cookies['token_info'])
        st.title("Your Spotify Statistics")

        # Here you would fetch and display user statistics
        user_stats = {
            "songs_listened": 150,
            "favorite_artist": "Artist Name",
            "playlists": ["Playlist 1", "Playlist 2"]
        }

        st.write(f"Songs Listened: {user_stats['songs_listened']}")
        st.write(f"Favorite Artist: {user_stats['favorite_artist']}")
        st.write("Playlists:")
        for playlist in user_stats['playlists']:
            st.write(f"- {playlist}")

        if st.button("Logout"):
            # Clear the token and redirect to login
            del cookies['token_info']
            cookies.save()
            st.session_state['authenticated'] = False
            st.experimental_rerun()  # Reload the app to show login
    else:
        st.warning("Please log in to see your statistics.")
