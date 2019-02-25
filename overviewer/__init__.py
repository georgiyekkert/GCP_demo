
from flask import Flask, session, json, redirect
import httplib2
from .models import init_app
from .views import blueprint, oauth2
from .tasks import cron


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.py')

    with app.app_context():
        init_app(app)

    app.register_blueprint(blueprint, url_prefix='/')
    app.register_blueprint(cron, url_prefix='/')

    oauth2.init_app(
        app,
        scopes=['email', 'profile'],
        authorize_callback=request_user_info)

    @app.errorhandler(404)
    def page_not_found():
        return """Couldn't find requested page""", 404

    @app.errorhandler(500)
    def server_error():
        return """An internal error occurred.""", 500

    @app.route('/logout')
    def logout():
        del session['profile']
        session.modified = True
        oauth2.storage.delete()
        return redirect('/')

    return app


def request_user_info(credentials):
    http = httplib2.Http()
    credentials.authorize(http)
    resp, content = http.request('https://www.googleapis.com/plus/v1/people/me')
    if resp.status != 200:
        return None
    session['profile'] = json.loads(content.decode('utf-8'))
