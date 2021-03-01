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
