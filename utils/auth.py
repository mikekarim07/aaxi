import streamlit as st

def login_form():
    """Formulario de inicio de sesión simple (solo visual por ahora)."""
    st.sidebar.header("Iniciar sesión")
    email = st.sidebar.text_input("Correo electrónico")
    password = st.sidebar.text_input("Contraseña", type="password")
    if st.sidebar.button("Entrar"):
        st.session_state["logged_in"] = True
        st.session_state["user_email"] = email
        st.sidebar.success("Sesión iniciada")
    return st.session_state.get("logged_in", False)

