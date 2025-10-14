import streamlit as st
from utils.supabase_client import init_supabase
from utils.excel_loader import load_excel

st.title("🏢 Entidades Legales")

supabase = init_supabase()

# Mostrar entidades existentes
entidades = supabase.table("entidades_legales").select("*").execute()
st.dataframe(entidades.data)

# Carga masiva desde Excel
st.subheader("Carga masiva de entidades")
uploaded_file = st.file_uploader("Selecciona archivo Excel", type=["xlsx"])

if uploaded_file:
    df = load_excel(uploaded_file)
    if df is not None:
        st.dataframe(df.head())
        if st.button("Cargar a base de datos"):
            records = df.to_dict(orient="records")
            supabase.table("entidades_legales").insert(records).execute()
            st.success("Entidades cargadas correctamente ✅")

