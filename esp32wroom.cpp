#include <WiFi.h>
#include <HTTPClient.h>
#include <EEPROM.h>
#include <Wire.h>
#include <ArduinoJson.h>
#include <DHT.h>
#include <WebServer.h>

#define DHTPIN 4
#define DHTTYPE DHT22
DHT dht(DHTPIN, DHTTYPE);

#define LED_PIN 2 // Built-in LED for visual feedback
#define EEPROM_SIZE 512

const char* ssid = "U";
const char* password = "29041991";
const char* apiEndpoint = "http://windevs.uz/api/sensor-data/";
const char* tokenEndpoint = "http://windevs.uz/api/token/";
const char* refreshEndpoint = "http://windevs.uz/api/token/refresh/";
const char* basicAuthUsername = "admin";
const char* basicAuthPassword = "admin";

String jwtToken;
String refreshTokenString;
unsigned long tokenExpiryTime = 0;

WebServer server(80);

unsigned long startTime;

void setup() {
  Serial.begin(9600);
  pinMode(LED_PIN, OUTPUT);
  EEPROM.begin(EEPROM_SIZE);
  dht.begin();
  
  connectToWiFi();
  startWebServer();
  
  // Initialize start time for uptime calculation
  startTime = millis();
  
  // Obtain initial tokens
  if (!obtainTokens()) {
    Serial.println("Failed to obtain initial tokens");
    return;
  }
}

void loop() {
  delay(2000);
  float h = dht.readHumidity();
  float t = dht.readTemperature();
  float f = dht.readTemperature(true);

  if (isnan(h) || isnan(t) || isnan(f)) {
    Serial.println(F("Failed to read from DHT sensor!"));
    return;
  }

  float hif = dht.computeHeatIndex(f, h);
  float hic = dht.computeHeatIndex(t, h, false);

  unsigned long currentTime = millis();
  unsigned long uptime = (currentTime - startTime) / 1000; // Uptime in seconds
  String timestamp = getTimestamp();

  sendDataToAPI(h, t, f, hic, hif, uptime, timestamp);

  provideVisualFeedback();

  // Rotate tokens if expired
  if (millis() > tokenExpiryTime) {
    if (!refreshToken()) {
      Serial.println("Failed to refresh token");
      return;
    }
  }

  server.handleClient();
}

void connectToWiFi() {
  Serial.print("Connecting to ");
  Serial.println(ssid);
  
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  
  Serial.println("");
  Serial.println("WiFi connected.");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void startWebServer() {
  server.on("/", HTTP_GET, []() {
    if (!server.authenticate(basicAuthUsername, basicAuthPassword)) {
      return server.requestAuthentication();
    }
    
    String message = "<html><body>";
    message += "<h1>Sensor Data</h1>";
    message += "<p>Humidity: " + String(dht.readHumidity()) + "%</p>";
    message += "<p>Temperature (C): " + String(dht.readTemperature()) + "°C</p>";
    message += "<p>Temperature (F): " + String(dht.readTemperature(true)) + "°F</p>";
    message += "<p>Heat Index (C): " + String(dht.computeHeatIndex(dht.readTemperature(), dht.readHumidity(), false)) + "°C</p>";
    message += "<p>Heat Index (F): " + String(dht.computeHeatIndex(dht.readTemperature(true), dht.readHumidity())) + "°F</p>";
    message += "<p>Uptime: " + String((millis() - startTime) / 1000) + " seconds</p>";
    message += "</body></html>";
    
    server.send(200, "text/html", message);
  });

  server.on("/config", HTTP_GET, []() {
    if (!server.authenticate(basicAuthUsername, basicAuthPassword)) {
      return server.requestAuthentication();
    }
    
    String message = "<html><body>";
    message += "<h1>Configure WiFi</h1>";
    message += "<form action='/config' method='post'>";
    message += "SSID: <input type='text' name='ssid'><br>";
    message += "Password: <input type='password' name='password'><br>";
    message += "<input type='submit' value='Save'>";
    message += "</form></body></html>";
    
    server.send(200, "text/html", message);
  });

  server.on("/config", HTTP_POST, []() {
    if (!server.authenticate(basicAuthUsername, basicAuthPassword)) {
      return server.requestAuthentication();
    }
    
    if (server.hasArg("ssid") && server.hasArg("password")) {
      String newSSID = server.arg("ssid");
      String newPassword = server.arg("password");
      storeWiFiConfig(newSSID.c_str(), newPassword.c_str());
      server.send(200, "text/html", "<html><body><h1>Configuration Saved!</h1></body></html>");
      delay(1000);
      ESP.restart();
    } else {
      server.send(400, "text/html", "<html><body><h1>Missing SSID or Password!</h1></body></html>");
    }
  });

  server.begin();
}

void sendDataToAPI(float humidity, float tempC, float tempF, float heatIndexC, float heatIndexF, unsigned long uptime, String timestamp) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(apiEndpoint);
    http.addHeader("Content-Type", "application/json");

    // Construct Authorization header
    String authHeader = "Bearer " + jwtToken;
    http.addHeader("Authorization", authHeader.c_str());

    DynamicJsonDocument doc(256);
    doc["sensor_id"] = generateSensorID();
    doc["humidity"] = humidity;
    doc["temperature_c"] = tempC;
    doc["temperature_f"] = tempF;
    doc["heat_index_c"] = heatIndexC;
    doc["heat_index_f"] = heatIndexF;
    doc["uptime"] = uptime;
    doc["timestamp"] = timestamp;

    String payload;
    serializeJson(doc, payload);

    int httpResponseCode = http.POST(payload);

    if (httpResponseCode == 401) { // Unauthorized
      if (refreshToken()) {
        // Refresh token and retry request
        authHeader = "Bearer " + jwtToken;  // Update authHeader with refreshed token
        http.addHeader("Authorization", authHeader.c_str());
        httpResponseCode = http.POST(payload);
      }
    }

    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println(httpResponseCode);
      Serial.println(response);
    } else {
      Serial.print("Error on sending POST: ");
      Serial.println(httpResponseCode);
    }

    http.end();
  }
}




