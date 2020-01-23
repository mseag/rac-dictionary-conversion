#!/usr/bin/python3

import fileinput
import re
import sys
import csv

def is_even(n):
    return n % 2 == 0
def is_odd(n):
    return n % 2 != 0

def fix_badly_wrapped_lines(lastline, line):
    """
    Returns a tuple of (bool, str).
    The bool indicates whether the input line was a complete line on its own, or whether it's
    a partial line that had to be appended to the previous line in order to be complete.

    This is used in the processing for loop, because we wait until the *next* complete line to
    process the *previous* complete line.
    """
    # Some lines have two pronunciations, therefore four slashes
    # Any line with an even number of slashes is probably okay
    slashes = re.findall("/", line)
    if is_even(len(slashes)):
        # Unless it has no slashes at all, in which case it was part of the previous line
        if len(slashes) == 0:
            return False, lastline.rstrip() + " " + line.lstrip()
        else:
            return True, line.rstrip()
    # A line with an odd number of slashes is tricky, because we might have two lines like this:
    # word /long-pronunciation-that-
    #    got-split-across-lines/ definition
    # The rule that works with our input data is that if the previous line had an even number of
    # slashes, it was complete, so this line is the first line of a pair. But if the previous line
    # had an odd number of slashes, this line is the second line of a pair and now we have the complete text.
    if is_odd(len(re.findall("/", lastline))):
        # Last line plus this line make a complete pair that can now be processed. We do NOT add a space in this scenario,
        # since pronunciation splits almost never should have had spaces in them.
        return True, lastline.rstrip() + line.lstrip()
    else:
        # Don't process this line yet since it's incomplete
        return False, ""

def fix_typoes(line):
    # There is one line containing "/ឬ " where it should have been "/ ឬ " with an extra space. This becomes
    # important in our pronunciation handling later.
    return line.replace("/ឬ ", "/ ឬ ")

most_recent_headword = ""
most_recent_sense_number = ""
def process(line):
    global most_recent_headword
    global most_recent_sense_number
    # Break line down into headword, pronunciation, etc.
    headword = ""
    sense_number = ""
    subentry = ""
    pronunciation = ""
    grammatical_info = ""
    parenthesis_contents = ""
    definition = ""

    # First, extract pronunciation, taking into account that there could be more than one
    parts = re.split("/", line)
    if len(parts) > 1:
        before = parts[0]
        middle = "".join(parts[1:-1])
        after = parts[-1]

        pronunciation = middle.strip()

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
            headword = most_recent_headword
            sense_number = most_recent_sense_number
        else:
            headword = headword.strip()
            most_recent_headword = headword
            most_recent_sense_number = sense_number

        # TODO: Detect examples (marked by ឧ.) in either source/etymology *or* definition, and strip them out.
        # If a parenthesis had nothing but an example in it, then source/etymology should be empty and that goes under "example" instead.

        # Extract source/etymology (found in parentheses) if present
        parts = re.split(r"\((.*)\)", after.strip(), 1)
        if len(parts) > 1:
            before, middle, after = parts
            grammatical_info = before.strip()
            parenthesis_contents = middle.strip()
            # A few lines have multiple parentheses, and the above regex is greedy
            parenthesis_contents = parenthesis_contents.replace("(", "").replace(")", "")
            definition = after.strip()
        else:
            # Some lines have "..." in them, so we need to search for a dot NOT preceded or followed by another dot
            dots_matches = list(re.finditer(r"((?<!\.)\.(?!\.))", parts[0]))
            if len(dots_matches) > 0:
                last_match = dots_matches[-1]
                grammatical_info = last_match.string[:last_match.end(1)]
                definition = last_match.string[last_match.end(1):].strip()
            else:
                # No grammatical info found
                definition = parts[0].strip()
    else:
        # Any lines that still don't contain a slash are not actual input data
        return None
    return (headword, sense_number, subentry, pronunciation, grammatical_info, parenthesis_contents, definition)  # TODO: Also return examples

def run_test(input, expected_output):
    output = process(input)
    if output != expected_output:
        print("Unexpected results from", input, ": got", output, "and expected", expected_output, file=sys.stderr)
        exit(2)

def output_entry_details(outfile, pronunciation, grammatical_info, parenthesis_contents, definition):
    # TODO: Also handle examples
    if pronunciation:
        print(r"\ph {}".format(pronunciation), file=outfile)
    if grammatical_info:
        print(r"\ps {}".format(grammatical_info), file=outfile)
    if parenthesis_contents:
        print(r"\etym {}".format(parenthesis_contents), file=outfile)
    if definition:
        print(r"\de {}".format(definition), file=outfile)

