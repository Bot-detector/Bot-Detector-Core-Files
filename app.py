from time import sleep
from flask import jsonify, render_template_string, redirect
from waitress import serve
import datetime as dt
import os
import logging
# custom
from Config import flask_port

import scraper.hiscoreScraper as scraper
from mysite.tokens import app_token
from mysite.dashboard import dashboard
from plugin.plugin_stats import plugin_stats
from plugin.detect import detect
from Config import app, sched
from mysite.predictions import app_predictions
from Predictions import model
from discord.discord import discord

logging.FileHandler(filename="error.log", mode='a')
logging.basicConfig(filename='error.log', level=logging.DEBUG)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("apscheduler").setLevel(logging.WARNING)
logging.getLogger('flask_cors').setLevel(logging.WARNING)

# logger = logging.getLogger()

app.register_blueprint(plugin_stats)
app.register_blueprint(detect)
app.register_blueprint(app_token)
app.register_blueprint(dashboard)
app.register_blueprint(app_predictions)
app.register_blueprint(discord)

if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
    started = True
    today18h = dt.datetime.combine(dt.date.today(), dt.datetime.min.time())
    today18h = today18h + dt.timedelta(hours=18)

    sched.add_job(scraper.run_scraper, 'interval', minutes=1, start_date=dt.date.today(), name='run_hiscore', max_instances=15, coalesce=True)
    
    sched.add_job(model.save_model,trigger='interval', days=1, start_date=today18h ,args=[50], replace_existing=True, name='save_model')
    sched.add_job(model.train_model ,args=[50], replace_existing=True, name='save_model') # on startup
    
    for job in sched.get_jobs():
        logging.debug(f'    Job: {job.name}, {job.trigger}, {job.func}')
        print(f'    Job: {job.name}, {job.trigger}, {job.func}')

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

@app.route("/hiscorescraper")
def hiscorescraper():
    sched.add_job(scraper.run_scraper, name='run_hiscore', max_instances=10, coalesce=True)
    for job in sched.get_jobs():
        logging.debug(f'    Job: {job.name}, {job.trigger}, {job.func}')
        print(f'    Job: {job.name}, {job.trigger}, {job.func}')
    return redirect('/log')

if __name__ == '__main__':
    app.run(port=flask_port, debug=True, use_reloader=False)
    # serve(app, host='127.0.0.1', port=flask_port, debug=True)
