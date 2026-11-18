// Lesson 9: Dimer's brain - the real robot program.
//
// Dimer is always in one "state" (a mode). Each state knows what to do and when to move on:
//
//   IDLE    sits still, looks around, blinks. After a while -> WANDER (or SLEEP if bored)
//   WANDER  drives forward on a gentle curve for a few seconds -> IDLE
//   EDGE    an edge sensor saw no table: stop, back up, turn away -> IDLE
//   LIFTED  both sensors see no table for a moment = someone picked it up: tracks stop -> IDLE when put down
//   NOTICE  heard a clap: looks up at you, chirps -> IDLE
//   SLEEP   nothing happened for 2 minutes: eyes half shut, head down. A clap wakes it.
//
// The loop() below runs about 100 times a second. Every time it:
//   1) reads the edge sensors (safety first),
//   2) does a small step of the current state,
//   3) updates the face and the head.
// Nothing in the loop waits long (no long delay()), so the edge sensors are always being watched.
//
// All the numbers you tuned in lessons 2-7 are in the dimer_settings.h tab.

#include "dimer_settings.h"
#include "expander.h"
#include "motors.h"
#include "tilt.h"
#include "face.h"
#include "sound.h"
#include "mic.h"

enum State { IDLE, WANDER, EDGE_BACK, EDGE_TURN, LIFTED, NOTICE, SLEEP, BROKEN };
const char *stateNames[] = { "IDLE", "WANDER", "EDGE_BACK", "EDGE_TURN", "LIFTED", "NOTICE", "SLEEP", "BROKEN" };

State state = IDLE;
unsigned long stateStartMs = 0;    // when we entered the state
unsigned long stateLengthMs = 0;   // how long we plan to stay
unsigned long lastFunMs = 0;       // last time something happened (for falling asleep)
unsigned long bothEdgesSinceMs = 0, onTableSinceMs = 0, quietSinceMs = 0, nextGlanceMs = 0;
int turnDirection = 1;             // 1 = turn right, -1 = turn left
int wanderLeft = 0, wanderRight = 0;
bool micOk = false;

const unsigned long BORED_AFTER_MS = 120000;   // 2 minutes

void goTo(State s, unsigned long lengthMs) {
  state = s;
  stateStartMs = millis();
  stateLengthMs = lengthMs;
  Serial.print("-> ");
  Serial.println(stateNames[s]);
}

bool stateTimeUp() { return millis() - stateStartMs >= stateLengthMs; }

// ---------- entering each state ----------

void startIdle() {
  stopMotors();
  faceMood(MOOD_NORMAL);
  faceLook(0, 0);
  tiltTo(0);
  goTo(IDLE, random(1500, 5000));
}

void startWander() {
  int curve = random(-30, 31);                  // a little left or right
  wanderLeft = DRIVE_SPEED + curve;
  wanderRight = DRIVE_SPEED - curve;
  faceMood(MOOD_NORMAL);
  faceLook(curve / 40.0, 0.2);                  // look where we are heading
  drive(wanderLeft, wanderRight);
  goTo(WANDER, random(2000, 6000));
}

void startEdge(bool left, bool right) {
  stopMotors();
  say(SND_SCARED);
  faceMood(MOOD_SCARED);
  faceLook(0, 1);                               // look down at the edge
  if (left && !right) turnDirection = 1;        // edge on the left -> turn right
  else if (right && !left) turnDirection = -1;
  else turnDirection = random(2) ? 1 : -1;
  lastFunMs = millis();
  goTo(EDGE_BACK, 450);
}

void startLifted() {
  stopMotors();
  say(SND_WHEE);
  faceMood(MOOD_SURPRISED);
  faceLook(0, -1);
  tiltTo(TILT_MAX_DEG, 90);
  lastFunMs = millis();
  goTo(LIFTED, 0);
}

void startNotice() {
  stopMotors();
  say(SND_QUESTION);
  faceMood(MOOD_SURPRISED);
  faceLook(0, -1);                              // look up at you
  tiltTo(TILT_MAX_DEG, 80);
  lastFunMs = millis();
  goTo(NOTICE, 2500);
}

