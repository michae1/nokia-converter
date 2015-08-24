#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vobject
import io
import quopri
import re
import argparse
import sys

parser = argparse.ArgumentParser(description='Tool to convert your google exported vcard to older one used by microsoft nokia phones')
parser.add_argument('vcard30_infile', 
                   help='path to the gmail exported vcard file (or other vcard 3.0)')
parser.add_argument('--file21', metavar='vcard21_infile',  
                   help='path to vcard 2.1 (if you have new numbers in your phone)')
parser.add_argument('--outfile', nargs='?', type=argparse.FileType('w'),
                    default=sys.stdout)

args = parser.parse_args()

def get21_str(in_dict):
    """
    Simple template of vcard 2.1 (no photo etc yet)
    :param in_dict: dictionary of single vcard {"name":"[NAME]","tel":"[TEL]"}
    """
    return """BEGIN:VCARD
VERSION:2.1
N;ENCODING=QUOTED-PRINTABLE;CHARSET=UTF-8:;%s;;;
TEL;VOICE;CELL:%s
END:VCARD
"""%(quopri.encodestring(in_dict["name"]), in_dict["tel"])


card = vobject.vCard()

items21 = []
newItems = []
out_str = ""
phone_cnt = 0
newItemsIndex = {}
newItemsPhoneIndex = {}

# Parse Google exported file (VCARD 3.0) into newItems dict
stream = io.open(args.vcard30_infile, "r", encoding="utf-8")
eng_order = ('prefix', 'given', 'additional', 'family', 'suffix')
for item in vobject.readComponents(stream):
    display_name = ' '.join(item.n.value.toString(getattr(item.n.value, val)) for val in eng_order).strip()
    if len(display_name) > 0:
        phone_num = item.tel.value if "tel" in item.contents else None
        if not phone_num:
            continue
        phone_cnt += 1    
        newItem = {
            'name':display_name.encode('utf-8'),
            'tel': phone_num
        }
        newItems.append(newItem)
        newItemsIndex[newItem['name']] = True
        newItemsPhoneIndex[newItem['tel']] = True

# Parse Nokia vCard 2.1
v21_objects = []
commands = ('TEL', 'N', 'PHOTO', 'FN', 'TITLE', 'ORG', 'ADR', 'LABEL', 'EMAIL', 'REV') # all 2.1 possible fields
parse_patterns = {'TEL': '([+]?\d+)', 'N': 'N;[^;]*;[^;]*;([^;]+);'} # regexp to parse values
# possible fields convertions after parse
convertion = {
    'N': lambda s: quopri.decodestring(s)
}

if args.file21:
    with io.open(args.file21, "r", encoding="utf-8") as vcard21:
        current_obj = {}
        current_field = None
        current_card = ""
        current_command = None
        current_command_data = ""
        prev_command = None
        for line in vcard21:
            if 'END:VCARD' in line:
                if prev_command in parse_patterns:
                    possible_value = re.findall(parse_patterns[prev_command], current_command_data)
                    new_obj = possible_value[0] if len(possible_value) else None
                    current_obj[prev_command] = convertion[prev_command](new_obj) if prev_command in convertion else new_obj

                v21_objects.append(current_obj)
                prev_command = current_command
                current_obj = {}
                current_card = ""
                current_command = None
                current_command_data = ""

            else:
                if line.startswith(commands):
                    possible_command = re.findall('^(\w+)[:|;]', line)
                    current_command = possible_command[0] if len(possible_command) else None    

                    if current_command != prev_command:
                        if prev_command in parse_patterns:
                            possible_value = re.findall(parse_patterns[prev_command], current_command_data)
                            new_obj = possible_value[0] if len(possible_value) else None
                            current_obj[prev_command] = convertion[prev_command](new_obj) if prev_command in convertion else new_obj
         
                        prev_command = current_command  
                        current_command_data = ""    

                current_command_data += line

# Merge 2.1 object if there is no existent keys with phone number and name:
for obj in v21_objects:
    if not obj['N'] in newItemsIndex and not obj['TEL'] in newItemsPhoneIndex:
        newItems.append({
            'name': obj['N'],
            'tel': obj['TEL'] 
            })
        phone_cnt += 1

print "Total phones processed: %s"%phone_cnt

# Write results
with args.outfile as out_file:
    for item in newItems:
        out_file.write(get21_str(item))

