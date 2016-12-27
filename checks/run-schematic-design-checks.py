#!/usr/bin/env python

import sys
import xml.etree.ElementTree as ET
from optparse import OptionParser
from itertools import chain
from helpers import get_parts_by_triple, get_part_attribute, has_part_number, only_placed_components

def run(schematic_file, options):
  tree_root = ET.parse(schematic_file).getroot()
  parts = tree_root.findall('*//part')

  errors = chain(
    # First, check if there are any parts without a part number, whether the attribute
    # is missing or the part number is just empty.
    check_for_missing_or_empty_part_numbers(parts, options),

    # Then check to see if there is more than one unique part number for a given part triple.
    # While you may specify different voltage ratings for decoupling caps based on the rail
    # they're decoupling (but use the same package/value), we generally want to simplify buying
    # by using a part which satisfies the highest ratings required.  So if we have a bunch of
    # bulk 0402 0.1uF capacitors, and some of them are seeing 12V, we're going to use 25V rated
    # ones across the board.
    #
    # The intent should be that if something has a different enough requirement that is exotic
    # or would otherwise bump the price up, it should be called out in the value, thereby
    # distinguishing the part triple so it can be considered separately.
    check_for_uniqueness_in_part_triples(parts, options),

    # Check whether parts have a HEIGHT attribute.  This is semi-important if something doesn't
    # have a model in CircuitWorks but we want it to give us the default bounding box to simulate
    # the part and expect it to have a correct height for clearance/interference checks.
    check_for_height_attribute(parts, options),
  )

  # Convert to a list of errors, thereby triggering our checks to run.
  errors = list(errors)
  if len(errors) > 0:
    for error in errors:
      print error

    sys.exit(1)
  else:
    print "All checks passed!"

def check_for_missing_or_empty_part_numbers(parts, options):
  parts = only_placed_components(parts)
  parts = filter(lambda x: not has_part_number(x), parts)
  grouped_parts = get_parts_by_triple(parts)

  for (k, g) in grouped_parts:
    yield "[missing-empty-part-number] Found part group {} with missing or empty part numbers: {}".format(k, ', '.join(map(lambda x: x.attrib.get('name'), g)))

def check_for_uniqueness_in_part_triples(parts, options):
  parts = only_placed_components(parts)
  grouped_parts = get_parts_by_triple(parts)
  for (k, g) in grouped_parts:
    unique_part_numbers = map(lambda x: get_part_attribute(x, 'PN'), g)
    unique_part_numbers = filter(lambda x: x != '', unique_part_numbers)
    unique_part_numbers = set(unique_part_numbers)

    # We only care when there's two or more part numbers, because triples with
    # no part number whatsoever, or some with and some without, are caught before.
    if len(unique_part_numbers) > 1:
      yield "[uniqueness] Found part group {} with two or more part numbers in use: {}".format(k, ', '.join(unique_part_numbers))

def check_for_height_attribute(parts, options):
  if options.check_height:
    parts = only_placed_components(parts)
    for part in filter(lambda x: get_part_attribute(x, 'HEIGHT') == '', parts):
      yield "[part-height] Part {} missed HEIGHT attribute or empty!".format(part.attrib.get('name'))

if __name__ == "__main__":
  usage = "usage: %prog [options] schematic_path"
  parser = OptionParser(usage)
  parser.add_option("-z", "--check-height", dest="check_height", action="store_true", default=False,
                    help="check or not to check for a HEIGHT attribute")

  (options, args) = parser.parse_args()
  if len(args) != 1:
    parser.error("incorrect number of args; must specify schematic file")

  run(args[0], options)
