import streamlit as st
from utils.supabase_client import init_supabase
from postgrest.exceptions import APIError

st.title("👤 Gestión de Usuarios")

supabase = init_supabase()

# Paso 1. Seleccionar cliente
clientes = supabase.table("clientes").select("id, nombre_cliente").execute()
clientes_data = clientes.data or []

cliente_options = {c["nombre_cliente"]: c["id"] for c in clientes_data}
cliente_nombre = st.selectbox("Selecciona el cliente", list(cliente_options.keys())) if cliente_options else None
cliente_id = cliente_options[cliente_nombre] if cliente_nombre else None

st.divider()

# Paso 2. Capturar datos del nuevo usuario
with st.form("crear_usuario_form"):
    email = st.text_input("Correo electrónico")
    nombre_usuario = st.text_input("Nombre del usuario")
    rol = st.selectbox("Rol", ["Administrador", "Gerente", "Usuario"])
    estatus = st.checkbox("Activo", value=True)
    submit = st.form_submit_button("Crear usuario")

if submit:
    if not cliente_id:
        st.error("Debes seleccionar un cliente antes de crear un usuario.")
    elif not email or not nombre_usuario:
        st.error("El nombre y el correo son obligatorios.")
    else:
        try:
            # Paso 3. Crear usuario en Auth
            auth_response = supabase.auth.admin.create_user(
                {
                    "email": email,
                    "email_confirm": True,  # Marca el email como confirmado
                    "user_metadata": {"nombre_usuario": nombre_usuario, "rol": rol},
                }
            )
            auth_user = auth_response.user

            if auth_user:
                # Paso 4. Crear registro en la tabla usuarios
                usuario_data = {
                    "email": email,
                    "nombre_usuario": nombre_usuario,
                    "rol": rol,
                    "estatus": estatus,
                    "cliente_id": cliente_id,
                    "auth_id": auth_user.id,
                }

                supabase.table("usuarios").insert(usuario_data).execute()

                st.success(f"✅ Usuario '{nombre_usuario}' creado exitosamente.")
            else:
                st.error("❌ No se pudo crear el usuario en Supabase Auth.")

        except APIError as e:
            st.error(f"Error en la base de datos: {e}")
        except Exception as e:
            st.error(f"Ocurrió un error: {e}")

st.divider()

# Paso 5. Mostrar lista de usuarios existentes
usuarios = supabase.table("usuarios").select("*").execute()
st.dataframe(usuarios.data)
