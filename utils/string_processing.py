import re

def is_valid_rsn(rsn):
    return re.fullmatch('[\w\d _-]{1,12}', rsn)

def to_jagex_name(name: str) -> str:
    #Allow for special characters as the first character of RSNs
    jagex_name = name[0:1] + name[1:].replace('_', ' ').replace('-', ' ').strip()
    return jagex_name

#https://github.com/AaronTraas/Clash-Royale-Clan-Tools/blob/79f90e5bd6d3008ebd25718f5bbdbee10c82e0ee/crtools/discord.py#L111
#Taken from above.
def escape_markdown(s):
    markdown_escape_map = {'_' : '\\_', '*' : '\\*', '<': '\\<', '@': '\\@', '//': '\\//'}
    for search, replace in markdown_escape_map.items():
        s = s.replace(search, replace)
    return s 