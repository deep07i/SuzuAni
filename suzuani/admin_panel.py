import os.path as op
from flask import redirect, request, url_for
from flask_admin.contrib.sqla import ModelView
from flask_admin.form.upload import FileUploadField, ImageUploadField
from flask_admin.form.fields import Select2Field
from flask_login import current_user
from wtforms.validators import DataRequired

base_path = op.join(op.dirname(__file__), 'static')

class SecureModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('main.login', next=request.url))

class UserAdminView(SecureModelView):
    column_exclude_list = ['password']
    form_excluded_columns = ['password', 'comments', 'liked_animes', 'liked_mangas', 'otp', 'messages']
    form_extra_fields = {
        'profile_image': ImageUploadField(
            'Profile Image', base_path=base_path, relative_path='uploads/profiles/', thumbnail_size=(100, 100, True)
        )
    }

class AnimeAdminView(SecureModelView):
    form_extra_fields = {
        'poster_url': ImageUploadField(
            'Poster', base_path=base_path, relative_path='uploads/posters/', thumbnail_size=(100, 150, True)
        )
    }
    column_searchable_list = ['title']
    column_filters = ['release_year', 'rating', 'category']

class MangaAdminView(SecureModelView):
    form_extra_fields = {
        'poster_url': ImageUploadField(
            'Poster', base_path=base_path, relative_path='uploads/posters/', thumbnail_size=(100, 150, True)
        )
    }
    column_searchable_list = ['title']
    column_filters = ['release_year', 'rating', 'category']

class EpisodeAdminView(SecureModelView):
    form_extra_fields = {
        'thumbnail_url': ImageUploadField(
            'Thumbnail', base_path=base_path, relative_path='uploads/episodes/', thumbnail_size=(160, 90, True)
        )
    }
    column_list = ('title', 'anime', 'watch_link')
    form_columns = ('anime', 'title', 'thumbnail_url', 'watch_link')

class MangaChapterAdminView(SecureModelView):
    column_list = ('title', 'manga')
    form_columns = ('manga', 'title')

class MangaPageAdminView(SecureModelView):
    form_extra_fields = {
        'image_url': ImageUploadField(
            'Page Image', base_path=base_path, relative_path='uploads/manga_pages/'
        )
    }
    column_list = ('chapter', 'page_number')
    form_columns = ('chapter', 'page_number', 'image_url')

class BannerAdminView(SecureModelView):
    form_extra_fields = {
        'image_url': ImageUploadField(
            'Banner Image', base_path=base_path, relative_path='uploads/banners/', thumbnail_size=(200, 100, True), validators=[DataRequired()]
        )
    }
    form_overrides = {'banner_type': Select2Field}
    form_args = {
        'banner_type': {
            'label': 'Banner Type',
            'choices': [('anime', 'Anime'), ('manga', 'Manga'), ('music', 'Music')],
            'validators': [DataRequired()]
        }
    }
    column_list = ('banner_type', 'anime', 'manga')
    form_columns = ('banner_type', 'image_url', 'anime', 'manga')
    form_widget_args = {
        'anime': {'description': 'Agar banner type "Anime" hai to hi ise select karein.'},
        'manga': {'description': 'Agar banner type "Manga" hai to hi ise select karein.'}
    }

class MusicCategoryAdminView(SecureModelView):
    form_columns = ['name']
    column_searchable_list = ['name']

class SongAdminView(SecureModelView):
    form_extra_fields = {
        'cover_url': ImageUploadField(
            'Cover Image', base_path=base_path, relative_path='uploads/covers/', thumbnail_size=(100, 100, True), validators=[DataRequired()]
        ),
        'song_url': FileUploadField(
            'MP3 File', base_path=base_path, relative_path='uploads/songs/', allowed_extensions=['mp3', 'wav', 'ogg'], validators=[DataRequired()]
        )
    }
    column_list = ('title', 'artist', 'category')
    form_columns = ('category', 'title', 'artist', 'cover_url', 'song_url')
    column_searchable_list = ('title', 'artist')
    column_filters = ('category', 'artist')