#!/usr/bin/python3

import fileinput
import re
import sys

khmer_numerals = "០១២៣៤៥៦៧៨៩"

def fix_badly_wrapped_lines(lastline, line):
    if len(re.findall("/", line)) < 2:
        return lastline.rstrip() + " " + line.lstrip()
    else:
        return line.rstrip()

numbers = []

def format_output(headword, sense_number, subentry, pronunciation, grammatical_info, parenthesis_contents, definition):
    return "{}|{}|{}|{}|{}|{}|{}".format(headword, sense_number, subentry, pronunciation, grammatical_info, parenthesis_contents, definition)

def process(line):
    # Break line down into headword, pronunciation, etc.
    headword = ""
    sense_number = ""
    subentry = ""
    pronunciation = ""
    grammatical_info = ""
    parenthesis_contents = ""
    definition = ""
    parts = re.split("/", line, 2)
    if len(parts) > 2:
        before, middle, after = parts
        pronunciation = middle.strip()
        # print(before.strip(), "-|-", mid.strip(), "-|-", after.strip())

        # Extract sense number if present
        parts = re.split(r"(\d+)", before.rstrip(), 1)  # \d also matches [០-៩] thanks to Unicode
        if len(parts) > 1:
            before, middle, _ = parts
            headword = before
            sense_number = middle.strip()
        else:
            headword = parts[0]

        # If headword has leading spaces, this is a subentry
        if re.match(r"^\s", headword):
            subentry = headword.strip()
            headword = ""
        else:
            headword = headword.strip()

        # Extract source/etymology (found in parentheses) if present
        parts = re.split(r"\((.*)\)", after.strip(), 1)
        if len(parts) > 1:
            before, middle, after = parts
            grammatical_info = before.strip()
            parenthesis_contents = middle.strip()
            definition = after.strip()
        else:
            # Some lines have "..." in them, so we need to search for a dot NOT preceded or followed by another dot
            dots_match = re.search(r"((?<!\.)\.(?!\.))", parts[0])
            if dots_match:
                grammatical_info = dots_match.string[:dots_match.end(1)]
                definition = dots_match.string[dots_match.end(1):].strip()
            else:
                # No grammatical info found
                definition = parts[0].strip()
    else:
        # Any lines that still don't contain a slash are not actual input data
        return None
    return format_output(headword, sense_number, subentry, pronunciation, grammatical_info, parenthesis_contents, definition)


def run_test():
    test_line = "បើក ១ /បើក/ កិ. ធ្វើឱ្យច្រហ, ឱ្យមានផ្លូវ, មានទំនង...។"
    expected_output = "បើក|១||បើក|កិ.||ធ្វើឱ្យច្រហ, ឱ្យមានផ្លូវ, មានទំនង...។"

    output = process(test_line)
    if output != expected_output:
        print("Unexpected results from test: got", output, "and expected", expected_output, file=sys.stderr)
        exit(2)

def process_input():
    lastline = ""
    print(format_output("Headword", "Sense number", "Subentry", "Pronunciation", "Part of Speech", "Source/Etymology", "Definition"))
    for line in fileinput.input():
        fixed_line = fix_badly_wrapped_lines(lastline, line)
        result = process(fixed_line)
        if result is not None:
            print(result)
        lastline = line

run_test()
process_input()
