
from flask import Flask
from .models import init_app
from .views import blueprint
from .tasks import cron


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.py')

    with app.app_context():
        init_app(app)

    app.register_blueprint(blueprint, url_prefix='/')
    app.register_blueprint(cron, url_prefix='/')

    @app.errorhandler(404)
    def page_not_found():
        return """Couldn't find requested page""", 404

    @app.errorhandler(500)
    def server_error():
        return """An internal error occurred.""", 500

    return app


