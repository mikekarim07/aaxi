import streamlit as st
from utils.supabase_client import init_supabase
from postgrest.exceptions import APIError

st.title("👤 Gestión de Usuarios")

supabase = init_supabase()

# Paso 1. Obtener lista de clientes
clientes = supabase.table("clientes").select("id, nombre").execute()
clientes_data = clientes.data or []

# Dropdown con placeholder
cliente_nombres = ["Seleccionar Cliente"] + [c["nombre"] for c in clientes_data]
cliente_seleccionado = st.selectbox("Selecciona un cliente", cliente_nombres)

# Obtener el cliente_id
cliente_id = None
if cliente_seleccionado != "Seleccionar Cliente":
    cliente = next((c for c in clientes_data if c["nombre"] == cliente_seleccionado), None)
    if cliente:
        cliente_id = cliente["id"]

st.divider()

# Paso 2. Mostrar formulario SOLO si hay cliente seleccionado
if cliente_id:
    st.subheader(f"Creación de usuario para el cliente: {cliente_seleccionado}")

    with st.form("crear_usuario_form"):
        email = st.text_input("Correo electrónico")
        nombre_usuario = st.text_input("Nombre del usuario")
        rol = st.selectbox("Rol", ["Administrador", "Gerente", "Usuario"])
        estatus = st.checkbox("Activo", value=True)
        submit = st.form_submit_button("Crear usuario")

    if submit:
        if not email or not nombre_usuario:
            st.error("El nombre y el correo son obligatorios.")
        else:
            try:
                # Validación 1: Verificar si el correo ya existe en la tabla usuarios
                existing_user = supabase.table("usuarios").select("*").eq("email", email).execute()
                if existing_user.data:
                    st.error("❌ Ya existe un usuario con este correo en la tabla interna.")
                else:
                    # Validación 2: Verificar si el correo ya existe en Auth
                    auth_users = supabase.auth.admin.list_users()
                    if any(u.email == email for u in auth_users.data):
                        st.error("❌ Ya existe un usuario con este correo en Supabase Auth.")
                    else:
                        # Crear usuario en Auth
                        auth_response = supabase.auth.admin.create_user(
                            {
                                "email": email,
                                "email_confirm": True,
                                "user_metadata": {
                                    "nombre_usuario": nombre_usuario,
                                    "rol": rol,
                                    "cliente_id": cliente_id,
                                },
                            }
                        )
                        auth_user = auth_response.user

                        if auth_user:
                            # Insertar en tabla usuarios
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

else:
    st.info("Selecciona un cliente para habilitar el formulario de creación de usuario.")

st.divider()

# Mostrar todos los usuarios registrados
st.subheader("Usuarios registrados")
usuarios = supabase.table("usuarios").select("*").execute()
st.dataframe(usuarios.data)