void startSleep() {
  stopMotors();
  say(SND_SLEEPY);
  faceMood(MOOD_SLEEPY);
  faceLook(0, 0.5);
  tiltTo(0, 15);
  goTo(SLEEP, 0);
}

// ---------- setup and loop ----------

void setup() {
  Serial.begin(115200);
  randomSeed(esp_random());

  faceBegin();
  faceMood(MOOD_SLEEPY);
  faceUpdate();
  micOk = micBegin();           // the microphone first: it needs I2S unit 0
  soundBegin();
  tiltBegin();

  if (!expanderBegin()) {       // without the expander we cannot see edges, so never drive
    Serial.println("Expander not found. Dimer will not drive. Check the HEAD wires and the switch.");
    faceMood(MOOD_DIZZY);
    say(SND_SCARED);
    goTo(BROKEN, 0);
    return;
  }
  motorsBegin();

  say(SND_HELLO);
  faceMood(MOOD_HAPPY);
  tiltTo(15, 40);               // a little nod hello
  lastFunMs = millis();
  goTo(NOTICE, 1500);
}

void loop() {
  unsigned long now = millis();

  if (state == BROKEN) { faceUpdate(); tiltUpdate(); delay(10); return; }

  // 1) Safety: the edge sensors.
  bool edgeL = edgeLeftNoTable();
  bool edgeR = edgeRightNoTable();

  if (edgeL && edgeR) {
    if (bothEdgesSinceMs == 0) bothEdgesSinceMs = now;
    if (now - bothEdgesSinceMs > 300 && state != LIFTED) startLifted();
  } else {
    bothEdgesSinceMs = 0;
  }

  if (state == WANDER && (edgeL || edgeR)) startEdge(edgeL, edgeR);

  // 2) Listening for a clap. We listen all the time (so old sounds do not pile up),
  //    but only react while the tracks have been still for a moment and Dimer is quiet.
  int loudness = micOk ? micLoudness() : 0;
  if (soundPlaying) quietSinceMs = now;
  bool still = (state == IDLE || state == SLEEP) && now - stateStartMs > 400;
  if (still && now - quietSinceMs > 300) {
    if (loudness > CLAP_LEVEL) {
      if (state == SLEEP) { faceMood(MOOD_HAPPY); say(SND_HAPPY); }
      startNotice();
    }
  }

  // 3) A small step of the current state.
  switch (state) {
    case IDLE:
      if (now > nextGlanceMs) {                       // glance around now and then
        faceLook(random(-10, 11) / 10.0, random(-5, 6) / 10.0);
        if (random(5) == 0) tiltTo(random(0, 15), 30);
        nextGlanceMs = now + random(800, 2500);
      }
      if (now - lastFunMs > BORED_AFTER_MS) startSleep();
      else if (stateTimeUp()) {
        if (random(10) < 7) startWander();
        else { say(random(2) ? SND_BEEP : SND_QUESTION); startIdle(); }
      }
      break;

    case WANDER:
      if (stateTimeUp()) startIdle();
      break;

    case EDGE_BACK:
      if (now - stateStartMs > 150) drive(-DRIVE_SPEED, -DRIVE_SPEED);   // a moment's pause, then back up
      if (stateTimeUp()) {
        drive(turnDirection * TURN_SPEED, -turnDirection * TURN_SPEED);
        faceLook(turnDirection, 0);
        goTo(EDGE_TURN, random(400, 900));
      }
      break;

    case EDGE_TURN:
      if (stateTimeUp()) startIdle();
      break;

    case LIFTED:
      if (!edgeL && !edgeR) {                          // back on the table?
        if (onTableSinceMs == 0) onTableSinceMs = now;
        if (now - onTableSinceMs > 1000) {
          onTableSinceMs = 0;
          say(SND_HAPPY);
          faceMood(MOOD_HAPPY);
          goTo(NOTICE, 1500);
        }
      } else {
        onTableSinceMs = 0;
      }
      break;

    case NOTICE:
      if (now - stateStartMs > 1200) faceMood(MOOD_HAPPY);
      if (stateTimeUp()) startIdle();
      break;

    case SLEEP:
    case BROKEN:
      break;
  }

  // 4) Face and head.
  faceUpdate();
  tiltUpdate();
  delay(5);
}
