from .models import Twitch, YouTube
from flask import Blueprint, render_template
from sqlalchemy.sql.expression import func

blueprint = Blueprint('videos', __name__)


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

