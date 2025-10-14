import streamlit as st
from utils.supabase_client import init_supabase
from postgrest.exceptions import APIError

st.title("👤 Gestión de Usuarios")

supabase = init_supabase()

# -----------------------------
# Paso 1: Selección de cliente
# -----------------------------
clientes = supabase.table("clientes").select("id, nombre").execute()
clientes_data = clientes.data or []

cliente_nombres = ["Seleccionar Cliente"] + [c["nombre"] for c in clientes_data]
cliente_seleccionado = st.selectbox("Selecciona un cliente", cliente_nombres)

cliente_id = None
if cliente_seleccionado != "Seleccionar Cliente":
    cliente = next((c for c in clientes_data if c["nombre"] == cliente_seleccionado), None)
    if cliente:
        cliente_id = cliente["id"]

# -----------------------------
# Paso 2: Mostrar usuarios existentes en expander
# -----------------------------
if cliente_id:
    with st.expander(f"Usuarios del cliente: {cliente_seleccionado}", expanded=True):
        usuarios_cliente = supabase.table("usuarios").select("*").eq("cliente_id", cliente_id).execute()
        usuarios_data = usuarios_cliente.data or []

        if usuarios_data:
            st.dataframe(usuarios_data)
        else:
            st.info("No hay usuarios registrados para este cliente.")

    st.divider()

    # -----------------------------
    # Paso 3: Botón para agregar usuario
    # -----------------------------
    if "agregar_usuario" not in st.session_state:
        st.session_state["agregar_usuario"] = False

    if st.button("Agregar usuario"):
        st.session_state["agregar_usuario"] = True

    # -----------------------------
    # Paso 4: Formulario de alta en expander (solo si se presionó el botón)
    # -----------------------------
    if st.session_state["agregar_usuario"]:
        with st.expander("Formulario de creación de usuario", expanded=True):
            # Mapping de roles para cumplir el CHECK constraint
            rol_opciones_ui = {
                "Superadmin": "superadmin",
                "Administrador Cliente": "admin_cliente",
                "Analista": "analista",
                "Visor": "visor"
            }

            with st.form("crear_usuario_form"):
                email = st.text_input("Correo electrónico")
                nombre_usuario = st.text_input("Nombre del usuario")
                rol_seleccionado = st.selectbox("Rol", list(rol_opciones_ui.keys()))
                rol = rol_opciones_ui[rol_seleccionado]  # valor exacto que se guardará en la tabla
                estatus = st.checkbox("Activo", value=True)
                submit = st.form_submit_button("Crear usuario")

            if submit:
                if not email or not nombre_usuario:
                    st.error("El nombre y el correo son obligatorios.")
                else:
                    try:
                        # -----------------------------
                        # Crear usuario en Auth
                        # -----------------------------
                        auth_response = supabase.auth.admin.create_user(
                            {
                                "email": email,
                                "password": "temporal123!",  # password temporal
                                "email_confirm": True,
                                "user_metadata": {
                                    "nombre_usuario": nombre_usuario,
                                    "rol": rol,
                                    "cliente_id": cliente_id,
                                }
                            }
                        )
                        auth_user = auth_response.user

                        if auth_user:
                            # -----------------------------
                            # Insertar usuario en tabla interna
                            # -----------------------------
                            usuario_data = {
                                "email": email,
                                "nombre_usuario": nombre_usuario,
                                "rol": rol,
                                "estatus": estatus,
                                "cliente_id": cliente_id,
                                "auth_id": auth_user.id,
                            }
                            supabase.table("usuarios").insert(usuario_data).execute()
                            st.success(f"✅ Usuario '{nombre_usuario}' creado correctamente en Auth y tabla interna.")
                            st.session_state["agregar_usuario"] = False  # Ocultar formulario

                            # Refrescar la lista de usuarios
                            usuarios_cliente = supabase.table("usuarios").select("*").eq("cliente_id", cliente_id).execute()
                            with st.expander(f"Usuarios del cliente: {cliente_seleccionado}", expanded=True):
                                st.dataframe(usuarios_cliente.data)

                        else:
                            st.error("❌ No se pudo crear el usuario en Supabase Auth.")

                    except APIError as e:
                        st.error(f"Error en la base de datos: {e}")
                    except Exception as e:
                        st.error(f"Ocurrió un error: {e}")

else:
    st.info("Selecciona un cliente para ver sus usuarios.")
