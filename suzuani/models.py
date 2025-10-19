from flask import current_app
from flask_login import UserMixin
from itsdangerous import URLSafeTimedSerializer as Serializer
from suzuani import db, login_manager
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

anime_likes = db.Table('anime_likes',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('anime_id', db.Integer, db.ForeignKey('anime.id'), primary_key=True)
)

manga_likes = db.Table('manga_likes',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('manga_id', db.Integer, db.ForeignKey('manga.id'), primary_key=True)
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    profile_image = db.Column(db.String(40), nullable=False, default='uploads/profiles/default.jpg')
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    otp = db.Column(db.String(6), nullable=True)
    liked_animes = db.relationship('Anime', secondary=anime_likes, backref='liked_by')
    liked_mangas = db.relationship('Manga', secondary=manga_likes, backref='liked_by')
    comments = db.relationship('Comment', backref='author', lazy=True)

    def get_reset_token(self):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id})

    @staticmethod
    def verify_reset_token(token, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token, max_age=expires_sec)['user_id']
        except:
            return None
        return User.query.get(user_id)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    animes = db.relationship('Anime', backref='category', lazy=True)
    mangas = db.relationship('Manga', backref='category', lazy=True)
    def __repr__(self): return self.name

class Anime(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    poster_url = db.Column(db.String(100), nullable=False, default='default_poster.jpg')
    description = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Float, default=0.0)
    release_year = db.Column(db.Integer, nullable=False)
    views = db.Column(db.Integer, default=0)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    episodes = db.relationship('Episode', backref='anime', lazy=True, cascade="all, delete-orphan")
    comments = db.relationship('Comment', backref='anime', lazy=True, cascade="all, delete-orphan")

class Episode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    thumbnail_url = db.Column(db.String(100), nullable=False, default='default_thumb.jpg')
    watch_link = db.Column(db.String(200), nullable=False)
    anime_id = db.Column(db.Integer, db.ForeignKey('anime.id'), nullable=False)

class Manga(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    poster_url = db.Column(db.String(100), nullable=False, default='default_poster.jpg')
    description = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Float, default=0.0)
    release_year = db.Column(db.Integer, nullable=False)
    views = db.Column(db.Integer, default=0)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    chapters = db.relationship('MangaChapter', backref='manga', lazy=True, cascade="all, delete-orphan")
    comments = db.relationship('Comment', backref='manga', lazy=True, cascade="all, delete-orphan")

class MangaChapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    manga_id = db.Column(db.Integer, db.ForeignKey('manga.id'), nullable=False)
    pages = db.relationship('MangaPage', backref='chapter', lazy=True, cascade="all, delete-orphan", order_by="MangaPage.page_number")

class MangaPage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    page_number = db.Column(db.Integer, nullable=False)
    image_url = db.Column(db.String(100), nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('manga_chapter.id'), nullable=False)

class Banner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(100), nullable=False)
    banner_type = db.Column(db.String(10), nullable=False)
    anime_id = db.Column(db.Integer, db.ForeignKey('anime.id'), nullable=True)
    manga_id = db.Column(db.Integer, db.ForeignKey('manga.id'), nullable=True)
    anime = db.relationship('Anime', backref='banner')
    manga = db.relationship('Manga', backref='banner')

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    anime_id = db.Column(db.Integer, db.ForeignKey('anime.id'), nullable=True)
    manga_id = db.Column(db.Integer, db.ForeignKey('manga.id'), nullable=True)

class MusicCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    songs = db.relationship('Song', backref='category', lazy=True)
    def __repr__(self): return self.name

class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    artist = db.Column(db.String(100), nullable=False)
    cover_url = db.Column(db.String(100), nullable=False, default='default_cover.jpg')
    song_url = db.Column(db.String(100), nullable=False)
    music_category_id = db.Column(db.Integer, db.ForeignKey('music_category.id'), nullable=False)