from itertools import groupby

def is_supply_part(part):
  library = part.attrib.get('library', '')
  device = part.attrib.get('device', '')

  return library.startswith('supplies') and device == ''

def is_excluded_part(part):
  return get_part_attribute(part, 'BOM') == 'EXCLUDE'

def get_part_attribute(part, name):
  attribs = part.findall('attribute')
  for attrib in attribs:
    if attrib.attrib.get('name', '') == name:
      return attrib.get('value', '')

  return ''

def has_part_number(part):
  return get_part_attribute(part, 'PN') != ''

def get_device_key(part):
  deviceset = part.attrib.get('deviceset', '')
  device = part.attrib.get('device', '')
  value = part.attrib.get('value', '')

  return "{}{}-{} (value: {})".format(deviceset, device, value, value)

def only_placed_components(parts):
  parts = filter(lambda x: not is_excluded_part(x), parts)
  parts = filter(lambda x: not is_supply_part(x), parts)
  return parts

def get_parts_by_triple(parts):
  return groupby(sorted(parts, key=get_device_key), get_device_key)
