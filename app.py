from flask import Flask, jsonify
from waitress import serve

app = Flask(__name__)


@app.errorhandler(404)
def page_not_found(e):
   return "<h1>404</h1><p>The resource could not be found.</p>", 404

@app.route("/")
def hello():
   data = {'welcome': 'test'}
   return jsonify(data)

if __name__ == '__main__':
   serve(app, host='127.0.0.1', port=5000)