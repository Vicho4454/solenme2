import streamlit as st
import json
from streamlit_cookies_manager import EncryptedCookieManager

# Initialize cookie manager
password = st.secrets["cookies"]["password"]
cookies = EncryptedCookieManager(prefix="spotify_app", password=password)
if not cookies.ready():
    st.stop()

def show_login():
    st.title("Login to Spotify")

    if 'token_info' not in cookies or not cookies['token_info']:
        # Display login form
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            # Here you would normally authenticate with Spotify
            # For demonstration, we will just simulate a successful login
            if email == "user@example.com" and password == "password123":
                # Simulate storing token info in cookies
                token_info = {"access_token": "dummy_token"}
                cookies['token_info'] = json.dumps(token_info)
                cookies.save()
                st.session_state['authenticated'] = True
                st.experimental_rerun()  # Reload the app to show statistics
            else:
                st.error("Invalid credentials. Please try again.")
    else:
        st.success("You are already logged in. Redirecting to statistics...")
        st.session_state['authenticated'] = True
        st.experimental_rerun()  # Reload the app to show statistics
