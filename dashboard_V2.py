import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Configurar tema escuro do Streamlit
st.set_page_config(page_title="Monitoramento de Cadeia de Frio", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""
    <style>
    .main {
        background-color: #1e1e1e;
        color: #ffffff;
    }
    .stSelectbox label {
        color: #ffffff;
    }
    .stDataFrame {
        background-color: #2e2e2e;
    }
    </style>
""", unsafe_allow_html=True)

# Aplicar tema Seaborn
sns.set_theme(style="darkgrid")

# Inicializar o Firebase (apenas se não inicializado)
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase-key.json")
    firebase_admin.initialize_app(cred, {
        "databaseURL": "https://simcaf-9ae4d-default-rtdb.firebaseio.com/"
    })

# Função para carregar dados
@st.cache_data
def load_data():
    ref = db.reference("/alertas/dados/DHT11_01")
    data = ref.get()
    if not data:
        return pd.DataFrame()
    rows = []
    for timestamp, values in data.items():
        values["timestamp"] = timestamp
        rows.append(values)
    return pd.DataFrame(rows)

# Configurar Streamlit
st.title("Sistema de Monitoramento de Cadeia de Frio")
st.header("Dashboard de Sensores", divider="blue")

# Carregar dados
df = load_data()

if not df.empty:
    # Filtrar por localização
    locations = df["location"].unique()
    selected_location = st.selectbox("Selecione a Localização", locations, help="Escolha a farmácia para visualizar os dados")

    # Dados filtrados
    df_filtered = df[df["location"] == selected_location]

    # Criar colunas para gráficos
    col1, col2, col3 = st.columns(3)

    # Gráfico de temperatura
    with col1:
        st.subheader("Temperatura (°C)")
        fig, ax = plt.subplots(figsize=(5, 3))
        sns.lineplot(x="timestamp", y="temperature", data=df_filtered, marker="o", color="#1f77b4", linewidth=2, ax=ax)
        ax.set_xlabel("Timestamp", fontsize=10, color="white")
        ax.set_ylabel("Temperatura (°C)", fontsize=10, color="white")
        ax.set_title("Temperatura ao Longo do Tempo", fontsize=12, color="white")
        ax.tick_params(axis="x", rotation=45, labelsize=8, colors="white")
        ax.tick_params(axis="y", labelsize=8, colors="white")
        fig.patch.set_facecolor("#2e2e2e")
        ax.set_facecolor("#2e2e2e")
        st.pyplot(fig)

    # Gráfico de umidade
    with col2:
        st.subheader("Umidade (%)")
        fig, ax = plt.subplots(figsize=(5, 3))
        sns.lineplot(x="timestamp", y="humidity", data=df_filtered, marker="o", color="#2ca02c", linewidth=2, ax=ax)
        ax.set_xlabel("Timestamp", fontsize=10, color="white")
        ax.set_ylabel("Umidade (%)", fontsize=10, color="white")
        ax.set_title("Umidade ao Longo do Tempo", fontsize=12, color="white")
        ax.tick_params(axis="x", rotation=45, labelsize=8, colors="white")
        ax.tick_params(axis="y", labelsize=8, colors="white")
        fig.patch.set_facecolor("#2e2e2e")
        ax.set_facecolor("#2e2e2e")
        st.pyplot(fig)

    # Gráfico de UV
    with col3:
        st.subheader("UV (mW/cm²)")
        fig, ax = plt.subplots(figsize=(5, 3))
        sns.lineplot(x="timestamp", y="uv", data=df_filtered, marker="o", color="#9467bd", linewidth=2, ax=ax)
        ax.set_xlabel("Timestamp", fontsize=10, color="white")
        ax.set_ylabel("UV (mW/cm²)", fontsize=10, color="white")
        ax.set_title("UV ao Longo do Tempo", fontsize=12, color="white")
        ax.tick_params(axis="x", rotation=45, labelsize=8, colors="white")
        ax.tick_params(axis="y", labelsize=8, colors="white")
        fig.patch.set_facecolor("#2e2e2e")
        ax.set_facecolor("#2e2e2e")
        st.pyplot(fig)

    # Tabela de alertas
    st.subheader("Alertas Recentes", divider="red")
    ref_alerts = db.reference("/alertas")
    alerts = ref_alerts.get()
    if alerts and isinstance(alerts, dict):
        alert_rows = [
            {"timestamp": ts, **values} for ts, values in alerts.items() if ts != "dados"
        ]
        df_alerts = pd.DataFrame(alert_rows)[["timestamp", "sensor_id", "reason", "temperature", "uv"]]
        # Estilizar tabela com fundo vermelho para alertas
        def highlight_alerts(row):
            return ['background-color: #4b0000' if row["reason"] else '' for _ in row]
        styled_df = df_alerts.style.apply(highlight_alerts, axis=1).format({"temperature": "{:.1f}", "uv": "{:.5f}"})
        st.dataframe(styled_df, use_container_width=True)
    else:
        st.warning("Nenhum alerta disponível.", icon="⚠️")
else:
    st.warning("Nenhum dado disponível. Execute insert_data.py primeiro.", icon="⚠️")