previous_headword_for_sfm = ("", "", "", "", "", "")  # TODO: Add seventh field here once we handle examples
previous_subentries = []
def output_to_sfm(outfile, headword, sense_number, subentry, pronunciation, grammatical_info, parenthesis_contents, definition):  # TODO: Add example parameter as well
    global previous_headword_for_sfm
    global previous_subentries

    if subentry and headword == previous_headword_for_sfm[0] and sense_number == previous_headword_for_sfm[1]:
        previous_subentries.append((subentry, pronunciation, grammatical_info, parenthesis_contents, definition))
    else:
        # New headword, so we're done adding subentries. Print out the previous one
        (prev_headword, prev_sense_number, prev_pronunciation, prev_grammatical_info, prev_parenthesis_contents, prev_definition) = previous_headword_for_sfm
        print(r"\lx {}".format(prev_headword), file=outfile)
        if prev_sense_number:
            print(r"\sn {}".format(prev_sense_number), file=outfile)
        output_entry_details(outfile, prev_pronunciation, prev_grammatical_info, prev_parenthesis_contents, prev_definition)
        for subentry in previous_subentries:
            (sub_lexeme, sub_pronunciation, sub_grammatical_info, sub_parenthesis_contents, sub_definition) = subentry  # TODO: Also handle examples
            print(r"\se {}".format(sub_lexeme), file=outfile)
            output_entry_details(outfile, sub_pronunciation, sub_grammatical_info, sub_parenthesis_contents, sub_definition)
        print("", file=outfile)

        previous_headword_for_sfm = (headword, sense_number, pronunciation, grammatical_info, parenthesis_contents, definition)
        previous_subentries = []

def process_input():
    lastline = ""
    last_complete_line = ""
    outfile_csv = None
    outfile_sfm = None
    out_sfm = None
    for line in fileinput.input():
        if fileinput.isfirstline():
            at_start = True
            csv_fname = fileinput.filename().replace(".txt", ".csv")
            sfm_fname = fileinput.filename().replace(".txt", ".sfm")
            if outfile_csv is not None:
                outfile_csv.close()
            if out_sfm is not None:
                out_sfm.close()
            outfile_csv = open(csv_fname, "w")
            csvwriter = csv.writer(outfile_csv)
            csvwriter.writerow(("Headword", "Sense number", "Subentry", "Pronunciation", "Part of Speech", "Source/Etymology", "Definition"))  # TODO: Also examples
            outfile_sfm = open(sfm_fname, "w")
        if at_start:
            if "/" not in line:
                continue  # Skip initial set of slash-less lines, as that's the intro text
            # Now we've seen a slash, so process this line and all subsequent lines
            at_start = False
        if line is None or not (line.strip()):
            continue  # Skip blank lines
        ready, maybe_fixed_line = fix_badly_wrapped_lines(lastline, line)
        fixed_line = fix_typoes(maybe_fixed_line)
        if ready:
            result = process(last_complete_line)
            if result is not None:
                csvwriter.writerow(result)
                output_to_sfm(outfile_sfm, *result)
        # If fix_badly_wrapped_lines returned an empty string, then we're not supposed to overwrite the previous completed line
        if maybe_fixed_line:
            last_complete_line = fixed_line
        lastline = line
    # Don't forget to process the last complete line, which won't have been output by the loop above
    last_result = process(last_complete_line)
    if last_result is not None:
        csvwriter.writerow(last_result)
        output_to_sfm(outfile_sfm, *last_result)
    # And one last call to output_to_sfm() to flush the last entry since it's still waiting for subentries that won't be arriving
    output_to_sfm(outfile_sfm, None, None, None, None, None, None, None)  # TODO: Add an eighth None here once we handle examples
    outfile_csv.close()
    outfile_sfm.close()

for input, expected_output in [
    ("បើក ១ /បើក/ កិ. ធ្វើឱ្យច្រហ, ឱ្យមានផ្លូវ, មានទំនង...។",
     ('បើក', '១', '', 'បើក', 'កិ.', '', 'ធ្វើឱ្យច្រហ, ឱ្យមានផ្លូវ, មានទំនង...។')),

    ("បស្ចិមទិស /បាស់-ចិម-ទឹស/ ឬ /ប៉ាច់-ចិម-ម៉ៈ-ទឹស/ ន. ",
     ('បស្ចិមទិស', '', '', 'បាស់-ចិម-ទឹស ឬ ប៉ាច់-ចិម-ម៉ៈ-ទឹស', 'ន.', '', '')),

    ("ប្អ៊ឹះ /ប្អ៊ឹះ/ គុ. ឬ កិ.វិ.",
     ('ប្អ៊ឹះ', '', '', 'ប្អ៊ឹះ', 'គុ. ឬ កិ.វិ.', '', '')),
    # TODO: Add test to demonstrate handling examples (marked by ឧ.)
]:
    run_test(input, expected_output)
process_input()
