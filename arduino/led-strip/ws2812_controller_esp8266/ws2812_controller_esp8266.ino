  
/*
* This example works for ESP8266 and uses the NeoPixelBus library instead of the one bundle
* Sketch contributed to by Joey Babcock - https://joeybabcock.me/blog/
* Codebase created by ScottLawsonBC - https://github.com/scottlawsonbc
*/

#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <WiFiUdp.h>
#include <NeoPixelBus.h>
#include <ArduinoJson.h>

// Set to the number of LEDs in your LED strip
#define NUM_LEDS 90
// Maximum number of packets to hold in the buffer. Don't change this.
#define BUFFER_LEN 1024
// Toggles FPS output (1 = print FPS over serial, 0 = disable output)
#define PRINT_FPS 0

typedef enum {
    SERVER_MESSAGE_ID_CONNECT = 1,
    SERVER_MESSAGE_ID_LED_STRIP_UPDATE = 2
} ServerMessageId;

typedef enum {
    CLIENT_MESSAGE_ID_CONNECT = 1
} ClientMessageId;

//NeoPixelBus settings
const uint8_t PixelPin = 3;  // make sure to set this to the correct pin, ignored for Esp8266(set to 3 by default for DMA)

// Wifi and socket settings17
const char* ssid     = "YOUR SSID";
const char* password = "YOUR PASSWORD";
const uint8_t clientType = 1;  // 1: LED_STRIP_CLIENT, 2: CONTROLLER_CLIENT
const char* clientName = "YOUR_CLIENT_NAME";
unsigned int localPort = 7777;
unsigned int serverPort = 8888;
char packetBuffer[BUFFER_LEN];

// LED strip
NeoPixelBus<NeoGrbFeature, Neo800KbpsMethod> ledstrip(NUM_LEDS, PixelPin);
float sigma = 0.9f;
String color = "#ff00";

WiFiUDP port;
WiFiUDP broadcastUdp;

bool isConnectedToServer = false;

// Network information
IPAddress ip(192, 168, 178, 41);
IPAddress broadcast(192, 168, 178, 255);
// Set gateway to your router's gateway
IPAddress gateway(192, 168, 178, 1);
IPAddress subnet(255, 255, 255, 0);

void setup() {
    Serial.begin(115200);
    
    WiFi.config(ip, gateway, subnet);
    WiFi.begin(ssid, password);
    Serial.println("");
    // Connect to wifi and print the IP address over serial
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("");
    Serial.print("Connected to ");
    Serial.println(ssid);
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
    port.begin(localPort);
    broadcastUdp.begin(serverPort);
    ledstrip.Begin();//Begin output
    ledstrip.Show();//Clear the strip for use
}

uint8_t N = 0;
#if PRINT_FPS
    uint16_t fpsCounter = 0;
    uint32_t secondTimer = 0;
#endif

void broadcastMessage(uint8_t messageId, char* messageBuffer, int len) {
  Serial.print("broadcastUDP: ");
  Serial.println(messageId);

  broadcastUdp.beginPacketMulticast(broadcast, serverPort, WiFi.localIP());
  broadcastUdp.write(messageId);
  broadcastUdp.write(messageBuffer, len);
  broadcastUdp.endPacket();
}

String ipAddress2String(const IPAddress& ipAddress)
{
  return String(ipAddress[0]) + String(".") +\
  String(ipAddress[1]) + String(".") +\
  String(ipAddress[2]) + String(".") +\
  String(ipAddress[3])  ;
}

void handleMessage(int messageId, int len, char *buffer){
    Serial.printf("\nReceived message with Id: %d\n", messageId);
    switch(messageId){
        case SERVER_MESSAGE_ID_CONNECT:
            onConnectionMessage(buffer);
            break;
        case SERVER_MESSAGE_ID_LED_STRIP_UPDATE:
            onLedStripUpdateMessage(len, buffer);
            break;
        default:
            Serial.printf("\nCan't handle message with id: %d\n", messageId);
    }
}

void onLedStripUpdateMessage(int len, char *buffer){
    for(int i=0; i<len; i+=4) {
        buffer[len]=0;
        N = buffer[i];
        RgbColor pixel((uint8_t)buffer[i+1], (uint8_t)buffer[i+2], (uint8_t)buffer[i+3]);
        ledstrip.SetPixelColor(N, pixel);
    } 
    ledstrip.Show();
}

void onConnectionMessage(char *buffer){
    isConnectedToServer = true;
    // TODO get and print server IP address
    char serverIp[] = "Not yet set";
    Serial.printf("\nRegistered at server: %s\n", serverIp);
}

void loop() {
    if(!isConnectedToServer){
        delay(1000);
        // TODO send complete client config not just ip
        // convert string to char array
        char msg[1024];
        DynamicJsonDocument configJson(1024);
        configJson["typeId"] = clientType;
        configJson["name"] = clientName;
        configJson["num_pixels"]   = NUM_LEDS;
        configJson["ip"] = ipAddress2String(WiFi.localIP());
        serializeJson(configJson, msg);
        broadcastMessage(CLIENT_MESSAGE_ID_CONNECT, msg, 1024);
    }

    // Read data over socket
    int packetSize = port.parsePacket();
    // If packets have been received, interpret the command
    if (packetSize) {
        int len = port.read(packetBuffer, BUFFER_LEN);
        Serial.printf("Received message with len %d: %s", len, packetBuffer);
        // read 4 bytes as messageId integer
        int messageId = packetBuffer[0];
        handleMessage(messageId, len-1, &packetBuffer[1]);
        #if PRINT_FPS
            fpsCounter++;
            Serial.print("/");//Monitors connection(shows jumps/jitters in packets)
        #endif
    }
    #if PRINT_FPS
        if (millis() - secondTimer >= 1000U) {
            secondTimer = millis();
            Serial.printf("FPS: %d\n", fpsCounter);
            fpsCounter = 0;
        }   
    #endif
    // TODO set isConnectedToServer=false with connection timeout
}
