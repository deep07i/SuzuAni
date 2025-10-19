from flask import (Blueprint, flash, jsonify, redirect, render_template,
                   request, url_for)
from flask_login import current_user, login_required, login_user, logout_user
from suzuani import bcrypt, db
from suzuani.forms import (CommentForm, LoginForm, OTPForm, ProfileUpdateForm,
                           RegistrationForm, RequestResetForm,
                           ResetPasswordForm)
from suzuani.models import (Anime, Banner, Category, Comment, Manga,
                            MangaChapter, User, MusicCategory, Song)
from suzuani.utils import (generate_otp, save_picture, send_otp_email,
                           send_reset_email)

main = Blueprint('main', __name__)

@main.route("/")
@login_required
def index():
    banners = Banner.query.filter_by(banner_type='anime').limit(4).all()
    categories = Category.query.all()
    animes_by_category = {cat: Anime.query.filter_by(category=cat).limit(10).all() for cat in categories}
    return render_template('index.html', banners=banners, animes_by_category=animes_by_category)

@main.route("/mangas")
@login_required
def mangas():
    banners = Banner.query.filter_by(banner_type='manga').limit(4).all()
    categories = Category.query.all()
    mangas_by_category = {cat: Manga.query.filter_by(category=cat).limit(10).all() for cat in categories}
    return render_template('mangas.html', banners=banners, mangas_by_category=mangas_by_category)

@main.route("/music")
@login_required
def music():
    banners = Banner.query.filter_by(banner_type='music').limit(4).all()
    music_categories = MusicCategory.query.all()
    songs_by_category = {cat: Song.query.filter_by(category=cat).limit(15).all() for cat in music_categories}
    return render_template('music.html', songs_by_category=songs_by_category, banners=banners)

@main.route("/search")
@login_required
def search():
    query = request.args.get('q', '').strip()
    anime_results, manga_results, song_results = [], [], []
    if query:
        search_term = f'%{query}%'
        anime_results = Anime.query.filter(Anime.title.ilike(search_term)).all()
        manga_results = Manga.query.filter(Manga.title.ilike(search_term)).all()
        song_results = Song.query.filter(Song.title.ilike(search_term) | Song.artist.ilike(search_term)).all()
    return render_template('search.html', query=query, animes=anime_results, mangas=manga_results, songs=song_results)

@main.route("/anime/<int:anime_id>", methods=['GET', 'POST'])
@login_required
def movie_details(anime_id):
    anime = Anime.query.get_or_404(anime_id)
    form = CommentForm()
    if form.validate_on_submit():
        if Comment.query.filter_by(user_id=current_user.id, anime_id=anime.id).first():
            flash('You have already commented on this anime.', 'info')
        else:
            comment = Comment(text=form.text.data, author=current_user, anime=anime)
            db.session.add(comment)
            db.session.commit()
            flash('Your comment has been posted!', 'success')
        return redirect(url_for('main.movie_details', anime_id=anime.id))
    comments = Comment.query.filter_by(anime_id=anime.id).order_by(Comment.id.desc()).all()
    return render_template('movie_details.html', title=anime.title, anime=anime, form=form, comments=comments)

@main.route("/manga/<int:manga_id>")
@login_required
def manga_details(manga_id):
    manga = Manga.query.get_or_404(manga_id)
    return render_template('manga_details.html', title=manga.title, manga=manga)

@main.route("/manga/<int:manga_id>/read/<int:chapter_id>")
@login_required
def manga_reader(manga_id, chapter_id):
    chapter = MangaChapter.query.get_or_404(chapter_id)
    return render_template('manga_reader.html', chapter=chapter, pages=chapter.pages)

