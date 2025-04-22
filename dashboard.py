import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import pandas as pd

# === CONFIGURAÇÃO DO FIREBASE ===
# Carrega as credenciais do Firebase
cred = credentials.Certificate("chave_firebase.json")  
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://simcaf-9ae4d-default-rtdb.firebaseio.com"
})

# === FUNÇÃO PARA BUSCAR DADOS ===
def buscar_dados():
    ref = db.reference("dados/DHT11_01")  # Caminho no Firebase
    dados = ref.get()
    if dados:
        # Converte os dados em um DataFrame
        df = pd.DataFrame.from_dict(dados, orient="index")
        df.index = pd.to_datetime(df.index, unit="s")  # Converte timestamps Unix (em segundos) para formato de data legível
        df.sort_index(inplace=True)  # Ordena pelo timestamp
        return df
    else:
        return pd.DataFrame()  # Retorna DataFrame vazio se não houver dados

# === FUNÇÃO PARA BUSCAR ALERTAS ===
def buscar_alertas():
    ref = db.reference("alertas")  # Caminho para alertas no Firebase
    alertas = ref.get()
    if alertas:
        return pd.DataFrame.from_dict(alertas, orient="index")
    else:
        return pd.DataFrame()

# === INTERFACE DO DASHBOARD ===
st.title("Dashboard - Monitoramento de Vacinas")
st.subheader("Dados em Tempo Real")

# Busca e exibe os dados dos sensores
df = buscar_dados()
if not df.empty:
    st.line_chart(df[["temperature", "humidity", "uv"]])  # Gráfico para temperatura, umidade e UV
    st.dataframe(df.tail(5))  # Mostra as últimas 5 leituras
else:
    st.write("Nenhum dado encontrado.")

# Busca e exibe alertas
st.subheader("Alertas")
alertas = buscar_alertas()
if not alertas.empty:
    st.dataframe(alertas)  # Mostra os alertas em formato de tabela
else:
    st.write("Nenhum alerta registrado.")
