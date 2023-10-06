// A pulse signal interpreter for RF receivers.
//
// It measures the length of an on-pulse and outputs a run of bits
// being samples at the pulse interval. If the gap is too large, the
// run is flushed and the on-pulse detection starts over.
//
// The output format is lines of tagged, tab-separated, values:
//
//   d<bits> \t i<idletime> \t t<bittime> \t r<residual> \n
//
// Example:
//
//   d110100110110 i7824 t579 r27
//
// The above example shows a PWM OOK modulation where a zero is 0b100
// and a one is 0b110, so the demodulated signal was 0b1011. There
// were 7824 µs between the last signal and this one. The first '1'
// pulse was 579 µs long. The residual 27 µs is much lower than the
// 579 µs, suggesting bits are properly aligned to the time base.
//
// Unless your receiver handles FM, this only supports OOK. E.g. the
// SRX882 receiver module is AM-only. FM signals show up as bursts of
// noise.

/* --- Types --- */
enum RxMode {
  RX_IDLE = 0,
  RX_HIGH,
  RX_LOW,
};

struct Rx {
  RxMode mode;
  unsigned long buf[256];
  size_t len;
  bool time_wrapped;

  unsigned long prevt;
};

/* --- Data --- */
const uint8_t RX_PIN = 0;
const unsigned long MIN_TIME_BASE = 100;  // µs
const unsigned long MAX_GAP = 5000;  // µs

static Rx rx;

void setup()
{
  Serial.begin(115200);
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(RX_PIN, INPUT);
}

void rx_output(Rx *rx)
{
  if (rx->len < 3)
    return;

  // If initial gap was too small, we probably caught
  // the middle of a packet or noise.
  if (rx->buf[0] < MAX_GAP)
    return;

  unsigned long base = -1;

  // Get the time base (minimum duration).
  for (size_t i = 1; i != rx->len; ++i) {
    base = min(base, rx->buf[i]);
  }

  unsigned long base_limit = base + base / 2;

  // Check if preamble is longer than the time base.
  // We assume the first bit is a start bit that should
  // be short. If not, this is probably not a good packet.
  if (rx->buf[1] > base_limit)
    return;

  unsigned long base_max = base;

  // Get the maximum of the single-period times.
  for (size_t i = 1; i != rx->len; ++i) {
    if (rx->buf[i] >= base_limit)
      continue;

    base_max = max(base_max, rx->buf[i]);
  }

  unsigned int nbits = 0;
  unsigned long rsum = 0;

  // Data bits.
  Serial.print('d');
  for (size_t i = 1; i != rx->len; ++i) {
    unsigned long t;

    for (t = base_max / 2; t < rx->buf[i]; t += base_max, ++nbits)
      Serial.print(i % 2 == 0 ? '0' : '1');

    unsigned long v = abs((long) rx->buf[i] - (long) (t - base_max / 2));
    if (v > base_max)
      v -= base_max;
    rsum += v;
  }
  Serial.print('\t');

  // Line idle time before first bit.
  Serial.print('i');
  Serial.print(rx->buf[0]);
  Serial.print('\t');

  // Bit time base in microseconds.
  Serial.print('t');
  Serial.print((base + base_max) / 2);
  Serial.print('\t');

  // Residual. Measure of timing quality. It is the average of the
  // difference between base_max and individual bit times in microseconds.
  Serial.print('r');
  Serial.print((rsum + nbits / 2) / nbits);
  Serial.println();
}

void rx_work(Rx *rx)
{
  uint8_t rv = digitalRead(RX_PIN);
  unsigned long now = micros();
  unsigned long dt = now - rx->prevt;

  rx->time_wrapped = rx->time_wrapped || now < rx->prevt;
  if (rx->time_wrapped) {
    dt = -1;
  }

  if (rx->mode == RX_IDLE && rv) {
    rx->len = 0;
    rx->buf[rx->len++] = dt;
    rx->prevt = now;
    rx->time_wrapped = false;
    rx->mode = RX_HIGH;
  } else if (rx->mode == RX_HIGH && !rv) {
    if (dt < MIN_TIME_BASE) {
      rx->mode = RX_IDLE;
      return;
    }

    digitalWrite(LED_BUILTIN, HIGH);
    rx->buf[rx->len++] = dt;
    rx->prevt = now;
    rx->time_wrapped = false;
    rx->mode = RX_LOW;
  } else if (rx->mode == RX_LOW && rv) {
    if (dt < MIN_TIME_BASE) {
      digitalWrite(LED_BUILTIN, LOW);
      rx->mode = RX_IDLE;
      return;
    }

    rx->buf[rx->len++] = dt;
    rx->prevt = now;
    rx->time_wrapped = false;
    rx->mode = RX_HIGH;
  } else if (rx->mode == RX_LOW && dt > MAX_GAP) {
    rx_output(rx);
    digitalWrite(LED_BUILTIN, LOW);
    rx->mode = RX_IDLE;
  }

  if (rx->len == sizeof(rx->buf) / sizeof(*rx->buf)) {
    digitalWrite(LED_BUILTIN, LOW);
    rx->mode = RX_IDLE;
  }
}

void loop()
{
  rx_work(&rx);
}
