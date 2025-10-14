import streamlit as st
from utils.supabase_client import init_supabase

st.title("👤 Gestión de Usuarios")

supabase = init_supabase()

usuarios = supabase.table("usuarios").select("*").execute()
st.dataframe(usuarios.data)

