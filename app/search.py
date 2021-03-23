import re
from db import NAMES

ALT_GROUPS = [
    ['n', 'hn', 'nn', 'hnn'],
    ['y', 'ie', 'ey', 'ee', 'i', 'ea', 'eigh'],
    ['c', 'k', 'ck', 'kh'],
    ['s', 'ss'],
    ['sy', 'sie', 'cy', 'cie', 'cee', 'see'],
    ['r', 'rh'],
    ['ph', 'f'],
    ['o', 'au', 'oh'],
    ['g', 'j'],
    ['ai', 'ay', 'a'],
    ['l', 'll'],
    ['m', 'mm'],
]

lower_names = [ name.lower() for name in NAMES ]

def find_alts(name, alts=[], checked=[]):
    '''
    Function to find alternate spellings for names.  Recursively finds alts of alts.
    '''

    for group in ALT_GROUPS:
        for unit in group:
            sub = '(' + '|'.join([ u for u in group if u != unit ]) + ')'
            alt = re.sub(sub, unit, name)
            if (alt != name) and (alt in lower_names) and (alt not in checked) and (alt not in alts):
                alts.append(alt)
    checked.append(name)
    
    if len(alts) == 0:
        return checked
    else:
        return find_alts(alts[0], alts=alts[1:], checked=checked)