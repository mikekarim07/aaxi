import streamlit as st
from utils.supabase_client import init_supabase

st.title("📈 Dashboard General")

supabase = init_supabase()

clientes = supabase.table("clientes").select("*").execute()
entidades = supabase.table("entidades_legales").select("*").execute()
usuarios = supabase.table("usuarios").select("*").execute()

st.metric("Clientes activos", len(clientes.data))
st.metric("Entidades legales", len(entidades.data))
st.metric("Usuarios registrados", len(usuarios.data))

