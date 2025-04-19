from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import WritePrecision, SYNCHRONOUS
import time


# Configurações do InfluxDB Cloud
url = "https://us-west-2-1.aws.cloud2.influxdata.com"  # Ajuste para sua região
token = "seu-token-copiado"  # Cole o token salvo
org = "VaccineMonitoring"
bucket = "vaccine_monitoring"

# Conectar ao InfluxDB (modo síncrono para evitar problema de threads)
client = InfluxDBClient(url=url, token=token, org=org)
write_api = client.write_api(write_options=SYNCHRONOUS)

# Dados simulados para sensor_data
sensor_points = [
    Point("sensor_data")
    .tag("sensor_id", "DHT11_01")
    .tag("location", "Farmacia_A")
    .field("temperature_raw", 5.2)
    .field("humidity_raw", 60.5)
    .field("temperature_filtered", 5.1)  # Placeholder
    .field("humidity_filtered", 60.3)    # Placeholder
    .time(time.time_ns(), WritePrecision.NS),
    Point("sensor_data")
    .tag("sensor_id", "GuvaS12SD_01")
    .tag("location", "Farmacia_A")
    .field("uv_raw", 0.1)
    .field("uv_filtered", 0.09)  # Placeholder
    .time(time.time_ns(), WritePrecision.NS)
]

# Dados simulados para alerts
alert_point = (
    Point("alerts")
    .tag("sensor_id", "DHT11_01")
    .tag("location", "Farmacia_A")
    .tag("alert_type", "temperature_high")
    .field("alert_status", True)
    .field("alert_message", "Temp Alta: 9°C")
    .time(time.time_ns(), WritePrecision.NS)
)

# Inserir dados
write_api.write(bucket=bucket, org=org, record=sensor_points + [alert_point])
print("Dados inseridos com sucesso!")

# Fechar conexão
client.close()

