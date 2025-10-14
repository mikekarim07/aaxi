import streamlit as st
from utils.supabase_client import init_supabase

# Configuración general
st.set_page_config(page_title="AAxI Superadmin", layout="wide")

st.title("📊 Panel del Superadministrador - AAxI")

# Conexión a Supabase
supabase = init_supabase()

st.info("Conexión exitosa con Supabase ✅")

# Prueba de lectura de tabla
try:
    data = supabase.table("clientes").select("*").execute()
    st.write("Clientes registrados:")
    st.dataframe(data.data)
except Exception as e:
    st.error(f"No se pudo obtener datos: {e}")

