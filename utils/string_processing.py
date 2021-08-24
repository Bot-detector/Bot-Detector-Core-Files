import re

def is_valid_rsn(rsn):
    return re.fullmatch('[\w\d _-]{1,12}', rsn)

def to_jagex_name(name: str) -> str:
    return name.replace('_', ' ').replace('-', ' ').strip()