"""A program to decode TX07K-THC signals."""
import struct
import sys

def decode_signal_line(line: str):
    return {s[0]: s[1:] for s in line.split()}

def decode_pdm(s: str, short=4, long=8, fudge=1):
    # The left-most zeros can't belong to this message, so just strip
    # them. The symbol is a stop symbol.
    s = s.rstrip('0')

    ss = ''
    while s != '1':
        i = s.index('1', 1)
        if i > long + fudge: ss += 'x'
        elif i >= long - fudge: ss += '1'
        elif i > short + fudge: ss += 'x'
        elif i >= short - fudge: ss += '0'
        else: ss += 'x'
        s = s[i:]

    return ss

def to_nibbles(v: int, n: int):
    return [int(c, 16) for c in ('{:0' + str(n) + 'x}').format(v)]

def almost_crc4(bs, poly=3, init=0):
    rem = init

    for b in bs:
        # This is backwards: in normal CRC-4, the XOR b happens first.
        for i in range(0, 4):
            if rem & 0x08:
                rem = (rem << 1) ^ poly
            else:
                rem <<= 1
        rem ^= b

    return rem & 0x0F

def decode_bcd(v: int):
    return int('{:x}'.format(v))

def one(s: str):
    sig = decode_signal_line(s)
    ss = decode_pdm(sig['d'])

    if 'x' in ss or len(ss) != 5*8:
        #print('enc', s, file=sys.stderr)
        return

    v = int(ss, 2)
    gen  =  v >> 32  # Generation, changes on every start-up.
    chk  = (v >> 28) & 0x0F
    flag = (v >> 24) & 0x0F
    temp = (v >> 12) & 0x0FFF
    hum  = (v >> 4)  & 0xFF
    chan =  v        & 0x0F

    nib = to_nibbles(v, 10)

    # The channel takes the place of the checksum.
    chkc = almost_crc4(nib[:2] + nib[-1:] + nib[3:-1], poly=3)

    if chk != chkc:
        print('chk', hex(chkc), hex(v), file=sys.stderr)
        return

    try:
        hum = decode_bcd(hum)
    except ValueError as ex:
        print('bcd', ss, ex, file=sys.stderr)
        return

    tempf = 0.1*temp - 90
    button = flag & 0x08 != 0
    battlow = flag & 0x04 != 0
    temp_falling = flag & 0x02 != 0
    temp_rising = flag & 0x01 != 0

    flagstr = (
        ('T' if button else '-') +
        ('b' if battlow else '-') +
        ('f' if temp_falling else '-') +
        ('r' if temp_rising else '-')
    )
    print('temp chan={}/{:x} flag={:x}/{} temp={:.1f}*F rh={}%'.format(chan, gen, flag, flagstr, tempf, hum))

if len(sys.argv) == 1:
    for s in sys.stdin:
        s = s.strip()
        if not s: continue
        one(s)
else:
    import serial

    with serial.Serial(sys.argv[1], 115200) as f:
        while True:
            one(f.readline().decode('ascii'))
