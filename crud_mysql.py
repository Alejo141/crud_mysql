import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text

# Configuración de conexión
host = "mysql-db-test-jaag141-cbae.b.aivencloud.com"
port = 20255  # sin comillas
user = "avnadmin"
password = "AVNS_TxkkcYsOoIOiLnb-ZUj"
database = "defaultdb"  # Exactamente igual al nombre de la BD en MySQL

engine = create_engine(
    f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}",
    echo=True,  # Opcional: muestra SQL en consola
    pool_pre_ping=True  # Opcional: evita desconexiones por inactividad
)

# Función para cargar los datos
@st.cache_data(ttl=60)
def get_data():
    try:
        query = "SELECT * FROM usuarios"  # <-- CAMBIADO
        return pd.read_sql(query, engine)
    except Exception as e:
        st.error(f"Ocurrió un error al conectar: {e}")
        return pd.DataFrame()

def add_user(nombre, correo):
    with engine.connect() as conn:
        with conn.begin():
            conn.execute(
                text("INSERT INTO usuarios (nombre, correo) VALUES (:nombre, :correo)"),
                {"nombre": nombre, "correo": correo}
            )

def update_user(user_id, nombre, correo):
    with engine.connect() as conn:
        with conn.begin():
            conn.execute(
                text("UPDATE usuarios SET nombre = :nombre, correo = :correo WHERE id = :id"),
                {"nombre": nombre, "correo": correo, "id": user_id}
            )

def delete_user(user_id):
    with engine.connect() as conn:
        with conn.begin():
            conn.execute(
                text("DELETE FROM usuarios WHERE id = :id"),
                {"id": user_id}
            )

# Interfaz Streamlit
st.title("Gestión de Usuarios - MySQL con Streamlit")

menu = st.sidebar.selectbox("Menú", ["Ver Usuarios", "Agregar Usuario", "Editar Usuario", "Eliminar Usuario"])

if menu == "Ver Usuarios":
    st.subheader("Lista de Usuarios")
    df = get_data()
    st.dataframe(df)

elif menu == "Agregar Usuario":
    st.subheader("Agregar nuevo usuario")
    nombre = st.text_input("Nombre")
    correo = st.text_input("Correo")
    if st.button("Agregar"):
        if nombre and correo:
            add_user(nombre, correo)
            st.success("Usuario agregado correctamente")
            st.cache_data.clear()
        else:
            st.warning("Por favor, completa todos los campos.")

elif menu == "Editar Usuario":
    st.subheader("Editar usuario existente")
    df = get_data()
    if not df.empty:
        user_ids = df['id'].tolist()
        selected_id = st.selectbox("Selecciona ID de usuario", user_ids)
        user = df[df['id'] == selected_id].iloc[0]
        nombre = st.text_input("Nombre", user["nombre"])
        correo = st.text_input("Correo", user["correo"])

        if st.button("Actualizar"):
            update_user(selected_id, nombre, correo)
            st.success("Usuario actualizado")
            st.cache_data.clear()
    else:
        st.info("No hay usuarios para editar.")

elif menu == "Eliminar Usuario":
    st.subheader("Eliminar usuario")
    df = get_data()
    if not df.empty:
        user_ids = df['id'].tolist()
        selected_id = st.selectbox("Selecciona ID de usuario", user_ids)
        if st.button("Eliminar"):
            delete_user(selected_id)
            st.success("Usuario eliminado")
            st.cache_data.clear()
    else:
        st.info("No hay usuarios para eliminar.")
