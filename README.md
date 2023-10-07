# Reverse Engineering The TX07K-THC RF Temperature Sensor

This repository contains tools for reverse engineering the protocol of the TX07K-THC temperature and humidity sensor operating over 433 MHz RF.

## Protocol

* The packets are sent over 433 MHz.
* It use pulse distance modulation (pulse position modulation) on top of on/off keying (AM).
* All pulses start with a single "on", and the remaining bits are "off".
* A zero is four pulses long and a one is eight pulses long.
* The pulse duration is 600 µs.
* The device sends bursts of six packets, with 8 ms in-between.
* Periodic updates are sent every 35 s.
* The "TX" button can be pushed to manually trigger a send.

The nibble is the fundamental data unit.
A packet is ten nibbles long:

```
  GGIFTTTHHCC

GG  - 8-bit device generation/ID, changes on every restart.
I   - 4-bit checksum, an almost-CRC-4 with polynomial 3.
F   - 4-bit flags:
      3 - Button for manual transmission pressed.
      2 - Battery low (below 2.5 V.)
      1 - Temperature falling.
      0 - Temperature rising.
TTT - 12-bit temperature in deci-Fahrenheit, offset 90 *F.
HH  - 8-bit humidity as %RH, in BCD.
CC  - 8-bit channel (1-3).
```

The checksum uses a modified (or wrongly implemented) CRC-4, see `tempdec.py`.

The temperature rising/falling flags seem meaningless, since the receiver has six states: rising, flat and falling, for both temperature and humidity.
The sensor doesn't seem to be doing anything fancy with the flags, so they are most likely useless.
Perhaps they are used to bootstrap the display's direction indicator when switching channels, but after two samples, it makes sense that the receiver itself infers direction.

### Unknowns

The exact semantics of the temperature direction flags are unclear.
They can react to 0.1*F changes, but not always.
They reset to zero after 25-60 min of no change.

### The Process

I wrote a blog post about this: [Reverse Engineering an RF Sensor Protocol Checksum](https://tommie.github.io/a/2023/10/reverse-engineering-checksum)
