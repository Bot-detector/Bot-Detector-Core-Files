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

line_seen = set()
response = 0
ip_timelog = []
ip_ban_list = []
check = 0
ipr = []

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
        if response < 3:
            if ip in ip_ban_list:
                abort(403)
            else:
                ip_ban_list.append(ip)
                abort(403)
        else:
            if ip in ip_ban_list:
                abort(403)
    print("Response Time: ", response)
    print("Timelog: ", ip_timelog)
    print("IP REC: ", ipr)
    print("Banlist: ", ip_ban_list)

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
            
            return 'FINISHED'
            
if __name__ == '__main__':
    app.run(port="8000")
