#include <DHT.h>

// === CONFIGURAÇÃO DE PINOS ===
#define DHTPIN 15         // Pino do sinal do DHT11
#define DHTTYPE DHT11     // Tipo do sensor DHT
#define LEDPIN 2          // Pino do LED de alerta
#define UVPIN 34          // Entrada analógica para UVM-30A (GPIO 34 no ESP32)

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(115200);      // Inicia comunicação serial
  dht.begin();               // Inicia o sensor DHT
  pinMode(LEDPIN, OUTPUT);   // Configura o LED como saída
}

void loop() {
  // === LEITURA DOS SENSORES ===
  float temperatura = dht.readTemperature(); // Celsius
  float umidade = dht.readHumidity();
  int leituraUV = analogRead(UVPIN);         // Leitura analógica bruta
  float tensaoUV = leituraUV * (3.3 / 4095.0); // Conversão ADC para volts

  // === EXIBE NO SERIAL ===
  Serial.print("Temperatura: ");
  Serial.print(temperatura);
  Serial.print(" °C | Umidade: ");
  Serial.print(umidade);
  Serial.print(" % | UV: ");
  Serial.print(tensaoUV, 2);
  Serial.println(" V");

  // === VERIFICA CONDIÇÕES DE ALERTA ===
  if (temperatura > 8.0 || temperatura < 2.0 || tensaoUV > 1.0) {
    digitalWrite(LEDPIN, HIGH); // Alerta ativado
  } else {
    digitalWrite(LEDPIN, LOW); // Tudo normal
  }

  delay(2000); // Espera 2 segundos antes de repetir
}
