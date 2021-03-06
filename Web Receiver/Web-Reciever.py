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

from flask import request, abort, current_app as app
from flask import Flask
from flask import request
import re
import time
import pickle
import numpy as np
import pandas as pd
import time
import os
import requests
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import normalize
from sklearn.preprocessing import scale

line_seen = set()
response = 0
check = 0
ip_timelog = []
ip_ban_list = []
ip_whitelist = [('127.0.0.1')]
ipr = []
PLAYER_NAME = []
returned_data = []
newplayername = []
newplayerskills = []
DATAarray = []
userfixed = ""

MAIN = "http://services.runescape.com/m=hiscore_oldschool/index_lite.ws?player="

osrsknn = pickle.load(open("OSRS_KNN_V1","rb"))
y_km = pickle.load(open("ykmfile","rb"))
PLAYER_TRAIN = pickle.load(open("traindata","rb"))
player_name = pickle.load(open("pnamefile","rb"))

for name in player_name:
    PLAYER_NAME.append(name.replace('\n',''))
    
##################################################################################################

app = Flask(__name__)

@app.before_request
def block_method(r = 0):
    ip = request.environ.get('REMOTE_ADDR')
    
    if ip in ipr:
        r = ipr.index(ip)
        check = 1
    else:
        ip_timelog.append([ip,time.time()])
        check = 0
        ipr.append(ip)
    
    last_time = ip_timelog[r][1]
    response = time.time()-last_time
    ip_timelog[r][1] = time.time()
    
    if check == 1:
        if response < 1:
            if ip not in ip_whitelist:
                if ip in ip_ban_list:
                    abort(403)
                else:
                    ip_ban_list.append(ip)
                    abort(403)
        else:
            if ip not in ip_whitelist:
                if ip in ip_ban_list:
                    abort(403)
    print("Response Time: ", response)
    print("Timelog: ", ip_timelog)
    print("IP REC: ", ipr)
    print("Banlist: ", ip_ban_list)
    print("Whitelist: ", ip_whitelist)
    return 

@app.route('/', methods =['POST'])
def post():
    if request.method == 'POST':
        print(request.data)
        datastr = str(request.data)
        dataclean = datastr[1:].replace('\\r', '').strip("'[]").replace(', ','\n')
        with open("TempINPUT.txt", "wt") as SERVERDATARAW:
            SERVERDATARAW.write(dataclean)
        SERVERDATARAW.close()
        SERVERDATARAW = open("TempINPUT.txt", "rt")
        with open("PLAYERGATHERDATA2.txt", "a") as SERVERDATA:
            for line in SERVERDATARAW:
                if len(line)<13:
                    L = re.findall('[a-zA-Z0-9_-] *', line)
                    line = ''.join(map(str, L))
                    if line not in line_seen:
                        SERVERDATA.write(line + '\n')
                        line_seen.add(line)
    return 
        
@app.route('/user/<user>', methods =['GET'])
def get(user):
    userfixed = user.replace(' ','_')
    print(userfixed)
    if userfixed in PLAYER_NAME:
        ind = PLAYER_NAME.index(userfixed)
        osrsknn_predict = osrsknn.predict(PLAYER_TRAIN[ind].reshape(1,-1))
        player_predprob = osrsknn.predict_proba(PLAYER_TRAIN[ind].reshape(1,-1))
        print(osrsknn_predict)
        print(player_predprob)
        print(y_km[ind])
        print(PLAYER_NAME[ind])
    else:
        try:
            print("User not found. Currently evaluating user...")
            pulldata(userfixed)
        except: 
            print("AN ERROR WAS ENCOUNTERED")
    return 
        
def pulldata(userfixed):
    url = MAIN+userfixed 
    #print(url) 
    response = requests.get(url) 
    data = response.text 
    try: 
        if data.find('404 - Page not found') != -1:
            print("PLAYER STATS UNREACHABLE.")
        else:
            r = str.split(data) 
            DATAarray = [[float(n) for n in row.split(",")] for row in r]
            print(DATAarray)
            cleanup(DATAarray)
    except: 
        print("ERROR, try again later.")
    return 
#check for errors
def cleanup(DATAarray):
    PLAYER_IND = pickle.load(open("PIfile","rb"))

    global newplayerskills
    DATAcheck = np.asarray(DATAarray)
    for x in range(0,len(DATAcheck)):
        if (0<x<24):
            newplayerskills = np.append(newplayerskills,DATAcheck[x][2])
        if (24<x<80):
            newplayerskills = np.append(newplayerskills,DATAcheck[x][1])

    PLAYER_IND = np.reshape(PLAYER_IND,(78,12869))
    PLAYER_IND = np.reshape(PLAYER_IND,(12869,78))
    scaler = StandardScaler()
    PLAYER_IND = scaler.fit_transform(PLAYER_IND)
    print(newplayerskills)
    newplayerskills = np.asarray(newplayerskills)
    newplayerskills = scaler.transform(newplayerskills.reshape(1, -1))
    
    print("DATA CLEANED FOR USER")
    osrsKNN(newplayerskills)
    newplayerskills = []
    return 

def osrsKNN(newplayerskills):
    print("SCANNING...")
    osrsknn_predict = osrsknn.predict(newplayerskills.reshape(1, -1))
    player_predprob = osrsknn.predict_proba(newplayerskills)
    print("Group: "+str(osrsknn_predict))
    print("Player Grouping Data: "+str(player_predprob))
    print("PLAYER SUCCESSFULLY SCANNED")
    return 

if __name__ == '__main__':
    app.run(port="8000")
