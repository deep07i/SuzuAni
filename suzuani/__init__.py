import os
import json
from flask import Flask, url_for
from urllib.parse import urlparse, parse_qs
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_admin import Admin
from suzuani.config import Config

# Extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'main.login'
login_manager.login_message_category = 'info'
mail = Mail()
admin = Admin(name='SuzuAni Admin', template_mode='bootstrap3', base_template='admin/master.html')

def get_embed_url(watch_link):
    if not watch_link: return ""
    parsed_url = urlparse(watch_link)
    if 'youtube.com' in parsed_url.hostname:
        query = parse_qs(parsed_url.query)
        if 'v' in query: return f"https://www.youtube.com/embed/{query['v'][0]}"
    elif 'youtu.be' in parsed_url.hostname:
        return f"https://www.youtube.com/embed/{parsed_url.path[1:]}"
    if "drive.google.com" in watch_link:
        file_id = watch_link.split("/")[-2]
        return f"https://drive.google.com/file/d/{file_id}/preview"
    return watch_link

def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

    upload_path = os.path.join(app.root_path, 'static', 'uploads')
    required_folders = ['banners', 'covers', 'episodes', 'manga_pages', 'posters', 'profiles', 'songs']
    for folder in required_folders:
        os.makedirs(os.path.join(upload_path, folder), exist_ok=True)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    admin.init_app(app)

    from suzuani.models import Song
    @app.context_processor
    def inject_utilities_and_playlist():
        try:
            all_songs = Song.query.all()
            playlist = [{'id': song.id, 'title': song.title, 'artist': song.artist, 'cover_url': url_for('static', filename=song.cover_url), 'song_url': url_for('static', filename=song.song_url)} for song in all_songs]
            playlist_json = json.dumps(playlist)
        except Exception:
            playlist_json = "[]"
        return dict(get_embed_url=get_embed_url, playlist_json=playlist_json)

    from suzuani.models import User, Category, Anime, Episode, Manga, MangaChapter, MangaPage, Banner, Comment, MusicCategory
    from suzuani.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from suzuani.admin_panel import (SecureModelView, UserAdminView, AnimeAdminView, MangaAdminView, EpisodeAdminView, MangaChapterAdminView, MangaPageAdminView, BannerAdminView, MusicCategoryAdminView, SongAdminView)
    
    admin.add_view(UserAdminView(User, db.session, endpoint='user_admin'))
    admin.add_view(SecureModelView(Category, db.session, endpoint='category_admin'))
    admin.add_view(AnimeAdminView(Anime, db.session, endpoint='anime_admin'))
    admin.add_view(EpisodeAdminView(Episode, db.session, endpoint='episode_admin'))
    admin.add_view(MangaAdminView(Manga, db.session, endpoint='manga_admin'))
    admin.add_view(MangaChapterAdminView(MangaChapter, db.session, endpoint='mangachapter_admin'))
    admin.add_view(MangaPageAdminView(MangaPage, db.session, endpoint='mangapage_admin'))
    admin.add_view(BannerAdminView(Banner, db.session, endpoint='banner_admin'))
    admin.add_view(SecureModelView(Comment, db.session, endpoint='comment_admin'))
    admin.add_view(MusicCategoryAdminView(MusicCategory, db.session, category="Music", endpoint="music_category_admin"))
    admin.add_view(SongAdminView(Song, db.session, category="Music", endpoint="song_admin"))
    
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            hashed_password = bcrypt.generate_password_hash('admin123').decode('utf-8')
            admin_user = User(username='admin', email='admin@suzuani.com', password=hashed_password, is_admin=True, is_verified=True)
            db.session.add(admin_user)
            db.session.commit()

    return app