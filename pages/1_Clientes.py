import streamlit as st
from utils.supabase_client import init_supabase

st.title("👥 Gestión de Clientes")

supabase = init_supabase()

# Listar clientes
clientes = supabase.table("clientes").select("*").execute()
st.dataframe(clientes.data)

# Botón para agregar nuevo cliente
st.subheader("Alta de nuevo cliente")
nombre = st.text_input("Nombre del cliente / grupo empresarial")
rfc = st.text_input("RFC del cliente")

if st.button("Guardar cliente"):
    data = {"nombre": nombre, "rfc": rfc}
    supabase.table("clientes").insert(data).execute()
    st.success(f"Cliente '{nombre}' guardado exitosamente ✅")

