import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime

# Inicializar o Firebase
cred = credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://simcaf-9ae4d-default-rtdb.firebaseio.com/"
})

# Referência ao banco
ref = db.reference("/")

# Dados simulados
timestamp = str(int(datetime.now().timestamp()))
data = {
    "environments": {
        "carro_001": {
            timestamp: {
                "sensor_id": "DHT11_01",
                "location": "Carro em Trânsito",
                "temperature": 22.6,
                "humidity": 59,
                "uv": 0.46659,
                "latitude": -3.123,
                "longitude": 60.456,
                "critical_condition": True,
                "timestamp": timestamp
            }
        },
        "hospital_periferia": {
            timestamp: {
                "sensor_id": "DHT11_02",
                "location": "Hospital Periferia",
                "temperature": 5.2,
                "humidity": 60,
                "uv": 0.1,
                "critical_condition": False,
                "timestamp": timestamp
            }
        },
        "laboratorio_estadual": {
            timestamp: {
                "sensor_id": "DHT11_03",
                "location": "Laboratório Estadual",
                "temperature": 6.0,
                "humidity": 55,
                "uv": 0.2,
                "critical_condition": False,
                "timestamp": timestamp
            }
        },
        "estoque_interior": {
            timestamp: {
                "sensor_id": "DHT11_04",
                "location": "Estoque Interior",
                "temperature": 7.5,
                "humidity": 58,
                "uv": 0.15,
                "critical_condition": False,
                "timestamp": timestamp
            }
        }
    },
    "alerts": {
        "carro_001": {
            timestamp: {
                "sensor_id": "DHT11_01",
                "location": "Carro em Trânsito",
                "reason": "Temperatura fora do intervalo (2-8°C).",
                "temperature": 22.6,
                "timestamp": timestamp
            }
        }
    },
    "users": {
        "admin_001": {
            "role": "admin",
            "allowed_environments": ["carro_001", "hospital_periferia", "laboratorio_estadual", "estoque_interior"],
            "password": "admin123"
        },
        "gerente_hospital_001": {
            "role": "gerente_hospital",
            "allowed_environments": ["hospital_periferia"],
            "password": "hospital123"
        }
    }
}

# Inserir dados
ref.set(data)
print("Dados inseridos com sucesso!")