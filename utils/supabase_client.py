from supabase import create_client
import streamlit as st

@st.cache_resource
def init_supabase():
    """Inicializa la conexión con Supabase."""
    url = st.secrets["url"]
    key = st.secrets["key"]
    return create_client(url, key)

