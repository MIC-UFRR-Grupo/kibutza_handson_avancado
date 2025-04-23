import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from streamlit_folium import st_folium

# Configurar tema escuro
st.set_page_config(page_title="Monitoramento de Cadeia de Frio", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
    <style>
    .main {
        background-color: #1e1e1e;
        color: #ffffff;
    }
    .stSelectbox label, .stTextInput label {
        color: #ffffff;
    }
    .stDataFrame {
        background-color: #2e2e2e;
    }
    .sidebar .sidebar-content {
        background-color: #2e2e2e;
    }
    </style>
""", unsafe_allow_html=True)

# Aplicar tema Seaborn
sns.set_theme(style="darkgrid")

# Inicializar o Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase-key.json")
    firebase_admin.initialize_app(cred, {
        "databaseURL": "https://simcaf-9ae4d-default-rtdb.firebaseio.com/"
    })

# Função para carregar dados
@st.cache_data
def load_data(environment):
    ref = db.reference(f"/environments/{environment}")
    data = ref.get()
    if not data:
        return pd.DataFrame()
    rows = []
    for timestamp, values in data.items():
        values["timestamp"] = timestamp
        rows.append(values)
    return pd.DataFrame(rows)

# Função para verificar login
def check_login(username, password):
    ref = db.reference(f"/users/{username}")
    user_data = ref.get()
    if user_data and user_data.get("password") == password:
        return user_data
    return None

# Estado da sessão
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_data = None

# Inicializar environment
environment = None

# Sidebar para login e seleção de ambiente
with st.sidebar:
    st.header("Controle de Acesso")
    if not st.session_state.logged_in:
        username = st.text_input("Usuário")
        password = st.text_input("Senha", type="password")
        if st.button("Login"):
            user_data = check_login(username, password)
            if user_data:
                st.session_state.logged_in = True
                st.session_state.user_data = user_data
                st.success("Login bem-sucedido!")
            else:
                st.error("Usuário ou senha inválidos.")
    else:
        st.write(f"Bem-vindo, {st.session_state.user_data['role']}!")
        allowed_environments = st.session_state.user_data["allowed_environments"]
        environment = st.selectbox("Ambiente", allowed_environments, help="Selecione o ambiente a monitorar")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.user_data = None
            st.rerun()

# Dashboard principal
if st.session_state.logged_in and environment:
    st.title("Sistema de Monitoramento de Cadeia de Frio")
    st.header(f"Monitoramento: {environment}", divider="blue")

    # Carregar dados
    df = load_data(environment)

    if not df.empty:
        # Layout principal
        col_map, col_charts = st.columns([1, 2])

        # Mapa (para carro)
        with col_map:
            st.subheader("Localização", divider="gray")
            if environment == "carro_001" and "latitude" in df.columns and "longitude" in df.columns:
                latest_data = df.iloc[-1]
                m = folium.Map(location=[latest_data["latitude"], latest_data["longitude"]], zoom_start=10)
                folium.Marker(
                    [latest_data["latitude"], latest_data["longitude"]],
                    popup=f"Carro em Trânsito\nTemp: {latest_data['temperature']}°C",
                    icon=folium.Icon(color="blue", icon="truck")
                ).add_to(m)
                st_folium(m, width=300, height=300)
            else:
                st.info("Mapa disponível apenas para Carro em Trânsito.")

        # Gráficos
        with col_charts:
            col1, col2, col3 = st.columns(3)
            # Temperatura
            with col1:
                st.subheader("Temperatura (°C)")
                fig, ax = plt.subplots(figsize=(4, 3))
                sns.lineplot(x="timestamp", y="temperature", data=df, marker="o", color="#1f77b4", linewidth=2, ax=ax)
                ax.set_xlabel("Timestamp", fontsize=8, color="white")
                ax.set_ylabel("Temperatura (°C)", fontsize=8, color="white")
                ax.set_title("Temperatura", fontsize=10, color="white")
                ax.tick_params(axis="x", rotation=45, labelsize=6, colors="white")
                ax.tick_params(axis="y", labelsize=6, colors="white")
                fig.patch.set_facecolor("#2e2e2e")
                ax.set_facecolor("#2e2e2e")
                st.pyplot(fig)

            # Umidade
            with col2:
                st.subheader("Umidade (%)")
                fig, ax = plt.subplots(figsize=(4, 3))
                sns.lineplot(x="timestamp", y="humidity", data=df, marker="o", color="#2ca02c", linewidth=2, ax=ax)
                ax.set_xlabel("Timestamp", fontsize=8, color="white")
                ax.set_ylabel("Umidade (%)", fontsize=8, color="white")
                ax.set_title("Umidade", fontsize=10, color="white")
                ax.tick_params(axis="x", rotation=45, labelsize=6, colors="white")
                ax.tick_params(axis="y", labelsize=6, colors="white")
                fig.patch.set_facecolor("#2e2e2e")
                ax.set_facecolor("#2e2e2e")
                st.pyplot(fig)

            # UV
            with col3:
                st.subheader("UV (mW/cm²)")
                fig, ax = plt.subplots(figsize=(4, 3))
                sns.lineplot(x="timestamp", y="uv", data=df, marker="o", color="#9467bd", linewidth=2, ax=ax)
                ax.set_xlabel("Timestamp", fontsize=8, color="white")
                ax.set_ylabel("UV (mW/cm²)", fontsize=8, color="white")
                ax.set_title("UV", fontsize=10, color="white")
                ax.tick_params(axis="x", rotation=45, labelsize=6, colors="white")
                ax.tick_params(axis="y", labelsize=6, colors="white")
                fig.patch.set_facecolor("#2e2e2e")
                ax.set_facecolor("#2e2e2e")
                st.pyplot(fig)

        # Tabela de alertas
        st.subheader("Alertas Recentes", divider="red")
        ref_alerts = db.reference(f"/alerts/{environment}")
        alerts = ref_alerts.get()
        if alerts and isinstance(alerts, dict):
            alert_rows = [
                {"timestamp": ts, **values} for ts, values in alerts.items()
            ]
            df_alerts = pd.DataFrame(alert_rows)[["timestamp", "sensor_id", "reason", "temperature"]]
            def highlight_alerts(row):
                return ['background-color: #4b0000' if row["reason"] else '' for _ in row]
            styled_df = df_alerts.style.apply(highlight_alerts, axis=1).format({"temperature": "{:.1f}"})
            st.dataframe(styled_df, use_container_width=True)
        else:
            st.warning("Nenhum alerta disponível.", icon="⚠️")
    else:
        st.warning(f"Nenhum dado disponível para {environment}. Execute insert_data.py.", icon="⚠️")
else:
    st.info("Por favor, faça login para acessar o dashboard.")