import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_extras.grid import grid
from datetime import datetime, timedelta

# Configurar tema escuro e layout wide
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

# Inicializar o Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase-key.json")
    firebase_admin.initialize_app(cred, {
        "databaseURL": "https://simcaf-9ae4d-default-rtdb.firebaseio.com/"
    })

# Função para carregar dados
@st.cache_data
def load_data(environments, start_date, end_date):
    data = []
    for env in environments:
        ref = db.reference(f"/environments/{env}")
        env_data = ref.get()
        if env_data:
            for timestamp, values in env_data.items():
                if int(timestamp) >= int(start_date.timestamp()) and int(timestamp) <= int(end_date.timestamp()):
                    values["timestamp"] = timestamp
                    values["environment"] = env
                    data.append(values)
    return pd.DataFrame(data)

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

# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/250x100?text=SIMCAF+Logo", caption="Sistema de Monitoramento")
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
        environments = st.multiselect("Ambientes", allowed_environments, default=allowed_environments[:1])
        start_date = st.date_input("De", format="DD/MM/YYYY", value=datetime.now() - timedelta(days=30))
        end_date = st.date_input("Até", format="DD/MM/YYYY", value=datetime.now())
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.user_data = None
            st.rerun()

# Dashboard principal
if st.session_state.logged_in and environments:
    st.title("Sistema de Monitoramento de Cadeia de Frio")
    st.header(f"Monitoramento: {', '.join(environments)}", divider="blue")

    # Carregar dados
    df = load_data(environments, start_date, end_date)

    if not df.empty:
        # Grid de métricas
        mygrid = grid(5, 5, 5, 5, vertical_align="top")
        for env in environments:
            env_df = df[df["environment"] == env]
            if not env_df.empty:
                latest = env_df.iloc[-1]
                c = mygrid.container(border=True)
                c.subheader(latest["location"], divider="red")
                colA, colB, colC = c.columns(3)
                icon_map = {
                    "carro_001": "https://img.icons8.com/color/48/truck.png",
                    "hospital_periferia": "https://img.icons8.com/color/48/hospital.png",
                    "laboratorio_estadual": "https://img.icons8.com/color/48/laboratory.png",
                    "estoque_interior": "https://img.icons8.com/color/48/warehouse.png"
                }
                colA.image(icon_map.get(env, "https://img.icons8.com/color/48/thermometer.png"), width=85)
                colB.metric(label="Temperatura", value=f"{latest['temperature']:.1f}°C")
                colC.metric(label="Alertas", value=f"{latest.get('alert_count', 0)}")
                style_metric_cards(background_color='rgba(255,255,255,0)')

        # Layout principal
        col_map, col_charts = st.columns([1, 2])

        # Mapa
        with col_map:
            st.subheader("Localização", divider="gray")
            if "carro_001" in environments and "latitude" in df.columns and "longitude" in df.columns:
                latest_data = df[df["environment"] == "carro_001"].iloc[-1]
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
            st.subheader("Monitoramento de Sensores")
            fig = px.line(
                df,
                x="timestamp",
                y=["temperature", "humidity", "uv"],
                color="environment",
                labels={"timestamp": "Timestamp", "value": "Valor", "variable": "Métrica"},
                height=600
            )
            fig.update_layout(
                xaxis_tickformat="%d/%m/%Y",
                yaxis_title="Valor",
                legend_title="Métrica/Ambiente"
            )
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("Temperatura vs. Umidade")
            fig = px.scatter(
                df,
                x="temperature",
                y="humidity",
                color="environment",
                text="environment",
                size="uv",
                height=400
            )
            fig.update_traces(textfont_color='white', textfont_size=10)
            fig.layout.xaxis.title = "Temperatura (°C)"
            fig.layout.yaxis.title = "Umidade (%)"
            st.plotly_chart(fig, use_container_width=True)

        # Tabela de alertas
        st.subheader("Alertas Recentes", divider="red")
        alerts_data = []
        for env in environments:
            ref_alerts = db.reference(f"/alerts/{env}")
            alerts = ref_alerts.get()
            if alerts and isinstance(alerts, dict):
                for ts, values in alerts.items():
                    values["timestamp"] = ts
                    values["environment"] = env
                    alerts_data.append(values)
        if alerts_data:
            df_alerts = pd.DataFrame(alerts_data)[["timestamp", "sensor_id", "reason", "temperature", "environment"]]
            def highlight_alerts(row):
                return ['background-color: #4b0000' if row["reason"] else '' for _ in row]
            styled_df = df_alerts.style.apply(highlight_alerts, axis=1).format({"temperature": "{:.1f}"})
            st.dataframe(styled_df, use_container_width=True)
        else:
            st.warning("Nenhum alerta disponível.", icon="⚠️")
    else:
        st.warning("Nenhum dado disponível para os ambientes selecionados.", icon="⚠️")
else:
    st.info("Por favor, faça login para acessar o dashboard.")