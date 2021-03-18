from flask import jsonify
from waitress import serve
import requests
#import logging
# custom

from mysite.tokens import app_token
from mysite.dashboard import dashboard
from plugin.plugin_stats import plugin_stats
from plugin.detect import detect
from Config import app

app.register_blueprint(plugin_stats)
app.register_blueprint(detect)
app.register_blueprint(app_token)
app.register_blueprint(dashboard)



@app.errorhandler(404)
def page_not_found(e):
    print(e)
    app.logger.warning(e)
    return "<h1>404</h1><p>The resource could not be found.</p>", 404


@app.route("/")
def hello():

    data = {'welcome': 'test'}
    return jsonify(data)

# Hacky testing
@app.route('/test')
def test():
    # expect list of dicts
    detect = [{
        'reporter': 'extreme4all',
        'reported': 'farriic',
        'region_id': '0',
        'x':'0',
        'y':'0',
        'z':'0',
        'ts':'0'
    }]
    requests.post('http://localhost:5000/plugin/detect/0', json=detect)
    requests.post('http://localhost:5000/plugin/detect/1', json=detect)
    return jsonify({'ok':'ok'})

if __name__ == '__main__':
    app.run(port=5000, debug=True)
    #serve(app, host='127.0.0.1', port=5000)
