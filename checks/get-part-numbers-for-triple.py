#!/usr/bin/env python

import xml.etree.ElementTree as ET
from optparse import OptionParser
from helpers import get_parts_by_triple, get_part_attribute

def run(schematic_file, part_triple):
  tree_root = ET.parse(schematic_file).getroot()
  parts = tree_root.findall('*//part')

  grouped_parts = get_parts_by_triple(parts)
  for (k, g) in grouped_parts:
    if part_triple in k:
      # We're just matching a substring in the full part triple, which lets us
      # use the existing helpers which format the triple in a human-readable way.
      print "Found matching part triple '{}', which has the following part numbers:".format(k)

      part_numbers = set()
      for part in g:
        part_number = get_part_attribute(part, 'PN')
        if part_number is not '':
          part_numbers.add(part_number)

      for part_number in part_numbers:
        print "  - {}".format(part_number)

if __name__ == "__main__":
  usage = "usage: %prog [options] <schematic path> <part triple>"
  parser = OptionParser(usage)

  (options, args) = parser.parse_args()
  if len(args) != 2:
    parser.error("incorrect number of args; must specify schematic file and part triple")

  run(args[0], args[1])
