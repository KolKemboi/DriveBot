

float left_vel = 0.0f;
float right_vel = 0.0f;

unsigned long last_time = 0;

void setup() {
  Serial.begin(115200);

  while (!Serial) {}

  last_time = millis();
}

void loop() {
  // Read latest command if available
  if (Serial.available()) {
    String line = Serial.readStringUntil('\n');

    int comma = line.indexOf(',');

    if (comma != -1) {
      left_vel = line.substring(0, comma).toFloat();
      right_vel = line.substring(comma + 1).toFloat();
    }
  }

float left_position = 0.0f;
float right_position = 0.0f;
  // Send feedback
  Serial.print(left_position, 3);
  Serial.print(",");
  Serial.print(left_vel, 3);
  Serial.print(",");
  Serial.print(right_position, 3);
  Serial.print(",");
  Serial.println(right_vel, 3);

  delay(20);
}