String generateSensorID() {
  return WiFi.macAddress();
}

String getTimestamp() {
  time_t now;
  struct tm timeinfo;
  if (!getLocalTime(&timeinfo)) {
    Serial.println("Failed to obtain time");
    return "";
  }
  char timeStringBuff[50];
  strftime(timeStringBuff, sizeof(timeStringBuff), "%Y-%m-%d %H:%M:%S", &timeinfo);
  return String(timeStringBuff);
}

void provideVisualFeedback() {
  digitalWrite(LED_PIN, HIGH);
  delay(100);
  digitalWrite(LED_PIN, LOW);
  delay(100);
}

// EEPROM functions
void writeStringToEEPROM(int addrOffset, const String &strToWrite) {
  byte len = strToWrite.length();
  EEPROM.write(addrOffset, len);
  for (int i = 0; i < len; i++) {
    EEPROM.write(addrOffset + 1 + i, strToWrite[i]);
  }
  EEPROM.commit();
}

String readStringFromEEPROM(int addrOffset) {
  int newStrLen = EEPROM.read(addrOffset);
  char data[newStrLen + 1];
  for (int i = 0; i < newStrLen; i++) {
    data[i] = EEPROM.read(addrOffset + 1 + i);
  }
  data[newStrLen] = '\0';
  return String(data);
}

void storeWiFiConfig(const char* ssid, const char* password) {
  writeStringToEEPROM(0, String(ssid));
  writeStringToEEPROM(50, String(password));
}

void readWiFiConfig(char* ssid, char* password) {
  String storedSSID = readStringFromEEPROM(0);
  String storedPassword = readStringFromEEPROM(50);
  storedSSID.toCharArray(ssid, storedSSID.length() + 1);
  storedPassword.toCharArray(password, storedPassword.length() + 1);
}


bool obtainTokens() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(tokenEndpoint);
    http.addHeader("Content-Type", "application/json");

    DynamicJsonDocument doc(256);
    doc["username"] = "admin";  // Replace with your actual username
    doc["password"] = "admin";  // Replace with your actual password

    String payload;
    serializeJson(doc, payload);

    int httpResponseCode = http.POST(payload);

    if (httpResponseCode == 200) {
      String response = http.getString();
      DynamicJsonDocument responseDoc(512);
      deserializeJson(responseDoc, response);
      jwtToken = responseDoc["access"].as<String>();
      refreshTokenString = responseDoc["refresh"].as<String>();
      tokenExpiryTime = millis() + 300000; // Set token expiry time to 5 minutes from now
      http.end();
      return true;
    } else {
      Serial.print("Error on obtaining tokens: ");
      Serial.println(httpResponseCode);
    }

    http.end();
  }
  return false;
}


bool refreshToken() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(refreshEndpoint);
    http.addHeader("Content-Type", "application/json");

    // Construct Authorization header
    String authHeader = "Bearer " + jwtToken;
    http.setAuthorization(authHeader.c_str());

    DynamicJsonDocument doc(256);
    doc["refresh"] = refreshTokenString;

    String payload;
    serializeJson(doc, payload);

    int httpResponseCode = http.POST(payload);

    if (httpResponseCode == 200) {
      String response = http.getString();
      DynamicJsonDocument responseDoc(512);
      deserializeJson(responseDoc, response);
      jwtToken = responseDoc["access"].as<String>();
      tokenExpiryTime = millis() + 300000; // Set token expiry time to 5 minutes from now
      http.end();
      return true;
    } else {
      Serial.print("Error on refreshing token: ");
      Serial.println(httpResponseCode);
    }

    http.end();
  }
  return false;
}
