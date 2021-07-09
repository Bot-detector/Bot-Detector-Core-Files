
from waitress import serve

# custom
from Config import api, app, flask_port
from Routes.player import Player


api.add_resource(Player, '/player')


if __name__ == '__main__':
    # app.run(port=flask_port, debug=True, use_reloader=False)
    serve(app, host='127.0.0.1', port=flask_port)
