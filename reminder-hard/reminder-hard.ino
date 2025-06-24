#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <NTPClient.h>
#include <WiFiUdp.h>
#include <ArduinoJson.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include "pitches.h";

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
#define MAX_REMINDERS 10
#define SPEAKER_PIN D5

const char* ssid = "Igorko_1976";
const char* password = "Svatoslav1117";
const char* serverIP = "192.168.0.107";
const int serverPort = 8000;

#define SERIAL_NUMBER "serial123"
#define SECRET_KEY "secret321"

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);
WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "pool.ntp.org", 0, 60000);

struct Reminder {
  time_t timestamp;
  int id;
  String message;
};

Reminder reminders[MAX_REMINDERS];
int reminderCount = 0;

unsigned long lastUpdate = 0;
const unsigned long updateInterval = 10000;
uint8_t line = 0;

int message[] = {
  NOTE_E4, NOTE_E4, NOTE_F4, NOTE_G4,
  NOTE_G4, NOTE_F4, NOTE_E4, NOTE_D4,
  NOTE_C4, NOTE_C4, NOTE_D4, NOTE_E4,
  NOTE_E4, NOTE_D4, NOTE_D4,

  NOTE_E4, NOTE_E4, NOTE_F4, NOTE_G4,
  NOTE_G4, NOTE_F4, NOTE_E4, NOTE_D4,
  NOTE_C4, NOTE_C4, NOTE_D4, NOTE_E4,
  NOTE_D4, NOTE_C4, NOTE_C4
};

int noteDurations[] = {
  4, 4, 4, 4,
  4, 4, 4, 4,
  4, 4, 4, 4,
  4, 4, 2,

  4, 4, 4, 4,
  4, 4, 4, 4,
  4, 4, 4, 4,
  4, 4, 2
};

void setup() {
  Wire.begin(D2, D1);
  display.begin(SSD1306_SWITCHCAPVCC, 0x3C);
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(WHITE);
  line = 0;

  displayDebug("Booting...");
  WiFi.begin(ssid, password);
  displayDebug("WiFi connecting...");

  int tries = 0;
  while (WiFi.status() != WL_CONNECTED && tries++ < 20) {
    delay(500);
    displayDebug(".");
  }

  if (WiFi.status() != WL_CONNECTED) {
    displayDebug("WiFi Failed");
    while (true);
  }

  displayDebug("WiFi OK");
  timeClient.begin();
  displayDebug("NTP started");
}

void loop() {
  timeClient.update();
  time_t now = timeClient.getEpochTime();

  if (millis() - lastUpdate > updateInterval) {
    lastUpdate = millis();
    fetchAndDisplayReminders();
  }

  for (int i = 0; i < reminderCount; i++) {
    if (reminders[i].timestamp != 0) {
      long diff = now - reminders[i].timestamp;
      if (abs(diff) <= 5) {
        display.clearDisplay();
        display.setCursor(0, 0);
        display.println("REMINDER TRIGGERED!");
        display.display();
        triggerReminder(reminders[i].message);
        reminders[i].timestamp = 0;
      }
    }
  }
}

void displayDebug(const String& msg) {
  display.setCursor(0, line * 10);
  display.println(msg);
  display.display();
  line++;
  if (line > 5) {
    delay(2000);
    display.clearDisplay();
    line = 0;
  }
}

void fetchAndDisplayReminders() {
  if (WiFi.status() != WL_CONNECTED) {
    displayDebug("WiFi Lost");
    return;
  }

  WiFiClient client;
  HTTPClient http;
  String url = "http://" + String(serverIP) + ":" + String(serverPort) + "/api/reminders/as-device";

  http.begin(client, url);
  http.addHeader("X-DEVICE-TOKEN", String(SERIAL_NUMBER) + ":" + String(SECRET_KEY));
  http.addHeader("Accept", "application/json");

  int httpCode = http.GET();
  if (httpCode != 200) {
    displayDebug("HTTP ERR: " + String(httpCode));
    http.end();
    return;
  }

  String payload = http.getString();
  http.end();

  StaticJsonDocument<2048> doc;
  DeserializationError error = deserializeJson(doc, payload);
  if (error) {
    displayDebug("JSON error");
    return;
  }

  time_t now = timeClient.getEpochTime();
  reminderCount = 0;

  for (JsonObject reminder : doc.as<JsonArray>()) {
  if (reminderCount >= MAX_REMINDERS) break;

  const char* timeStr = reminder["time_"];
  const char* dateStr = reminder["date_"];
  int id = reminder["id"];

  String msg = reminder["message"].as<String>();
  if (msg == "") msg = "Reminder!";

  int h, m, s;
  sscanf(timeStr, "%d:%d:%d", &h, &m, &s);
  int year, month, day;
  sscanf(dateStr, "%d-%d-%d", &year, &month, &day);

  struct tm t = {0};
  t.tm_year = year - 1900;
  t.tm_mon = month - 1;
  t.tm_mday = day;
  t.tm_hour = h;
  t.tm_min = m;
  t.tm_sec = s;

  time_t reminderTime = mktime(&t) - 3 * 3600;
  reminders[reminderCount++] = { reminderTime, id, msg };
}


  display.clearDisplay();
  display.setTextSize(1);
  line = 0;

  struct tm* nowStruct = localtime(&now);
  char timeBuf[20];
  strftime(timeBuf, sizeof(timeBuf), "Time: %H:%M:%S", nowStruct);
  displayDebug(timeBuf);

  for (int i = 0; i < min(reminderCount, 3); i++) {
    struct tm* reminderStruct = localtime(&reminders[i].timestamp);
    char buf[32];
    strftime(buf, sizeof(buf), "Reminder: %Y-%m-%d %H:%M:%S", reminderStruct);
    displayDebug(buf);
  }

  display.display();
}

void triggerReminder(const String& message) {
  display.clearDisplay();
  display.setTextSize(1);
  line = 0;
  display.setCursor(0, 0);
  display.println("🔔 REMINDER ACTIVE 🔔");
  display.display();

  for (int r = 0; r < 3; r++) {
    playMessage();
    drawAnimation(message);
  }

  display.clearDisplay();
  display.display();
}

void playMessage() {
  int len = sizeof(message) / sizeof(int);
  for (int i = 0; i < len; i++) {
    int duration = 1000 / noteDurations[i];
    tone(SPEAKER_PIN, message[i], duration);
    delay(duration * 1.3);
    noTone(SPEAKER_PIN);
  }
}

void drawAnimation(const String& message) {
  const char* text = message.c_str();
  const int len = strlen(text);
  const int baseY = 30;
  const int amplitude = 6;
  const int steps = 20;

  display.setTextSize(2);
  display.setTextColor(WHITE);

  for (int frame = 0; frame < steps; frame++) {
    display.clearDisplay();

    for (int i = 0; i < len; i++) {
      float phase = (frame + i) * 0.4;
      int y = baseY + sin(phase) * amplitude;
      int x = 10 + i * 12;
      display.setCursor(x, y);
      display.print(text[i]);
    }

    display.display();
    delay(70);
  }
}
