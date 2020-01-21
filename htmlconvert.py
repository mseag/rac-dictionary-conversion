#!/usr/bin/python3

# Try converting the HTML file version of the Word doc, just to see if it works well

import fileinput
from lxml import etree
from lxml.html import html5parser
import re
import sys
import csv
import email.parser
import quopri
import html


def convert_to_points(text):
    unit = text[-2:]
    value = float(text[:-2])
    if unit == "in":
        return value * 72.0
    else:
        return value

def is_indented(elem):
    style = elem.get('style', '')
    parts = style.split(';')
    leftmargin = 0.0
    textindent = 0.0
    for part in parts:
        if part.startswith('margin-left'):
            value = part.split(':', 1)[1]
            leftmargin = convert_to_points(value)
        if part.startswith('text-indent'):
            value = part.split(':', 1)[1]
            textindent = convert_to_points(value)
    totalindent = leftmargin + textindent
    # Indents in this file are either 0 or 14 or more
    return (totalindent >= 10.0)

def unescape_html_repr(elem):
    html.unescape(etree.tostring(elem).decode('utf-8'))
    # That fetches the complete HTML representation, as a Unicode string, so I can grep it for Khmer text if needed

def look_for(rootdiv, s):
    items = [x for x in rootdiv if s in html.unescape(etree.tostring(x).decode('utf-8'))]
    texts = [html.unescape(etree.tostring(x, method="text", encoding="utf-8").decode('utf-8')) for x in items]
    return texts

def text_of(elem):
    return etree.tostring(elem, method="text", encoding="utf-8").decode('utf-8').replace('\n', ' ')

def convert_file(fname):
    out_fname = fname.replace('.mht', '.txt')
    with open(fname, "rb") as f:
        e = email.message_from_binary_file(f)

    htmlText = ""
    for part in e.walk():
        if part.get_content_type() == "text/html":
            htmlText = part.get_payload()
            break

    if not htmlText:
        print("Could not find HTML text in {}".format(fname))
        sys.exit(2)

    b = quopri.decodestring(htmlText.encode('utf-8'))
    content = b.decode('utf-8')
    doc = html5parser.document_fromstring(content)
    body = doc[1]
    rootdiv = body[-1]

    with open(out_fname, "w") as out_f:
        for p in rootdiv:
            text = text_of(p)
            if re.match(r'\s', text) or is_indented(p):
                out_f.write("\t{}\n".format(text.strip()))
            else:
                out_f.write("{}\n".format(text.strip()))

for fname in sys.argv[1:]:
    print("Handling {}...".format(fname))
    convert_file(fname)
