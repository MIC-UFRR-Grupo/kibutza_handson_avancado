#include <DHT.h>
#include <ArduinoJson.h>
#include <WiFi.h>
#include <Firebase_ESP_Client.h>
#include <time.h> // Biblioteca para NTP (sincronização de horário)

// === CONFIGURAÇÃO DE PINOS ===
#define DHTPIN 15
#define DHTTYPE DHT11
#define LEDPIN 2         // LED de alerta (vermelho)
#define LED_GREEN_PIN 4  // LED verde (condição normal)
#define UVPIN 32

DHT dht(DHTPIN, DHTTYPE);

// === CONFIGURAÇÃO DO FIREBASE ===
#define FIREBASE_HOST "https://simcaf-9ae4d-default-rtdb.firebaseio.com"
#define FIREBASE_AUTH "AIzaSyDkOIfjWdKtXWBM6YDudsVF2u9GSmbUoks"

FirebaseData fbdo;
FirebaseAuth auth;
FirebaseConfig config;

// === CONFIGURAÇÃO DO WI-FI ===
const char* ssid = "CIT_Alunos";
const char* password = "alunos@2024";

// === FUNÇÃO PARA SINCRONIZAR O HORÁRIO COM NTP ===
void inicializarNTP() {
  configTime(-3 * 3600, 0, "pool.ntp.org", "time.nist.gov"); // GMT-3 (Horário de Brasília)
  Serial.println("Sincronizando com NTP...");
  while (time(nullptr) < 100000) {
    delay(100);
  }
  Serial.println("✅ Sincronização NTP concluída!");
}

// Retorna o timestamp atual em segundos desde a época Unix
String obterTimestamp() {
  time_t agora = time(nullptr);
  return String(agora); // Retorna o timestamp Unix
}

void setup() {
  Serial.begin(115200);
  Serial.println("\nInicializando ESP32...");

  dht.begin();
  pinMode(LEDPIN, OUTPUT);       // Configura o LED de alerta como saída
  pinMode(LED_GREEN_PIN, OUTPUT); // Configura o LED verde como saída

  // Conecta ao Wi-Fi
  Serial.println("Conectando ao Wi-Fi...");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("\n✅ Wi-Fi conectado!");

  // Configuração do Firebase
  config.api_key = FIREBASE_AUTH;
  config.database_url = FIREBASE_HOST;
  Firebase.reconnectWiFi(true);
  Firebase.begin(&config, &auth);

  if (Firebase.signUp(&config, &auth, "", "")) {
    Serial.println("✅ Autenticação anônima bem-sucedida!");
  } else {
    Serial.printf("❌ Erro na autenticação: %s\n", config.signer.signupError.message.c_str());
  }

  if (Firebase.ready()) {
    Serial.println("✅ Firebase conectado!");
  } else {
    Serial.printf("❌ Erro na inicialização do Firebase: %s\n", fbdo.errorReason());
  }

  inicializarNTP();  // Sincroniza o horário com NTP
}

void loop() {
  // === LEITURA DOS SENSORES ===
  float temperatura = dht.readTemperature();
  float umidade = dht.readHumidity();
  int leituraUV = analogRead(UVPIN);
  float tensaoUV = leituraUV * (3.3 / 4095.0);

  if (isnan(temperatura) || isnan(umidade)) {
    Serial.println("❌ Erro ao ler os dados do DHT11!");
    delay(10000);
    return;
  }

  // === ALGORITMO DE ANÁLISE DE DADOS ===
  bool alertaTemperatura = (temperatura < 2.0 || temperatura > 8.0);
  bool alertaUV = (tensaoUV > 1.0);
  bool condicaoCritica = alertaTemperatura || alertaUV;

  String motivoAlerta = "";
  if (condicaoCritica) {
    Serial.println("⚠️ ALERTA: Condições críticas detectadas!");
    Serial.printf("Temperatura: %.1f°C (Fora do intervalo 2-8°C)\n", temperatura);
    Serial.printf("Umidade: %.1f%%\n", umidade);
    Serial.printf("UV: %.2fV (Limite: 1.0V)\n", tensaoUV);
    digitalWrite(LEDPIN, HIGH);       // Liga o LED de alerta (vermelho)
    digitalWrite(LED_GREEN_PIN, LOW); // Desliga o LED verde

    if (alertaTemperatura) {
      motivoAlerta += "Temperatura fora do intervalo (2-8°C). ";
    }
    if (alertaUV) {
      motivoAlerta += "UV acima do limite (1.0V).";
    }
  } else {
    Serial.println("✅ Tudo normal.");
    Serial.printf("Temperatura: %.1f°C\n", temperatura);
    Serial.printf("Umidade: %.1f%%\n", umidade);
    Serial.printf("UV: %.2fV\n", tensaoUV);
    digitalWrite(LEDPIN, LOW);         // Desliga o LED de alerta (vermelho)
    digitalWrite(LED_GREEN_PIN, HIGH); // Liga o LED verde
  }

  // === GERAÇÃO DE TIMESTAMP ===
  String timestamp = obterTimestamp(); // Usa o horário real (NTP)

  // === DADOS JSON PARA O FIREBASE (Leituras) ===
  FirebaseJson json;
  json.set("sensor_id", "DHT11_01");
  json.set("location", "Farmacia_A");
  json.set("temperature", temperatura);
  json.set("humidity", umidade);
  json.set("uv", tensaoUV);
  json.set("timestamp", timestamp);
  json.set("critical_condition", condicaoCritica);

  Serial.println("=== JSON Gerado (Leituras) ===");
  json.toString(Serial);
  Serial.println("\n===================");

  // === ENVIA OS DADOS PARA O FIREBASE (Leituras) ===
  String path = "/dados/DHT11_01/" + timestamp;
  Serial.print("Enviando dados para o Firebase... ");
  if (Firebase.ready() && Firebase.RTDB.setJSON(&fbdo, path.c_str(), &json)) {
    Serial.println("✅ Dados enviados com sucesso!");
  } else {
    Serial.println("❌ Erro ao enviar dados: " + fbdo.errorReason());
  }

  // === REGISTRO DE ALERTAS NO FIREBASE ===
  if (condicaoCritica) {
    FirebaseJson alertJson;
    alertJson.set("sensor_id", "DHT11_01");
    alertJson.set("location", "Farmacia_A");
    alertJson.set("temperature", temperatura);
    alertJson.set("uv", tensaoUV);
    alertJson.set("timestamp", timestamp);
    alertJson.set("reason", motivoAlerta);

    String alertPath = "/alertas/" + timestamp;
    Serial.print("Registrando alerta no Firebase... ");
    if (Firebase.ready() && Firebase.RTDB.setJSON(&fbdo, alertPath.c_str(), &alertJson)) {
      Serial.println("✅ Alerta registrado com sucesso!");
    } else {
      Serial.println("❌ Erro ao registrar alerta: " + fbdo.errorReason());
    }
  }

  delay(10000); // Intervalo de 10 segundos
}
