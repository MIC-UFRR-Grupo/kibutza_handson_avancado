import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Inicializar o Firebase (apenas se não inicializado)
if not firebase_admin._apps:
    cred = credentials.Certificate("AIzaSyDkOIfjWdKtXWBM6YDudsVF2u9GSmbU")
    firebase_admin.initialize_app(cred, {
        "databaseURL": "https://simcaf-9ae4d-default-rtdb.firebaseio.com"
    })

# Função para carregar dados
@st.cache_data
def load_data():classcls
    ref = db.reference("/sensor_data")
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
st.header("Dashboard de Sensores")

# Carregar dados
df = load_data()

if not df.empty:
    # Filtrar por localização
    locations = df["location"].unique()
    selected_location = st.selectbox("Selecione a Localização", locations)

    # Dados filtrados
    df_filtered = df[df["location"] == selected_location]

    # Gráfico de temperatura
    st.subheader("Temperatura (°C)")
    fig, ax = plt.subplots()
    ax.plot(df_filtered["timestamp"], df_filtered["temperature_raw"], marker="o", linestyle="-", color="b")
    ax.set_xlabel("Timestamp")
    ax.set_ylabel("Temperatura (°C)")
    ax.set_title("Temperatura ao Longo do Tempo")
    ax.grid(True)
    plt.xticks(rotation=45)
    st.pyplot(fig)

    # Gráfico de umidade
    st.subheader("Umidade (%)")
    fig, ax = plt.subplots()
    ax.plot(df_filtered["timestamp"], df_filtered["humidity_raw"], marker="o", linestyle="-", color="g")
    ax.set_xlabel("Timestamp")
    ax.set_ylabel("Umidade (%)")
    ax.set_title("Umidade ao Longo do Tempo")
    ax.grid(True)
    plt.xticks(rotation=45)
    st.pyplot(fig)

    # Tabela de alertas
    st.subheader("Alertas Recentes")
    ref_alerts = db.reference("/alerts")
    alerts = ref_alerts.get()
    if alerts:
        alert_rows = [
            {"timestamp": ts, **values} for ts, values in alerts.items()
        ]
        st.dataframe(pd.DataFrame(alert_rows)[["timestamp", "sensor_id", "alert_type", "alert_message"]])
    else:
        st.warning("Nenhum alerta disponível.")
else:
    st.warning("Nenhum dado disponível. Execute insert_data.py primeiro.")
