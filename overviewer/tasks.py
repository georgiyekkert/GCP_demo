from .models import Twitch, YouTube, from_sql, create, update
from .config import user_id, client_id, yt_id, playlist_id
from flask import Blueprint, request
import requests


cron = Blueprint('cron', __name__)


@cron.route("/crontw_following")
def cron_tw():
    if "X-Appengine-Cron" in request.headers:
        following_streams = requests.get(url="https://api.twitch.tv/helix/users/follows?from_id=%s" % user_id +
                                             "&first=100",  headers={"Client-ID": "%s" % client_id}).json()["data"]
        known_streams = list(map(from_sql, Twitch.query.all()))

        if len(following_streams) == len(known_streams):
            return "Up to date", 200
        else:
            update_db_with_new_streams(set([i["to_name"].lower() for i in following_streams]) - set([i['author'].lower() for i in known_streams]))
            return 'Updated', 200
    return "Not Updated"


@cron.route("/crontw_live")
def check_tw_live():
    if "X-Appengine-Cron" in request.headers:
        followed = list(map(from_sql, Twitch.query.all()))

        ids = [i['author'] for i in followed]

        followed_alive = requests.get(url="https://api.twitch.tv/helix/streams?%s" % make_request_string(ids, "user_login") +
                                'first=100', headers={"Client-ID": "%s" % client_id}).json()['data']

        followed_alive = [user["user_name"].lower() for user in followed_alive]

        for stream in followed:
            if stream["author"] in followed_alive:
                data = {"description": "live"}
                update(data, stream['id'], Twitch)
            else:
                data = {"description": "offline"}
                update(data, stream['id'], Twitch)
        return 'Updated', 200
    return 'Not Updated'


@cron.route("/cronyt")
def cron_yt():
    if "X-Appengine-Cron" in request.headers:
        all_videos = requests.get("https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&maxResults=50&playlistId=%s&key=%s"
                         % (playlist_id, yt_id)).json()["items"]
        known_videos = list(map(from_sql, YouTube.query.all()))

        if len(known_videos) == len(all_videos):
            return "Up to date", 200
        else:
            new = {video["snippet"]["title"]: video["snippet"]["resourceId"]["videoId"] for video in all_videos}
            for known in known_videos:
                if known['name'] in new.keys():
                    new.pop(known['name'])

            update_db_with_new_videos(new)
            return 'Updated', 200
    return "Not Updated"


def update_db_with_new_streams(new_streams):
    streams_info = requests.get(url="https://api.twitch.tv/helix/users?%s" % make_request_string(new_streams, "login"),
                     headers={"Client-ID": "%s" % client_id}).json()['data']
    for stream in streams_info:
        data = {"author": stream['login'], "streamUrl": "https://player.twitch.tv/?channel=" + stream['display_name'],
                "profileImgUrl": stream['profile_image_url']}
        create(data, cls=Twitch)


def update_db_with_new_videos(new_videos):
    for video_name, url in new_videos.items():
        data = {"name": video_name, "videoUrl": "https://www.youtube.com/embed/"+url}
        create(data, cls=YouTube)


def make_request_string(to_proceed, locator):
    result = ''
    for i in to_proceed:
        result = result+"%s=" % locator+i+'&'
    return result
