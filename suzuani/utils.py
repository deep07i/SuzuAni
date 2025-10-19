import os
import secrets
from PIL import Image
from flask import url_for, current_app, render_template
from flask_mail import Message
from suzuani import mail

def save_picture(form_picture, path, output_size=(500, 500)):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static', path, picture_fn)
    os.makedirs(os.path.dirname(picture_path), exist_ok=True)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn

def generate_otp():
    return str(secrets.randbelow(900000) + 100000)

def send_otp_email(user):
    msg = Message('SuzuAni - Verify Your Email Address',
                  sender=('SuzuAni', current_app.config['MAIL_USERNAME']),
                  recipients=[user.email])
    msg.html = render_template('email/otp.html', user=user)
    try:
        mail.send(msg)
    except Exception as e:
        print(f"Error sending email: {e}")

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('SuzuAni - Password Reset Request',
                  sender=('SuzuAni', current_app.config['MAIL_USERNAME']),
                  recipients=[user.email])
    msg.html = render_template('email/reset.html', user=user, token=token)
    try:
        mail.send(msg)
    except Exception as e:
        print(f"Error sending email: {e}")