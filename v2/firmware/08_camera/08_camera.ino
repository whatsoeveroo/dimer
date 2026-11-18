// Lesson 8: Camera
// Joins your Wi-Fi and shows what Dimer sees on a web page.
// 1) Type your Wi-Fi name and password below (2.4 GHz Wi-Fi; the XIAO cannot use 5 GHz).
// 2) In the Tools menu set PSRAM to "OPI PSRAM" (the camera needs the extra memory).
// 3) Upload, open the Serial Monitor, and open the address it prints in a browser
//    on a phone or computer on the same Wi-Fi.
// Needs: only the XIAO Sense with its camera board clipped on.
#include "esp_camera.h"
#include <WiFi.h>
#include <WebServer.h>

const char *WIFI_NAME     = "your-wifi-name";
const char *WIFI_PASSWORD = "your-wifi-password";

WebServer server(80);

bool cameraBegin() {
  camera_config_t c = {};
  // These pins are wired inside the XIAO ESP32S3 Sense; you never touch them.
  c.pin_pwdn = -1;  c.pin_reset = -1;  c.pin_xclk = 10;
  c.pin_sccb_sda = 40;  c.pin_sccb_scl = 39;
  c.pin_d7 = 48;  c.pin_d6 = 11;  c.pin_d5 = 12;  c.pin_d4 = 14;
  c.pin_d3 = 16;  c.pin_d2 = 18;  c.pin_d1 = 17;  c.pin_d0 = 15;
  c.pin_vsync = 38;  c.pin_href = 47;  c.pin_pclk = 13;
  c.xclk_freq_hz = 20000000;
  c.ledc_timer = LEDC_TIMER_3;          // keep clear of the timers the motors and servo use
  c.ledc_channel = LEDC_CHANNEL_7;
  c.pixel_format = PIXFORMAT_JPEG;
  c.frame_size = FRAMESIZE_QVGA;        // 320 x 240
  c.jpeg_quality = 12;                  // 10 = better, 30 = smaller
  c.fb_count = 2;
  c.fb_location = CAMERA_FB_IN_PSRAM;
  c.grab_mode = CAMERA_GRAB_LATEST;
  return esp_camera_init(&c) == ESP_OK;
}

void handlePage() {
  server.send(200, "text/html",
    "<html><body style='background:#111;color:#eee;font-family:sans-serif;text-align:center'>"
    "<h2>What Dimer sees</h2><img id='v' style='width:90%;max-width:640px'>"
    "<script>function n(){document.getElementById('v').src='/jpg?'+Date.now()}"
    "document.getElementById('v').onload=()=>setTimeout(n,100);n();</script></body></html>");
}

void handlePicture() {
  camera_fb_t *fb = esp_camera_fb_get();
  if (!fb) { server.send(500, "text/plain", "camera error"); return; }
  server.setContentLength(fb->len);
  server.send(200, "image/jpeg", "");
  server.client().write(fb->buf, fb->len);
  esp_camera_fb_return(fb);
}

void setup() {
  Serial.begin(115200);
  delay(2000);
  if (!psramFound()) Serial.println("No PSRAM: set Tools > PSRAM > OPI PSRAM and upload again.");
  if (!cameraBegin()) {
    Serial.println("Camera did not start. Is the camera board clipped on firmly?");
    while (true) delay(1000);
  }
  Serial.println("Camera OK");

  WiFi.begin(WIFI_NAME, WIFI_PASSWORD);
  Serial.print("Joining Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) { delay(500); Serial.print("."); }
  Serial.println();
  Serial.print("Open this in a browser: http://");
  Serial.println(WiFi.localIP());

  server.on("/", handlePage);
  server.on("/jpg", handlePicture);
  server.begin();
}

void loop() {
  server.handleClient();
}
