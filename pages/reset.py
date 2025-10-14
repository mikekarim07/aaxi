import streamlit as st
from supabase import create_client, Client

url = st.secrets["url"]
key = st.secrets["key"]
supabase: Client = create_client(url, key)

st.title("🔑 Restablecer contraseña")

# Leer el token que viene en la URL
params = st.query_params
access_token = params.get("access_token", [None])[0]

if access_token:
    new_password = st.text_input("Nueva contraseña", type="password")
    if st.button("Cambiar contraseña"):
        try:
            res = supabase.auth.update_user({"password": new_password}, access_token)
            st.success("Contraseña actualizada correctamente. Ahora puedes iniciar sesión.")
        except Exception as e:
            st.error(f"Error al actualizar la contraseña: {e}")
else:
    st.info("Por favor abre el enlace que recibiste en tu correo para restablecer tu contraseña.")
