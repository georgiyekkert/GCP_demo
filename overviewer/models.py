from flask import Flask
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Twitch(db.Model):
    __tablename__ = 'twitch_channels'

    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(255))
    streamUrl = db.Column(db.String(255))
    profileImgUrl = db.Column(db.String(255))
    description = db.Column(db.String(4096))

    def __repr__(self):
        return "<Channel(author=%s)" % self.author


class YouTube(db.Model):
    __tablename__ = "youtube_videos"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    videoUrl = db.Column(db.String(255))
    description = db.Column(db.String(4096))

    def __repr__(self):
        return "<Video(name=%s, url=%s)" % (self.name, self.videoUrl)


class Memes(db.Model):
    __tablename__ = "memes"
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(255))
    author = db.Column(db.String(255))
    date = db.Column(db.String(255))
    labels = db.Column(db.String(255))

    def __repr__(self):
        return "<Meme(url=%s)" % self.url


def init_app(app):
    app.config.setdefault('SQLALCHEMY_TRACK_MODIFICATIONS', False)
    db.init_app(app)


def from_sql(row):
    data = row.__dict__.copy()
    data['id'] = row.id
    data.pop('_sa_instance_state')
    return data


def create(data, cls):
    item = cls(**data)
    db.session.add(item)
    db.session.commit()
    return from_sql(item)


def update(data, id, cls):
    item = cls.query.get(id)
    for k, v in data.items():
        setattr(item, k, v)
    db.session.commit()
    return from_sql(item)


def get(id, cls):
    item = cls.query.get(id)
    return from_sql(item)


def _create_database():
    app = Flask(__name__)
    app.config.from_pyfile('config.py')
    init_app(app)
    with app.app_context():
        db.create_all()


if __name__ == '__main__':
    _create_database()
