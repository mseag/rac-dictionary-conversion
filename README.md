# Khmer dictionary parser

A simple script to parse a dictionary file in MS Word format and produce an Excel spreadsheet with structured data

## Instructions

* Install Python 3
* Install the `lxml` and `html5lib` modules for Python 3
  * On Ubuntu Linux, run `sudo apt intall python3-lxml python3-html5lib`
* Get the input files in `.mht` format (in Word, save as "Single File Web Page (*.mht)")
* Put the input files in their own folder (for these instructions, let's say the folder is called "Dictionary")
* Run `python3 htmlconvert.py Dictionary/*.mht`
  * This produces a `.txt` file for each `.mht` file
* Run `python3 convert.py Dictionary/*.txt`
  * This produces a `.csv` file *and* a `.sfm` file for each `.txt` file
* Import the `.csv` files into Excel, or whatever else you need done with them
* Import the `.sfm` files into FieldWorks
