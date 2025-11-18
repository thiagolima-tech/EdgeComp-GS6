#include <WiFi.h>
#include <PubSubClient.h>
 
// =========================
// CONFIGURAÇÕES DE REDE / MQTT
// =========================
const char* default_SSID            = "Wokwi-GUEST";   // Nome da rede Wi-Fi
const char* default_PASSWORD        = "";              // Senha da rede Wi-Fi
 
const char* default_BROKER_MQTT     = "44.223.43.74";  // IP do Broker MQTT
const int   default_BROKER_PORT     = 1883;            // Porta do Broker MQTT
 
const char* default_TOPICO_SUBSCRIBE = "/TEF/device069/cmd";
const char* default_TOPICO_PUBLISH_1 = "/TEF/device069/attrs";
const char* default_TOPICO_PUBLISH_2 = "/TEF/device069/attrs/p";
const char* default_ID_MQTT          = "fiware_001";
 
const int default_D4 = 2;  // LED onboard (GPIO2)
 
// =========================
// PINOS E LÓGICA DE LUMINOSIDADE
// =========================
const int LDR_PIN = 34;
 
// 👉 AJUSTE ESSES DOIS VALORES CONFORME MEDIDAS REAIS
// quanto MAIOR o LDR, MENOS luz
const int LDR_BRIGHT_MAX = 1200;  // até aqui: MUITA luz  -> OK
const int LDR_DARK_MIN   = 3000;  // daqui pra cima: ESCURO -> OK
// entre LDR_BRIGHT_MAX e LDR_DARK_MIN: ALERTA
 
WiFiClient espClient;
PubSubClient mqttClient(espClient);
 
// 0 = escuro OK, 1 = ALERTA, 2 = claro OK
int estadoLuminosidade = -1;
 
// =========================
// FUNÇÕES AUXILIARES
// =========================
void conectaWiFi() {
  Serial.print("Conectando ao WiFi: ");
  Serial.println(default_SSID);
 
  WiFi.mode(WIFI_STA);
  WiFi.begin(default_SSID, default_PASSWORD);
 
  unsigned long inicio = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - inicio < 20000) { // 20s timeout
    delay(500);
    Serial.print(".");
  }
 
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi conectado!");
    Serial.print("IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\nFalha ao conectar no WiFi (timeout).");
  }
}
 
void conectaMQTT() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Sem WiFi, não vou tentar MQTT agora.");
    return;
  }
 
  while (!mqttClient.connected()) {
    Serial.print("Conectando ao broker MQTT ");
    Serial.print(default_BROKER_MQTT);
    Serial.print(":");
    Serial.print(default_BROKER_PORT);
    Serial.print(" ... ");
 
    if (mqttClient.connect(default_ID_MQTT)) {
      Serial.println("conectado!");
      // mqttClient.subscribe(default_TOPICO_SUBSCRIBE);
    } else {
      Serial.print("falhou, rc=");
      Serial.print(mqttClient.state());
      Serial.println(" tentando novamente em 3 segundos...");
      delay(3000);
    }
  }
}
 
void setup() {
  Serial.begin(115200);
  delay(1000);
 
  Serial.println("\nIniciando sensor de luminosidade com 3 estados (OK/ALERTA/OK)...");
 
  pinMode(LDR_PIN, INPUT);
  pinMode(default_D4, OUTPUT);
  digitalWrite(default_D4, LOW);
 
  conectaWiFi();
  mqttClient.setServer(default_BROKER_MQTT, default_BROKER_PORT);
  conectaMQTT();
}
 
void loop() {
  // Mantém conexões
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi caiu, tentando reconectar...");
    conectaWiFi();
  }
  if (!mqttClient.connected()) {
    Serial.println("MQTT desconectado, tentando reconectar...");
    conectaMQTT();
  }
  mqttClient.loop();
 
  // Leitura do LDR
  int ldrValue = analogRead(LDR_PIN);
  Serial.print("LDR: ");
  Serial.println(ldrValue);
 
  // quanto MAIOR o valor, MENOS luz
  int novoEstado;
 
  if (ldrValue >= LDR_DARK_MIN) {
    // Escuro / sem luminosidade -> OK
    novoEstado = 0;
  } else if (ldrValue <= LDR_BRIGHT_MAX) {
    // Muito claro / muita luz -> OK
    novoEstado = 2;
  } else {
    // Faixa intermediária -> ALERTA
    novoEstado = 1;
  }
 
  // Só envia MQTT se o estado mudou
  if (novoEstado != estadoLuminosidade) {
    estadoLuminosidade = novoEstado;
 
    String payload;
 
    if (estadoLuminosidade == 0) {
      // Escuro OK
      payload = String("{\"status\":\"OK\",\"nivel\":\"BAIXO\",\"mensagem\":\"Sem luminosidade (escuro)\",\"ldr\":")
                + ldrValue + "}";
      Serial.println("Estado: ESCURO OK, enviando MQTT...");
      digitalWrite(default_D4, LOW); // LED apagado (ok)
 
    } else if (estadoLuminosidade == 2) {
      // Claro OK
      payload = String("{\"status\":\"OK\",\"nivel\":\"ALTO\",\"mensagem\":\"Muita luminosidade\",\"ldr\":")
                + ldrValue + "}";
      Serial.println("Estado: CLARO OK, enviando MQTT...");
      digitalWrite(default_D4, LOW); // LED apagado (ok)
 
    } else {
      // ALERTA (luminosidade intermediária)
      payload = String("{\"status\":\"ALERTA\",\"nivel\":\"INTERMEDIARIO\",\"mensagem\":\"Luminosidade intermediaria (pouca/média)\",\"ldr\":")
                + ldrValue + "}";
      Serial.println("Estado: ALERTA (luminosidade intermediária), enviando MQTT...");
      digitalWrite(default_D4, HIGH); // LED aceso em alerta
    }
 
    bool ok = mqttClient.publish(default_TOPICO_PUBLISH_1, payload.c_str());
    Serial.println(ok ? "Publish OK" : "Publish FALHOU");
  }
 
  delay(1000);
}