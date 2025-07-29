#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <DHT.h>

#define DHTPIN D4     // DHT pin
#define DHTTYPE DHT11
#define PUMP_PIN D1   // Pump pin
#define SOIL_PIN A0   // Soil pin

DHT dht(DHTPIN, DHTTYPE);

const char* ssid = "<YOUR_SSID>";
const char* password = "<PSWD>";
const char* mqtt_server = "<MQTT_BROKER_IP>";

WiFiClient espClient;
PubSubClient client(espClient);

// Soil moisture variables (thresholds and actual value)
int moistureTh;
int soilHumidity;

// Temperature variables (thresholds and actual value)
int tempMin;
int tempMax;
int temperature;

// Humidity variables (thresholds and actual value)
int humidityTh; // %
int humidity;

// Irrigation duration parameters
const float FACTOR = 0.5; // Seconds/difference percentage point
const unsigned long MAX_IRRIGATION_DURATION = 60000; // max 60s

// MQTT topics
const char* pot_id = "pot_0"; // Pot ID
String topic_data   = "smartplant/"+String(pot_id)+"/data";
String topic_ready  = "smartplant/"+String(pot_id)+"/ready";
String topic_cmd    = "smartplant/"+String(pot_id)+"/cmd";


// Variables for timing automatic sensors readings
const float minutes = 1; // 1 just for tests (120 in real-world application)
const unsigned long sleepDuration = minutes * 60 * 1e6; 

bool parametersReceived = false;

void setup_wifi(){
  delay(10);
  // We start by connecting to a WiFi network
  WiFi.begin(ssid, password);
  Serial.println("Connecting to WiFi...");
  while(WiFi.status()!= WL_CONNECTED){
    delay(500);
    Serial.print(".");
  }
  Serial.println("Connected to WiFi");
}

int toPercentage(int sensorRead){
  const int dry = 1024; // sensor in air (completely dry)
  const int wet = 740; // sensor in water (completely wet)

  // avoid logarithm overflow
  sensorRead = constrain(sensorRead, wet, dry);
  
  // normalizing between 0 (dry) and 1 (wet)
  float normalized = (float)(sensorRead - wet) / (dry - wet);

  // Invert to get 100% for wet and 0% for dry
  float inverted = 1.0 - normalized;
  // Applying logarithmic curve (log10)
  float humidity = 100 * log10(9 * inverted + 1);

  humidity = constrain(humidity, 0, 100);

  return (int)humidity;
}

void publishSensorData(){
  soilHumidity = analogRead(SOIL_PIN);
  temperature = dht.readTemperature();
  humidity = dht.readHumidity();
  bool isIrrigated = false; 
  char buffer[256];
  StaticJsonDocument<256> doc;

  // Converting soilHumidity analog read to % values
  soilHumidity = toPercentage(soilHumidity);

  // evaluating if the plant needs water
  bool soil_cond = soilHumidity < moistureTh;
  bool temp_cond = temperature > tempMax;
  bool humidity_cond = humidity < humidityTh; 
  bool irrigate_cond = soil_cond || temp_cond || humidity_cond;

  bool irrigate_cond2 = soilHumidity > (moistureTh * 1.2);
  
  if(irrigate_cond2)
    irrigate_cond=false;

  if(irrigate_cond==true) { 
    int delta = moistureTh - soilHumidity;
    if(delta > 0){ 

      float duration = float(delta * FACTOR * 1000); 
      if(temperature < tempMin)
        duration *= 0.8; // less irrigation duration of 20%
      if(temperature > tempMax) 
        duration *= 1.1; // additional 10% of time 
      if(humidity < humidityTh) 
        duration *= 1.05; // additional 5% of time

      if(duration > MAX_IRRIGATION_DURATION)
        duration = MAX_IRRIGATION_DURATION;
    
      // Irrigation
      digitalWrite(PUMP_PIN, HIGH);
      delay((unsigned long)duration); 
      digitalWrite(PUMP_PIN, LOW);

    }
  }

  doc["humidity_value"]    = humidity;
  doc["temperature_value"] = temperature;
  doc["soil_moisture_value"]     = soilHumidity;
  doc["need_water"]        = irrigate_cond;

  serializeJson(doc, buffer);
  client.publish(topic_data.c_str(), buffer);
  delay(500);
  Serial.println("Buffer: \n"+ String(buffer));
}

void mqtt_callback(char* topic, byte* payload, unsigned int length) {
  StaticJsonDocument<256> doc;

  payload[length] = '\0';

  DeserializationError err = deserializeJson(doc, payload);
  if (err) 
    return;

  String action = doc["action"].as<String>();

  if(action == "save_parameters"){
    moistureTh = doc["soil_threshold"];
    humidityTh = doc["humidity_threshold"];
    tempMin     = doc["temperature_range"][0];
    tempMax     = doc["temperature_range"][1];

    parametersReceived = true;
  }
}

void reconnect() {
  while (client.connected()==0) {
    if (client.connect("pot_0")) {
        Serial.println("MQTT Connected");
    } else {
      Serial.print("Failed, rc=");
      Serial.print(client.state());
      Serial.println(" trying again in 5 seconds");
      delay(5000); // waits for 5 seconds
    }
  }
}

void setup() {
  Serial.begin(9600);
  pinMode(PUMP_PIN, OUTPUT);
  dht.begin();
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(mqtt_callback);
  
  if(!client.connected()){
    reconnect();
    client.subscribe(topic_cmd.c_str());
    client.publish(topic_ready.c_str(), "");
  }

  while (!parametersReceived) {
    client.loop(); 
  }

  publishSensorData();

  // Going to sleep for saving battery
  ESP.deepSleep(sleepDuration);
}

void loop() {
  // nothing here, saving battery
}
