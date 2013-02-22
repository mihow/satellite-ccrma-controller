#include <Bounce.h>

String inputString = "";         // a string to hold incoming data
boolean stringComplete = false;  // whether the string is complete
String lastResponse = "";

int LEDArray[] = {
  0, 1, 2, 3, 4};

int buttonArray[] = {
  20, 21};

Bounce button0 = Bounce(20, 20);
Bounce button1 = Bounce(21, 20);  // 10 = 10 ms debounce time

const int statusLED = LEDArray[4];
int timer = 30;
int count = 0;

#define numLEDs 5
#define numPatterns 7

int LEDpatterns[numPatterns][numLEDs] = {
  {1, 0, 0, 0, 0},
  {1, 1, 0, 0, 0},
  {1, 1, 1, 0, 0},
  {1, 1, 1, 1, 0},
  {1, 1, 1, 1, 1},
  {1, 0, 1, 0, 1},
  {0, 1, 0, 1, 0}
};

int currentPattern = 0;

void setup() {
  Serial.begin(4800); // USB is always 12 Mbit/sec
  inputString.reserve(200);

  pinMode(buttonArray[0], INPUT_PULLUP);
  pinMode(buttonArray[1], INPUT_PULLUP);

  for (count=0;count<6;count++) {
    pinMode(LEDArray[count], OUTPUT);
  }

  sequenceLEDs();
  //digitalWrite(statusLED, HIGH);
    
  sequencePatterns();
  advancePattern();
}

void loop() {
  // Update all the buttons.  There should not be any long
  // delays in loop(), so this runs repetitively at a rate
  // faster than the buttons could be pressed and released.
  button0.update();
  button1.update();

  showPattern(currentPattern);
  // Serial.println(currentPattern);

  if (serialEvent()) {
    handleInput(inputString);
    inputString = "";
  }

  if (button0.fallingEdge() && button1.fallingEdge()) {
    Serial.println("BUTTON 1 and BUTTON 2");
    sequenceLEDs();
  } else {

  if (button0.fallingEdge()) {
    Serial.println("STATE 1");
    advancePattern();
  }

  if (button1.fallingEdge()) {
    Serial.println("BUTTON 2");
    Serial.print("STATE ");
    Serial.print(currentPattern);
    Serial.print("\n");
    blinkAllLEDs();
    showPattern(currentPattern);
  }
}

  delay(50);
}

bool serialEvent() {
  unsigned char bytecount = 0;
  while (Serial.available() && bytecount < 10) {

    bytecount++;

    char inChar = (char)Serial.read();

    if (inChar == '\n') {
      return true;
    } 
    else {
      inputString += inChar;
      blinkLED(statusLED);
      return false;
    }
  }
}

void handleInput(String input) {
  Serial.println(input);
  lastResponse = input;
  
  if ( input.startsWith("!") ) {
    // Command
    
  } else if ( input.startsWith("?") ) {
    // Query
  }
  
  if ( input=="LED1" ) {
    toggleLED(LEDArray[0]);
  }
  if ( input=="LED2" ) {
    toggleLED(LEDArray[1]);
  }
}

void sequenceLEDs() {
  // lights going up
  for (int count=0;count<numLEDs;count++) {
    digitalWrite(LEDArray[count], HIGH);
    delay(timer);
    digitalWrite(LEDArray[count], LOW);
    delay(timer);
  }
}

void blinkAllLEDs() {
  int timesToBlink = 3;
  
  for (int i=0;i<=timesToBlink;i++) {
    for (int count=0;count<numLEDs;count++) {
      digitalWrite(LEDArray[count], HIGH);
    }
    delay(timer*3);
    for (int count=0;count<numLEDs;count++) {
      digitalWrite(LEDArray[count], LOW);
    }
    delay(timer*3);
  }
  
}

void showPattern(int pattern) {
  for (int count=0;count<5;count++) {
    digitalWrite(LEDArray[count], LEDpatterns[pattern][count]);
  }
  currentPattern = pattern;
}

void advancePattern() {
   if (currentPattern+1 < numPatterns) {
     currentPattern++;
   } else {
     currentPattern = 0;
   }
   showPattern(currentPattern);
}

void sequencePatterns() {
  for (int count=0;count<numPatterns;count++) {
    delay(timer);
    showPattern(count);
  }
}

void blinkLED(int LED) {
  toggleLED(LED);
  delay(timer);
  toggleLED(LED);
}

void toggleLED(int LED) {
  if (digitalRead(LED) == LOW) {
    digitalWrite(LED, HIGH);
  } else {
    digitalWrite(LED, LOW);
  }
}

void LEDOn(int pin) {
  digitalWrite(pin, HIGH);
}

void LEDOff(int pin) {
  digitalWrite(pin, LOW);
}
