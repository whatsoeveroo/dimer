// Lesson 1: Blink
// Your first program. It blinks the small orange light on the XIAO
// and prints a line to the Serial Monitor once a second.
// Needs: only the XIAO and a USB-C cable. Nothing else plugged in.

// setup() runs once, right after the board powers on or you upload.
void setup() {
  Serial.begin(115200);          // open the "text pipe" back to your Mac
  pinMode(LED_BUILTIN, OUTPUT);  // the little light is an output
}

int count = 0;  // a number we remember between loops

// loop() runs again and again, forever, as fast as it can.
void loop() {
  digitalWrite(LED_BUILTIN, LOW);   // on the XIAO, LOW turns the light ON
  delay(500);                       // wait 500 milliseconds (half a second)
  digitalWrite(LED_BUILTIN, HIGH);  // HIGH turns it OFF
  delay(500);

  count = count + 1;
  Serial.print("Hello from Dimer! Blink number ");
  Serial.println(count);
}
