#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <DHT.h>

#define DHTPIN D4     // DHT pin
#define DHTTYPE DHT11
#define PUMP_PIN D1   // Pump pin
#define SOIL_PIN A0   // Soil pin

const char* ssid = "<SSID>";
const char* password = "<PASSWORD>";
const char* mqtt_server = "<BROKER_IP>";

WiFiClient espClient;
PubSubClient client(espClient);

// Soil moisture variables (thresholds and actual value)
int moistureTh = 50;
int soilHumidity;

// Temperature variables (thresholds and actual value)
int tempMin = 5;
int tempMax = 40;
int temperature;

// Humidity variables (thresholds and actual value)
int humidityTh = 50; // %
int humidity;


// Irrigation duration parameters
const float FACTOR = 2.0; // Seconds/difference percentage point
const unsigned long MAX_IRRIGATION_DURATION = 60000; // max 60s

// MQTT topics
const char* pot_id = "pot_5"; // Pot ID
String topic_data   = "smartplant/"+String(pot_id)+"/data";
String topic_ready  = "smartplant/"+String(pot_id)+"/ready";
String topic_cmd    = "smartplant/"+String(pot_id)+"/cmd";


// Variables for timing automatic sensors readings
float hours = 0.5; // adjust it for tests
const unsigned long sleepDuration = hours * 60UL * 60UL * 1000UL; // hours * min * sec * msec

bool readyToSleep = false;

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
  const float dry = 1024; // sensor in air (completely dry)
  const float wet = 740; // sensor in water (completely wet)

  // avoid logarithm overflow
  sensorRead = constrain(sensorRead, wet, dry);
  // normalizing between 0 (dry) and 1 (wet)
  float normalized = (dry - sensorRead) / (dry - wet);

  // Applying logarithmic curve (log10)
  float humidity = 100 * log10(9 * normalized + 1);

  humidity = constrain(humidity, 0, 100);

  return (int)humidity;
}

void publishSensorData(){
  soilHumidity = analogRead(SOIL_PIN);
  temperature = dht.readTemperature();
  humidity = dht.readHumidity();
  bool isIrrigated = false; 
  char buffer[256];

  Serial.println("Soil Humidity: "+soilHumidity);
  // Converting soilHumidity analog read to % values
  soilHumidity = toPercentage(soilHumidity);
  Serial.println("Soil Humidity (%): "+soilHumidity+ 
                "\nTemperature (°C): "+temperature+
                "\nEnvironment Humidity: "+humidity);
  // evaluating if the plant needs water
  bool soil_cond = soilHumidity < moistureTh;
  bool temp_cond = temp > tempMax;
  bool humidity_cond = humidity < humidityTh; 
  bool irrigate_cond = soil_cond || temp_cond || humidity_cond;
  doc["need_water"] = String(irrigate_cond ? true : false);

  Serial.println("Plant must be irrigated: "+irrigate_cond);
  if(irrigate_cond) { 
    int delta = soilHumidity - moistureTh;
    if(delta > 0){ 
      float duration = delta * FACTOR * 1000.0; 
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
      delay(45000); // waiting for water to soak in 

      new_soilHumidity = analogRead(SOIL_PIN); // measuring soil humidity again
      new_soilHumidity = toPercentage(soilHumidity);
      // evaluating if watered properly or some problem occurred
      if(new_soilHumidity > soilHumidity && new_soilHumidity > moistureTh){
        isIrrigated = true;
        Serial.println("Plant has been irrigated");
      }else{
        isIrrigated = false;
        Serial.println("Plant has not been irrigated: out of water or pump fault");
      }
    }
  }
  StaticJsonDocument<256> doc;
  doc["humidity_value"]    = String(humidity);
  doc["temperature_value"] = String(temperature);
  doc["soil_moisture"]     = String(new_soilHumidity);
  doc["is_irrigated"]      = String(isIrrigated);
  doc["need_water"]        = String(irrigate_cond);

  serializeJson(doc, buffer);
  client.publish(topic_data.c_str(), buffer);

  Serial.println("Data published");
}

void mqtt_callback(char* topic, byte* payload, unsigned int length) {
  payload[length] = '\0';

  StaticJsonDocument<256> doc;
  DeserializationError err = deserializeJson(doc, payload);
  if (err) 
    return;

  String action = doc["action"];

  if(action == "save_parameters"){
    moistureTh = doc["soil_threshold"];
    humidityTh = doc["humidity_threshold"];
    tempMin     = doc["temperature_range"][0];
    tempMax     = doc["temperature_range"][1];

    Serial.println("Saved parameters:\n
                    Soil moisture threshold: "+moistureTh+
                    "\nHumidity threshold: "+humidityTh+
                    "\nTemperature thresholds (min:max): ("+tempMin+":"+
                    tempMax+")");
  }
}

void reconnect() {
  while (!client.connected()) {
    if (client.connect("NodeMCU_pot_5")) {
      client.subscribe(topic_cmd.c_str());
      client.publish(topic_ready.c_str());
    } else {
      delay(5000); // waits for 5 seconds
    }
  }
}

void setup() {
  pinMode(PUMP_PIN, OUTPUT);
  dht.begin();
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(mqtt_callback);
  unsigned long tStart = millis();
  
  while (!parametersReceived && millis() - tStart < 15000) {
    client.loop(); // attendi fino a 15s i parametri
  }

  publishSensorData();

  // Going to sleep for saving battery
  Serial.println("Going to sleep for 2 hours...");
  ESP.deepSleep(sleepDuration);
}

void loop() {
  // nothing here, saving battery
}