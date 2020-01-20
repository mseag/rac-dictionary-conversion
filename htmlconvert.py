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

with open("Orthographe ប 21.mht", "rb") as f:
    e = email.message_from_binary_file(f)

htmlText = ""
for part in e.walk():
    if part.get_content_type() == "text/html":
        htmlText = part.get_payload()
        break

if htmlText:
    print("Found HTML text starting with:", htmlText[:100])

    b = quopri.decodestring(htmlText.encode('utf-8'))
    content = b.decode('utf-8')
    print("Decoded HTML text starts with:", content[:100])
    doc = html5parser.document_fromstring(content)
    body = doc[1]
    rootdiv = body[0]

styles_found = ['margin-left:14.7pt;text-indent:-14.7pt;line-height:90%',
 'margin-left:.2in;text-align:justify;text-indent:-.2pt',
 'margin-left:14.2pt;text-align:justify;text-indent:-14.2pt;tab-stops:18.9pt',
 'margin-left:.2in;text-align:justify;text-indent:-.2in',
 'margin-left:14.2pt;text-align:justify;text-indent:-14.2pt;line-height:90%',
 'line-height:90%;tab-stops:13.5pt',
 'margin-left:14.2pt;text-align:justify',
 'line-height:90%;tab-stops:.25in',
 'text-align:justify',
 'margin-left:.5in;text-align:justify',
 'margin-left:14.2pt;text-align:justify;text-indent:-14.2pt;tab-stops:21.3pt',
 'margin-left:14.2pt;text-align:justify;text-indent:-14.2pt;tab-stops:14.2pt22.5pt',
 'margin-left:14.2pt;text-align:justify;text-indent:-14.2pt;tab-stops:14.2pt.25in',
 'text-indent:14.2pt;line-height:90%',
 'margin-left:14.2pt;text-indent:-14.2pt;page-break-after:auto;tab-stops:.25in',
 'margin-left:14.2pt;text-align:justify;text-indent:-14.2pt;tab-stops:.25in27.0pt',
 'margin-left:14.2pt;text-align:justify;text-indent:-14.2pt;tab-stops:13.5pt',
 'margin-left:14.2pt;text-align:justify;text-indent:-14.2pt;line-height:80%',
 'margin-left:14.2pt;text-align:justify;text-indent:21.8pt',
 'margin-left:14.2pt;text-align:justify;text-indent:-14.2pt;tab-stops:14.2pt',
 'text-align:justify;tab-stops:14.2pt.25in',
 'margin-top:0in;margin-right:-7.1pt;margin-bottom:0in;margin-left:14.2pt;margin-bottom:.0001pt;text-align:justify',
 'margin-left:14.2pt;text-align:justify;text-indent:-14.2pt;tab-stops:22.5pt',
 'text-align:justify;text-indent:14.2pt',
 'margin-top:0in;margin-right:-7.1pt;margin-bottom:0in;margin-left:14.2pt;margin-bottom:.0001pt;text-align:justify;text-indent:-14.2pt;line-height:80%',
 'margin-left:.25in;text-align:justify;text-indent:-.25in;line-height:90%',
 'margin-top:0in;margin-right:-14.2pt;margin-bottom:0in;margin-left:14.2pt;margin-bottom:.0001pt;text-align:justify;text-indent:-14.2pt',
 'margin-top:0in;margin-right:-7.1pt;margin-bottom:0in;margin-left:14.2pt;margin-bottom:.0001pt;text-align:justify;text-indent:-14.2pt;tab-stops:.25in',
 'margin-left:28.35pt;text-align:justify;text-indent:-14.2pt',
 'margin-left:14.2pt;text-align:justify;text-indent:-14.2pt',
 'page-break-after:auto;tab-stops:.25in',
 'margin-left:14.2pt;text-align:justify;text-indent:-14.2pt;tab-stops:13.5pt.25in',
 'margin-left:14.2pt;text-indent:-14.2pt',
 'text-align:justify;tab-stops:21.3pt',
 'margin-left:14.2pt;text-align:justify;text-indent:-14.2pt;tab-stops:27.0pt',
 'margin-left:.2in;text-align:justify',
 'margin-left:14.2pt;text-align:justify;text-indent:-14.2pt;tab-stops:.25in22.5pt',
 'page-break-after:auto',
 'text-align:justify;text-indent:.5in',
 'line-height:90%',
 'text-align:justify;line-height:90%',
 'margin-left:14.2pt;text-align:justify;text-indent:-14.2pt;tab-stops:.25in',
 'margin-top:0in;margin-right:-7.1pt;margin-bottom:0in;margin-left:14.2pt;margin-bottom:.0001pt;text-align:justify;text-indent:-14.2pt',
 'margin-left:.25in;text-align:justify;text-indent:-.25in']

def convert_to_points(text):
    unit = text[-2:]
    value = float(text[:-2])
    if unit == "in":
        return value * 72.0
    else:
        return value

leftmargins = []
textindents = []
totalindents = []
for style in styles_found:
    parts = style.split(';')
    leftmargin = 0.0
    textindent = 0.0
    for part in parts:
        if part.startswith('margin-left'):
            value = part.split(':', 1)[1]
            leftmargin = convert_to_points(value)
            leftmargins.append(leftmargin)
        if part.startswith('text-indent'):
            value = part.split(':', 1)[1]
            textindent = convert_to_points(value)
            textindents.append(textindent)
    totalindents.append(leftmargin + textindent)
    margin_related_parts = [part for part in parts if part.startswith('text-indent') or part.startswith('margin-left')]
    if margin_related_parts:
        print(margin_related_parts)
        # TODO: Convert inches to points (1in = 72pt) and then add margin-left to text-indent to get total indentation level
        # Then print out a bunch of sample lines that are and aren't indented, and see if that matches the document
print("Left margins:", list(set(leftmargins)))
print("Text indents:", list(set(textindents)))
print("Total indents in pt:", list(set(totalindents)))

left_margins = ['margin-left:28.35pt', 'margin-left:14.7pt', 'margin-left:.2in', 'margin-left:14.2pt', 'margin-left:.5in', 'margin-left:.25in']

# 14.7pt is about .2in, and 28.35pt is about .4in

def unescape_html_repr(elem):
    html.unescape(etree.tostring(elem).decode('utf-8'))
    # That fetches the complete HTML representation, as a Unicode string, so I can grep it for Khmer text if needed

def look_for(rootdiv, s):
    items = [x for x in rootdiv if s in html.unescape(etree.tostring(x).decode('utf-8'))]
    texts = [html.unescape(etree.tostring(x, method="text", encoding="utf-8").decode('utf-8')) for x in items]
    return texts

print(look_for(rootdiv, "បណ្ដាញ"))