@main.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated: return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        otp = generate_otp()
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, otp=otp)
        db.session.add(user)
        db.session.commit()
        try:
            send_otp_email(user)
            flash(f'An OTP has been sent to {user.email}. Please verify.', 'info')
        except Exception as e:
            print(f"EMAIL SENDING FAILED: {e}")
            flash('Registration successful, but could not send OTP email.', 'warning')
        return redirect(url_for('main.verify_otp', user_id=user.id))
    return render_template('register.html', title='Register', form=form)

@main.route("/verify_otp/<int:user_id>", methods=['GET', 'POST'])
def verify_otp(user_id):
    user = User.query.get_or_404(user_id)
    if user.is_verified: return redirect(url_for('main.login'))
    form = OTPForm()
    if form.validate_on_submit():
        if user.otp == form.otp.data:
            user.is_verified = True
            user.otp = None
            db.session.commit()
            flash('Your account has been verified! You can now log in.', 'success')
            return redirect(url_for('main.login'))
        else:
            flash('Invalid OTP. Please try again.', 'danger')
    return render_template('verify_otp.html', title='Verify OTP', form=form)

@main.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated: return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            if user.is_verified:
                login_user(user, remember=form.remember.data)
                next_page = request.args.get('next')
                return redirect(next_page or url_for('main.index'))
            else:
                flash('Please verify your email address before logging in.', 'warning')
                return redirect(url_for('main.verify_otp', user_id=user.id))
        else:
            flash('Login Unsuccessful. Please check email and password.', 'danger')
    return render_template('login.html', title='Login', form=form)

@main.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.login'))

@main.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated: return redirect(url_for('main.index'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        try:
            send_reset_email(user)
            flash('An email has been sent with instructions to reset your password.', 'info')
        except Exception as e:
            print(f"EMAIL SENDING FAILED: {e}")
            flash('Could not send password reset email. Please contact support.', 'danger')
        return redirect(url_for('main.login'))
    return render_template('forgot_password.html', title='Reset Password', form=form)

@main.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated: return redirect(url_for('main.index'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token.', 'warning')
        return redirect(url_for('main.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You can now log in.', 'success')
        return redirect(url_for('main.login'))
    return render_template('reset_password.html', title='Reset Password', form=form)
    
@main.route("/about")
def about():
    return render_template('about.html', title='About Us')

@main.route("/support")
def support():
    return render_template('support.html', title='Support')

@main.route("/profile", methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileUpdateForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_filename = save_picture(form.picture.data, path='uploads/profiles', output_size=(150, 150))
            current_user.profile_image = f'uploads/profiles/{picture_filename}'
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('main.profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    profile_image = url_for('static', filename=current_user.profile_image)
    return render_template('profile.html', title='Profile', image_file=profile_image, form=form)

@main.route("/history")
@login_required
def history():
    return render_template('history.html', title='Liked Content')

@main.route("/like_anime/<int:anime_id>", methods=['POST'])
@login_required
def like_anime(anime_id):
    anime = Anime.query.get_or_404(anime_id)
    if anime in current_user.liked_animes:
        current_user.liked_animes.remove(anime)
        status = 'unliked'
    else:
        current_user.liked_animes.append(anime)
        status = 'liked'
    db.session.commit()
    return jsonify({'status': status})

@main.route("/like_manga/<int:manga_id>", methods=['POST'])
@login_required
def like_manga(manga_id):
    manga = Manga.query.get_or_404(manga_id)
    if manga in current_user.liked_mangas:
        current_user.liked_mangas.remove(manga)
        status = 'unliked'
    else:
        current_user.liked_mangas.append(manga)
        status = 'liked'
    db.session.commit()
    return jsonify({'status': status})

@main.route("/comment/<int:comment_id>/delete", methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if comment.author != current_user: return redirect(url_for('main.index'))
    redirect_url = url_for('main.movie_details', anime_id=comment.anime_id) if comment.anime_id else url_for('main.manga_details', manga_id=comment.manga_id)
    db.session.delete(comment)
    db.session.commit()
    flash('Your comment has been deleted.', 'success')
    return redirect(redirect_url)