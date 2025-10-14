import streamlit as st
from supabase import create_client, Client

# --- Configuración inicial ---
url = st.secrets["url"]
key = st.secrets["key"]
supabase: Client = create_client(url, key)

st.title("🧾 Alta de Cliente - Ajuste Anual por Inflación")

# --- Formulario para crear cliente ---
with st.form("nuevo_cliente"):
    st.subheader("Datos del cliente")
    nombre_cliente = st.text_input("Nombre del grupo empresarial")
    contacto = st.text_input("Nombre del contacto principal")
    email_contacto = st.text_input("Correo del contacto principal")

    st.subheader("Configuración inicial")
    num_entidades = st.number_input("Número de entidades legales", min_value=1, max_value=50, value=3)
    num_usuarios = st.number_input("Número de usuarios (incluyendo al administrador)", min_value=1, max_value=50, value=1)

    st.subheader("Administrador del cliente")
    admin_nombre = st.text_input("Nombre del administrador")
    admin_email = st.text_input("Correo del administrador")
    admin_password = st.text_input("Contraseña temporal", type="password")

    submitted = st.form_submit_button("🚀 Crear Cliente")

# --- Al enviar el formulario ---
if submitted:
    if not (nombre_cliente and email_contacto and admin_email and admin_password):
        st.error("Por favor completa todos los campos obligatorios.")
        st.stop()

    # Paso 1️⃣: Crear cliente
    cliente_data = {
        "nombre": nombre_cliente,
        "contacto": contacto,
        "email_contacto": email_contacto,
        "estatus": True
    }

    cliente_result = supabase.table("clientes").insert(cliente_data).execute()

    if not cliente_result.data:
        st.error("❌ Error al crear el cliente en Supabase.")
        st.stop()

    cliente_id = cliente_result.data[0]["id"]
    st.success(f"✅ Cliente creado correctamente. ID: {cliente_id}")

    # Paso 2️⃣: Crear entidades legales vacías
    entidades = []
    for i in range(int(num_entidades)):
        entidades.append({
            "cliente_id": cliente_id,
            "razon_social": f"Entidad {i+1} - {nombre_cliente}",
            "estatus": True
        })

    entidades_result = supabase.table("entidades_legales").insert(entidades).execute()
    st.info(f"🏢 {len(entidades)} entidades legales creadas.")

    # Paso 3️⃣: Crear usuario administrador (en Supabase Auth)
    try:
        user_auth = supabase.auth.admin.create_user({
            "email": admin_email,
            "password": admin_password,
            "email_confirm": True
        })
        auth_id = user_auth.user.id
    except Exception as e:
        st.error(f"❌ Error al crear el usuario en Supabase Auth: {e}")
        st.stop()

    # Paso 4️⃣: Insertar usuario administrador en tabla 'usuarios'
    usuario_data = {
        "cliente_id": cliente_id,
        "nombre_usuario": admin_nombre,
        "email": admin_email,
        "rol": "admin_cliente",
        "estatus": True,
        "auth_id": auth_id
    }

    usuario_result = supabase.table("usuarios").insert(usuario_data).execute()
    if usuario_result.data:
        st.success(f"👤 Usuario administrador '{admin_nombre}' creado y vinculado correctamente.")
    else:
        st.warning("⚠️ Cliente creado, pero hubo un problema registrando el usuario administrador.")

    # (Opcional) Paso 5️⃣: Crear usuarios adicionales
    if num_usuarios > 1:
        st.info(f"ℹ️ Recuerda crear los {num_usuarios - 1} usuarios restantes desde el módulo de usuarios.")

