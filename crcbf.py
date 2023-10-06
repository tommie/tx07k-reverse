"""A program to brute-force CRC-4."""

import sys

def crc4(poly, bs, init=0):
    rem = init

    for b in bs:
        for i in range(0, 4):
            if rem & 0x08:
                rem = (rem << 1) ^ poly
            else:
                rem <<= 1
        rem ^= b
    return rem & 0x0F

def parse_sample(s):
    vs = [int(c, 16) for c in s]
    chk = vs[2]
    vs = vs[:2] + vs[-1:] + vs[3:-1]
    return bytes(vs), chk

samples = [
    '50f4647481',
    '50c4647581',
    '50045bd642',
    '50745bd702',
    '50a45bf642',
    '50d45bf702',
    '5084650481',
    '5034650501',
    '500465c491',
    '50a465c501',
    '50a5653501',
    '50f5653601',
    '50b45cc591',
    '50745cc601',
    '506464b481',
    '508464b601',
    '4714622521',
    '4744623521',
    '47d665c491',
]

for poly in range(3, 16, 2):
    for init in range(0, 16):
        n = 0
        for sample in samples:
            ns, chk = parse_sample(sample)
            cchk = crc4(poly, ns, init=init)
            if chk == cchk: n += 1
            print(poly, init, sample, hex(chk), hex(cchk))
        if n == len(samples): print(poly, init)
        else: print(poly, init, n / len(samples))
