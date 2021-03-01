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

from flask import Flask
from flask import request

app = Flask(__name__)

line_seen = set()

@app.route('/', methods =['POST'])
def post():
        if request.method == 'POST':
            print(request.data)
            datastr = str(request.data)
            dataclean = datastr[1:].replace('\\r', '').strip("'").replace('\\n','\n')
            with open("TempINPUT.txt", "wt") as SERVERDATARAW:
                SERVERDATARAW.write(dataclean)
            SERVERDATARAW.close()
            SERVERDATARAW = open("TempINPUT.txt", "rt")
            with open("PLAYERGATHERDATA.txt", "a") as SERVERDATA:
                for line in SERVERDATARAW: 
                    if line not in line_seen:
                        SERVERDATA.write(line)
                        line_seen.add(line)   
            return 'FINISHED'
            
if __name__ == '__main__':
    app.run(host= '0.0.0.0', port="8000")
