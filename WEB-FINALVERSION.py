#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from flask import Flask
from flask import request

app = Flask(__name__)

SERVERDATA = open("PLAYERGATHERDATA.txt", "wt")

@app.route('/post', methods =['POST'])
def post():
        if request.method == 'POST':
            print(request.data)
            datastr = str(request.data)
            dataclean = datastr[1:].replace('\\r', '').strip("'").replace('\\n','\n')
            with open("PLAYERGATHERDATA.txt", "wt") as SERVERDATA:
                SERVERDATA.write(dataclean)
            return 'FINISHED'
            
if __name__ == '__main__':
    app.run(port=8000)
    #host = '172.16.0.2',


# In[ ]:


SERVERDATA.close()

