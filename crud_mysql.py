import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text

# Configuración de conexión
host = "mysql-db-test-jaag141-cbae.b.aivencloud.com:20259"
port = 20259
user = "avnadmin"
password = "AVNS_TxkkcYsOoIOiLnb-ZUj"  # Deja vacío si no tiene contraseña
database = "defaultdb"

# Crear el motor de conexión
secrets = st.secrets["mysql"]
engine = create_engine(
    f"mysql+mysqlconnector://{secrets.user}:{secrets.password}@{secrets.host}:{secrets.port}/{secrets.database}"
)

# Función para cargar los datos
@st.cache_data(ttl=60)
def get_data():
    query = "SELECT * FROM usuarios"
    return pd.read_sql(query, engine)

def add_user(nombre, correo):
    with engine.connect() as conn:
        conn.execute(text("INSERT INTO usuarios (nombre, correo) VALUES (:nombre, :correo)"), {"nombre": nombre, "correo": correo})
        conn.commit()

def update_user(user_id, nombre, correo):
    with engine.connect() as conn:
        conn.execute(text("UPDATE usuarios SET nombre = :nombre, correo = :correo WHERE id = :id"),
                     {"nombre": nombre, "correo": correo, "id": user_id})
        conn.commit()

def delete_user(user_id):
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM usuarios WHERE id = :id"), {"id": user_id})
        conn.commit()

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
            st.cache_data.clear()  # Limpia caché para ver cambios
        else:
            st.warning("Por favor, completa todos los campos.")

elif menu == "Editar Usuario":
    st.subheader("Editar usuario existente")
    df = get_data()
    user_ids = df['id'].tolist()
    selected_id = st.selectbox("Selecciona ID de usuario", user_ids)
    user = df[df['id'] == selected_id].iloc[0]
    nombre = st.text_input("Nombre", user["nombre"])
    correo = st.text_input("Correo", user["correo"])

    if st.button("Actualizar"):
        update_user(selected_id, nombre, correo)
        st.success("Usuario actualizado")
        st.cache_data.clear()

elif menu == "Eliminar Usuario":
    st.subheader("Eliminar usuario")
    df = get_data()
    user_ids = df['id'].tolist()
    selected_id = st.selectbox("Selecciona ID de usuario", user_ids)
    if st.button("Eliminar"):
        delete_user(selected_id)
        st.success("Usuario eliminado")
        st.cache_data.clear()
