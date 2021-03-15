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

@app.route('/plugin/detect/')
def plugindetect():
    return 'plugindetect'

@app.route('/plugin/massdetect/')
def pluginmassdetect():
    return 'pluginmassdetect'

@app.route('/plugin/send/')
def pluginsend():
    return 'pluginsend'

@app.route('/plugin/heatmap/')
def pluginheatmap():
    return 'pluginheatmap'

@app.route('/plugin/report/')
def pluginreport():
    return 'pluginreport'

@app.route('/plugin/beta/')
def pluginbeta():
    return 'pluginbeta'

@app.route('/stats/')
def stats():
    return 'stats'

@app.route('/lookup/')
def lookup():
    return 'lookup'

@app.route('/graphs/')
def graphs():
    return 'graphs'

@app.route('/map/')
def map():
    return 'map'

@app.route('/contact/')
def contact():
    return 'contact'

if __name__ == '__main__':
   serve(app, host='127.0.0.1', port=5000)