float left_position = 1.25;
  float left_velocity = 0.42;
  float right_position = 1.24;
  float right_velocity = 0.41;

void setup() {
  Serial.begin(115200);
// Example values (replace with your encoder readings)
  
  // Wait for the serial port (useful on boards with native USB)
  while (!Serial) {
  }
}

void loop() {
  
if (Serial.available())
{
    String line = Serial.readStringUntil('\n');

    float left;
    float right;

    if (sscanf(line.c_str(), "%f,%f",
               &left, &right) == 2)
    {
        // Drive motors
    }
}
  Serial.print(left_position);
Serial.print(",");

Serial.print(left_velocity);
Serial.print(",");

Serial.print(right_position);
Serial.print(",");

Serial.println(right_velocity);

  delay(20);   // 50 Hz
  left_position += 1;
  left_velocity += 1;
  right_position += 1;
  right_velocity += 1;
}
