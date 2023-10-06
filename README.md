# Reverse Engineering The TX07K-THC RF Temperature Sensor

This repository contains tools for reverse engineering the protocol of the TX07K-THC temperature and humidity sensor operating over 433 MHz RF.

## Protocol

The signals are sent over 433 MHz using pulse distance modulation, with the nibble as the fundamental data unit.

All pulses start with a single "on", and the remaining bits are "off".
A zero is four pulses long and a one is eight pulses long.

The packet is ten nibbles long:

```
  GGIFTTTHHCC

GG  - 8-bit device generation/ID, changes on every restart.
I   - 4-bit checksum, an almost-CRC-4 with polynomial 3.
F   - 4-bit flags:
      0 - Unknown.
      1 - Unknown.
      2 - Battery low (below 2.5 V.)
      3 - Button for manual transmission pressed.
TTT - 12-bit temperature in deci-Fahrenheit, offset 90 *F.
HH  - 8-bit humidity as %RH, in BCD.
CC  - 8-bit channel (1-3).
```

The device sends bursts of six packets, with 8 ms in-between.

The checksum uses a modified (or wrongly implemented) CRC-4, see `tempdec.py`.

### Unknowns

The flag nibble is mostly unknown.
Bits 0 and 1 are being set, but their meaning are unknown.

### The Process

I wrote a blog post about this: [Reverse Engineering an RF Sensor Protocol Checksum](https://tommie.github.io/a/2023/10/reverse-engineering-checksum)
