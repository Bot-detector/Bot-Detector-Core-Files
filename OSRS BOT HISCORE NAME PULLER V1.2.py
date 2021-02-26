#!/usr/bin/env python
# coding: utf-8

# In[6]:


#Author RSN: FERRARIIC 2/7/2021

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
DATADIR = "C:\Datasets\OSRSPlayerlist\BLAST.txt" #Filename for player names [#####MODIFY THIS VARIABLE POSSIBLE#####]

fRAW = open(DATADIR, "rt") #opens raw bot file
fCLEAN = open("2162021BLAST.txt", "wt") #starts new bot file type

line_seen = set() #Duplicate set check

for line in fRAW: 
    if line not in line_seen:
        fCLEAN.write(line.replace(' ', '_'))
        line_seen.add(line)        
        
f = open("2162021BLAST.txt", "rt") #reopens CLEAN file to read as f
num_lines = sum(1 for line in open('2162021BLAST.txt')) #finds number of entries

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

for x in f: #sorts through file looking for player names
    clear_output(wait=True)
    PLAYER = x #reads line of text file
    print("New player name:", PLAYER) 
    print("Pass Rate:", round(total*100,1),"%", "| Pass:",notfail, "| Fail:",fail,"| Total:",(fail+notfail),"| Total in File:", num_lines, "| Completed:", round(percent_complete*100,2),"%")
    print("Total Time:", int(elapsed_time), "| Estimated Time:", int(Estimated_time), "| Remaining Time", int(Remaining_time))
    url = MAIN+PLAYER #concats main + player for link
    print(url) #prints url REMOVE SOON
    response = requests.get(url) #gets skill info from Hiscores
    data = response.text #Pulls info from hiscores as variable (data)
    if data.find('404 - Page not found') != -1: #== '<!DOCTYPE html><html><head><script src="/Criciousand-meth-shake-Exit-be-till-in-ches-Shad" async></script><title>404 - Page not found</title> <meta charset="UTF-8"/><meta name="viewport" content="width=device-width, initial-scale=1" /><style>body, html{margin: 0; padding: 0; height: 100%; overflow: hidden;}#content{position:absolute; left: 0; right: 0; bottom: 0; top: 0px;}.error-frame{height: 100%;width: 100%;border: 0;}</style></head><body><div id="content"><iframe class="error-frame" src="https://www.runescape.com/error404"></iframe></div><script src="//ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script><script type="text/javascript" src="https://www.runescape.com/js/rs3/plugins-7.js"></script><script src="https://www.runescape.com/js/rs3/gtm-0.js"></script></body></html>\n':
        #print(data)
        fail += 1
        total = notfail/(notfail+fail)
        percent_complete = (notfail+fail)/num_lines
        elapsed_time = time.time() - start_time
        Estimated_time = elapsed_time/percent_complete
        Remaining_time = Estimated_time-elapsed_time
    else:
        r = str.split(data) 
        DATAarray = [[float(n) for n in row.split(",")] for row in r] #Convert STRING of DATA into ARRAY
        training_data.append([PLAYER, DATAarray])
        #print(training_data)
        notfail += 1
        total = notfail/(notfail+fail)
        percent_complete = (notfail+fail)/num_lines
        elapsed_time = time.time() - start_time
        Estimated_time = elapsed_time/percent_complete
        Remaining_time = Estimated_time-elapsed_time


# In[7]:


with open("PLAYERSHISCORES.pickle", "wb") as PLAYERS_pickle: #STORES DATA AS .PICKLE FORMAT
    pickle.dump(training_data, PLAYERS_pickle)


# In[8]:


PLAYER_DATA = pickle.load(open('PLAYERSHISCORES.pickle', 'rb')) #TEST OPEN

PLAYER_DATA[25][1][0][2] #TEST RECALL

