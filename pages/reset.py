import streamlit as st
from supabase import create_client, Client

# --- CONFIGURACIÓN DE SUPABASE ---
url = st.secrets["url"]
key = st.secrets["key"]
supabase: Client = create_client(url, key)

# --- INTERFAZ PRINCIPAL ---
st.set_page_config(page_title="Restablecer contraseña", page_icon="🔑")

# Detectar si estamos en la ruta /reset (cuando el usuario da clic desde el correo)
params = st.query_params
access_token = params.get("access_token") or params.get("token_hash")
if isinstance(access_token, list):
    access_token = access_token[0]

# Si no hay token, mostrar formulario para solicitar correo
if not access_token:
    st.title("🔒 Recuperar acceso")
    st.write("Ingresa tu correo electrónico para recibir un enlace de restablecimiento de contraseña.")

    email = st.text_input("Correo electrónico")
    if st.button("Enviar enlace de recuperación"):
        try:
            supabase.auth.reset_password_for_email(
                email,
                options={"redirect_to": "https://tu-app.streamlit.app/reset"}  # 👈 Ajusta con tu URL real
            )
            st.success("✅ Se ha enviado un correo con el enlace para restablecer tu contraseña.")
        except Exception as e:
            st.error(f"❌ Ocurrió un error: {e}")

# Si hay token, mostrar formulario para establecer nueva contraseña
else:
    st.title("🔑 Restablecer contraseña")
    st.write("Por favor, escribe tu nueva contraseña a continuación:")

    new_password = st.text_input("Nueva contraseña", type="password")
    confirm_password = st.text_input("Confirmar contraseña", type="password")

    if st.button("Actualizar contraseña"):
        if new_password != confirm_password:
            st.warning("⚠️ Las contraseñas no coinciden.")
        elif len(new_password) < 6:
            st.warning("⚠️ La contraseña debe tener al menos 6 caracteres.")
        else:
            try:
                # Llamar a Supabase para actualizar la contraseña
                res = supabase.auth.update_user({"password": new_password}, access_token)
                st.success("✅ Contraseña actualizada correctamente. Ahora puedes iniciar sesión.")
            except Exception as e:
                st.error(f"❌ Error al actualizar la contraseña: {e}")
