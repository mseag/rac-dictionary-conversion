#!/usr/bin/python3

import fileinput
import re

def fix_badly_wrapped_lines(lastline, line):
    if not re.search("/", line):
        return lastline.rstrip() + " " + line.lstrip()
    else:
        return line.rstrip()

def process(line):
    # Break line down into headword, pronunciation, etc.
    # TODO: Write this
    if not re.search("/", line):
        print("Line without slash:", line)

lastline = ""
for line in fileinput.input():
    fixed_line = fix_badly_wrapped_lines(lastline, line)
    process(fixed_line)
    lastline = line
