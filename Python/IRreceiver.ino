/*

IR Receiver using the IRremoteESP8266 and PubSubClient libraries.
Using the IRremoveESP8266 example "IRrecvDumpV2" and PubSubClient example "mqtt_ESP8266"

*/
#include <IRremoteESP8266.h>
#include <Arduino.h>
#include <assert.h>
#include <IRrecv.h>
#include <IRac.h>
#include <IRtext.h>
#include <IRutils.h>
#include <WiFi.h>
#include <AsyncTCP.h>
#include <PubSubClient.h>

// IRremoteESP8266
const uint16_t kRecvPin = 14;
const uint32_t kBaudRate = 115200;
const uint16_t kCaptureBufferSize = 1024;
const uint8_t kTimeout = 50;
const uint16_t kMinUnknownSize = 12;
const uint8_t kTolerancePercentage = kTolerance;  
#define LEGACY_TIMING_INFO false

// MQTT 
const char* ssid = "SmartSystems";
const char* password = "MovingTargets";
const char* mqtt_server = "broker.hivemq.com";

WiFiClient espClient;
PubSubClient client(espClient);
unsigned long lastMsg = 0;
#define MSG_BUFFER_SIZE	(50)
char msg[MSG_BUFFER_SIZE];

void setup_wifi() {

  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  randomSeed(micros());

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");

    String clientId = "ESP32-S3-SmartSystems";
    clientId += String(random(0xffff), HEX);

    if (client.connect(clientId.c_str())) {
      Serial.println("connected");
      client.publish("outTopic", "hello world");

    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

IRrecv irrecv(kRecvPin, kCaptureBufferSize, kTimeout, true);
decode_results results;  

void setup() {
  Serial.begin(kBaudRate);
  while (!Serial)  
    delay(50);

  assert(irutils::lowLevelSanityCheck() == 0);
  Serial.printf("\n" D_STR_IRRECVDUMP_STARTUP "\n", kRecvPin);

#if DECODE_HASH
  irrecv.setUnknownThreshold(kMinUnknownSize);
#endif  
  irrecv.setTolerance(kTolerancePercentage);  
  irrecv.enableIRIn();  

  Serial.begin(115200);
  setup_wifi();
  client.setServer(mqtt_server, 1883);
}

void loop() {
  if (irrecv.decode(&results)) {
    uint32_t now = millis();
    if ((typeToString(results.decode_type) == "SONY") && (results.address = 0x1) && (results.command == 0x25) && (results.value == 0xA50))
    {
      if (now - lastMsg > 200) {
        lastMsg = now; 
        snprintf (msg, MSG_BUFFER_SIZE, "Hit Registered");
        client.publish("MovingTargetsSmartSystems", msg); 
        Serial.print("Hit registered at time: ");
        Serial.println(now);
      }
    } 
    else {
      Serial.println("Wrong IR result");
      snprintf (msg, MSG_BUFFER_SIZE, "Wrong IR signal");
      client.publish("MovingTargetsSmartSystems", msg);
    }
    Serial.println("");

  }
  if (!client.connected()) 
      {
        reconnect();
      }
      client.loop();
}