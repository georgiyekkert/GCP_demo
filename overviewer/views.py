from .models import Twitch, YouTube, create, Memes
from flask import Blueprint, render_template, request, session, redirect, url_for
from sqlalchemy.sql.expression import func
from .storage import upload_file
from oauth2client.contrib.flask_util import UserOAuth2
import datetime
from .queue_tasks import create_queue, annotate

blueprint = Blueprint('videos', __name__)
oauth2 = UserOAuth2()


@blueprint.route("/")
def list_main():
    twitch = Twitch.query.filter_by(description="live").order_by(func.rand()).all()
    if len(twitch) > 1:
        twitch = Twitch.query.filter_by(description="live").order_by(func.rand()).limit(2).all()
    else:
        twitch = Twitch.query.order_by(func.rand()).limit(2).all()

    youtube = YouTube.query.order_by(func.rand()).limit(2).all()
    return render_template("main.html", tw=twitch, yt=youtube)


@blueprint.route("/twitch")
def list_twitch():
    twitch = Twitch.query.order_by(func.rand()).all()
    return render_template("twitch.html", tw=twitch)


@blueprint.route("/youtube")
def list_youtube():
    youtube = YouTube.query.order_by(func.rand()).all()
    return render_template("youtube.html", yt=youtube)


@blueprint.route("/users_memes")
def list_memes():
    memes = Memes.query.order_by(func.rand()).all()
    return render_template("memes.html", memes=memes)


@blueprint.route('/add', methods=['GET', 'POST'])
@oauth2.required
def add():
    if request.method == 'POST':
        data = request.form.to_dict(flat=True)

        file = request.files.get('image')
        image_url = upload_file(file.read(), file.filename, file.content_type)

        if image_url:
            data['url'] = image_url
            data['author'] = session['profile']['displayName']
            data['date'] = datetime.datetime.today().strftime('%Y-%m-%d')

        obj = create(data, Memes)

        queue = create_queue(name="image")
        queue.enqueue(annotate, obj['id'])

        return redirect(url_for('.list_memes'))

    return render_template("upload_form.html", action="Add")


