"""A program to find pairs of lines that only differ with a specific
number of bits at a specific column.

Example:

  python3 diffat.py 6 1 2 <<EOF
1234567
1234587
1234597
EOF

will display the last two lines, because the 6th character only
differs in 1 bit (0b1000 to 0b1001), while the first line differs to
the second in three (0b0110 to 0b1000).
"""

import sys

at = int(sys.argv[1])
l = int(sys.argv[2])
nbits = int(sys.argv[3])

prev = None
prevprinted = False
for line in sorted(sys.stdin, key=lambda line: line[:2] + line[3:]):
    line = line.strip()
    n = len(line)
    line = line[:2] + '_' + line[3:] + ' ' + line[2]
    if prev is not None:
        if (int(prev[at], 16) ^ int(line[at], 16)).bit_count() == nbits and prev[:at] == line[:at] and prev[at+l:n] == line[at+l:n]:
            if not prevprinted: print(prev)
            print(line, hex(int(line[at:at+l], 16) ^ int(prev[at:at+l], 16)))
            prevprinted = True
        else:
            prevprinted = False

    prev = line
