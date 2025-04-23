import firebase_admin
from firebase_admin import credentials, db
import time
from datetime import datetime

# Inicializar o Firebase
cred = credentials.Certificate("simcaf-9ae4d-firebase-adminsdk-fbsvc-ad2aa2c568.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://vaccinemonitoring-default-rtdb.firebaseio.com/"
})

# Referência ao banco
ref = db.reference("/")

# Dados simulados
timestamp = datetime.now().isoformat()
sensor_data = {
    "sensor_data": {
        timestamp: {
            "sensor_id": "DHT11_01",
            "location": "Farmacia_A",
            "temperature_raw": 5.2,
            "humidity_raw": 60.5,
            "temperature_filtered": 5.2,
            "humidity_filtered": 60.5,
            "timestamp": timestamp
        }
    },
    "alerts": {
        timestamp: {
            "sensor_id": "DHT11_01",
            "location": "Farmacia_A",
            "alert_type": "temperature_high",
            "alert_status": True,
            "alert_message": "Temp Alta: 9°C",
            "timestamp": timestamp
        }
    }
}

# Inserir dados
ref.set(sensor_data)
print("Dados inseridos com sucesso!")