#######################################################################################
# BSD 2-Clause License

# Copyright (c) 2021, Ferrariic
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, 
    # this list of conditions and the following disclaimer.

 #2. Redistributions in binary form must reproduce the above copyright notice, 
    # this list of conditions and the following disclaimer in the documentation 
    # and/or other materials provided with the distribution.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#######################################################################################

import numpy as np
import re
import pandas as pd
import matplotlib.pyplot as plt
import pickle
import time
import os
import urllib 
from urllib import request
import requests
from IPython.display import clear_output
########################################################################################

MAIN = "http://services.runescape.com/m=hiscore_oldschool/index_lite.ws?player=" #main source url
DATADIR = "C:\Datasets\OSRSPlayerlist\CLEANFULL.txt" #Filename for player names 

fRAW = open(DATADIR, "rt") #opens raw bot file
fCLEAN = open("CLEAN.txt", "wt") #starts new bot file type

line_seen = set() #Duplicate set check

for line in fRAW: 
    if line not in line_seen:
        fCLEAN.write(line.replace(' ', '_'))
        line_seen.add(line)        
        
f = open("CLEAN.txt", "rt") #reopens CLEAN file to read as f
num_lines = sum(1 for line in open('CLEAN.txt')) #finds number of entries

########################################################################################
training_data = [] #STORES PLAYER DATA IN ARRAY
fail = 0 #number of failed attempts
notfail = 0 #number of passed attempts
total = 0 #total number of attempts = notfail/(notfail+fail)
percent_complete = 0 #total percent complete = (notfail+fail)/num_lines
Estimated_time = 0 #Estimated time = elapsed_time/percent_complete
Remaining_time = 0 #Remaining run time
elapsed_time = 0

start_time = time.time() #begins program time

for x in f: 
    clear_output(wait=True)
    PLAYER = x 
    print("New player name:", PLAYER) 
    print("Pass Rate:", round(total*100,1),"%", "| Pass:",notfail, "| Fail:",fail,"| Total:",(fail+notfail),"| Total in File:", num_lines, "| Completed:", round(percent_complete*100,2),"%")
    print("Total Time:", int(elapsed_time), "| Estimated Time:", int(Estimated_time), "| Remaining Time", int(Remaining_time))
    url = MAIN+PLAYER 
    print(url) 
    response = requests.get(url) 
    data = response.text 
    try: 
        if data.find('404 - Page not found') != -1: #== '<!DOCTYPE html><html><head><script src="/Criciousand-meth-shake-Exit-be-till-in-ches-Shad" async></script><title>404 - Page not found</title> <meta charset="UTF-8"/><meta name="viewport" content="width=device-width, initial-scale=1" /><style>body, html{margin: 0; padding: 0; height: 100%; overflow: hidden;}#content{position:absolute; left: 0; right: 0; bottom: 0; top: 0px;}.error-frame{height: 100%;width: 100%;border: 0;}</style></head><body><div id="content"><iframe class="error-frame" src="https://www.runescape.com/error404"></iframe></div><script src="//ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script><script type="text/javascript" src="https://www.runescape.com/js/rs3/plugins-7.js"></script><script src="https://www.runescape.com/js/rs3/gtm-0.js"></script></body></html>\n':
            fail += 1
            total = notfail/(notfail+fail)
            percent_complete = (notfail+fail)/num_lines
            elapsed_time = time.time() - start_time
            Estimated_time = elapsed_time/percent_complete
            Remaining_time = Estimated_time-elapsed_time
            with open("NAMEFAIL.txt", "a") as NAMEFAILS:
                NAMEFAILS.write(PLAYER)
        else:
            r = str.split(data) 
            DATAarray = [[float(n) for n in row.split(",")] for row in r] #Convert STRING of DATA into ARRAY
            training_data.append([PLAYER, DATAarray])
            notfail += 1
            total = notfail/(notfail+fail)
            percent_complete = (notfail+fail)/num_lines
            elapsed_time = time.time() - start_time
            Estimated_time = elapsed_time/percent_complete
            Remaining_time = Estimated_time-elapsed_time
    except: 
        print("ERROR but will continue")

# In[7]:

with open("PLAYERSHISCORES.pickle", "wb") as PLAYERS_pickle: #STORES DATA AS .PICKLE FORMAT
    pickle.dump(training_data, PLAYERS_pickle)

# In[8]:

PLAYER_DATA = pickle.load(open('PLAYERSHISCORES.pickle', 'rb')) #TEST OPEN
PLAYER_DATA[25][1][0][2] #TEST RECALL

