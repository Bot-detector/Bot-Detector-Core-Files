import re

def is_valid_rsn(rsn):
    return re.fullmatch('[\w\d _-]{1,12}', rsn)

def to_jagex_name(name: str) -> str:
    #Allow for special characters as the first character of RSNs
    jagex_name = name[0:1] + name[1:].replace('_', ' ').replace('-', ' ').strip()
    return jagex_name