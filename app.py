from flask import jsonify, render_template_string
from waitress import serve
import requests
import datetime
import os
import logging
#import logging
# custom

from mysite.tokens import app_token
from mysite.dashboard import dashboard
from plugin.plugin_stats import plugin_stats
from plugin.detect import detect
from Config import app, sched
from highscores import run_hiscore

import sys
sys.stdout = open('error.log', 'a')

logging.FileHandler(filename="error.log", mode='a')
logging.basicConfig(filename='error.log', level=logging.DEBUG)
logger = logging.getLogger()
print = logger.info

app.register_blueprint(plugin_stats)
app.register_blueprint(detect)
app.register_blueprint(app_token)
app.register_blueprint(dashboard)

if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
    started = True
    sched.add_job(run_hiscore, 'interval', minutes=10, start_date=datetime.date.today())
    sched.start()


@app.errorhandler(404)
def page_not_found(e):
    print(e)
    app.logger.warning(e)
    return "<h1>404</h1><p>The resource could not be found.</p>", 404


@app.route("/")
def hello():

    data = {'welcome': 'test', 'job': started}
    return jsonify(data)

@app.route("/log")
def print_log():
    with open("error.log", "r") as f:
        content = f.read()
        return render_template_string("<pre>{{ content }}</pre>", content=content)



if __name__ == '__main__':
    app.run(port=5000, debug=True, use_reloader=False)
    # serve(app, host='127.0.0.1', port=5000, debug=True)
