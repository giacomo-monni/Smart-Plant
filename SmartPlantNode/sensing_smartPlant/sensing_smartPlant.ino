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
const char* password = "<PASSWD>";
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
const int FACTOR = 2; // Seconds/difference percentage point
const unsigned long MAX_IRRIGATION_DURATION = 60000; // max 60s

// MQTT topics
const char* pot_id = "pot_0"; // Pot ID
String topic_data   = "smartplant/"+String(pot_id)+"/data";
String topic_ready  = "smartplant/"+String(pot_id)+"/ready";
String topic_cmd    = "smartplant/"+String(pot_id)+"/cmd";


// Variables for timing automatic sensors readings
const float hours = 60; // adjust it for tests
const unsigned long sleepDuration = hours * 1e6; 

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
  int new_soilHumidity;
  StaticJsonDocument<256> doc;

  // Converting soilHumidity analogue read to % values
  soilHumidity = toPercentage(soilHumidity);
  new_soilHumidity = soilHumidity;
  Serial.println("Soil Humidity (%): "+String(soilHumidity)+
                "\nTemperature (°C): "+String(temperature)+
                "\nEnvironment Humidity: "+String(humidity));

  // evaluating if the plant needs water
  bool soil_cond = soilHumidity < moistureTh;
  bool temp_cond = temperature > tempMax;
  bool humidity_cond = humidity < humidityTh; 
  bool irrigate_cond = soil_cond || temp_cond || humidity_cond;
  //doc["need_water"] = irrigate_cond;

  if(irrigate_cond==true) { 
    int delta = moistureTh - soilHumidity;
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
      new_soilHumidity = toPercentage(new_soilHumidity);

      // evaluating if watered properly or some problem occurred
      if(new_soilHumidity > soilHumidity && new_soilHumidity > moistureTh)
        isIrrigated = true;
      else
        isIrrigated = false;
    }
  }

  doc["humidity_value"]    = humidity;
  doc["temperature_value"] = temperature;
  doc["soil_moisture_value"]     = new_soilHumidity;
  doc["is_irrigated"]      = isIrrigated;
  doc["need_water"]        = irrigate_cond;

  serializeJson(doc, buffer);
  client.publish(topic_data.c_str(), buffer);
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

    Serial.println("Saved parameters:\nSoil moisture threshold: "+String(moistureTh)+
                  "\nHumidity threshold: "+String(humidityTh)+
                  "\nTemperature thresholds (min:max): ("+String(tempMin)+":"+String(tempMax)+")");
    parametersReceived = true;
  }
}

void reconnect() {
  while (client.connected()==0) {
    if (client.connect("pot_0")) {
      client.subscribe(topic_cmd.c_str());
      client.publish(topic_ready.c_str(), "");
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
  delay(5000);
  pinMode(PUMP_PIN, OUTPUT);
  dht.begin();
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(mqtt_callback);
  
  if(!client.connected()){
    reconnect();
  }

  while (!parametersReceived) {
    client.loop(); 
  }

  publishSensorData();

  // Going to sleep to save battery
  ESP.deepSleep(sleepDuration);
}

void loop() {
  // nothing here, saving battery
}
