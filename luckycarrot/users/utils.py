import os
import secrets
from PIL import Image
from flask import url_for, current_app
from flask_mail import Message
from luckycarrot import mail
from flask_login import current_user

def save_profile_picture(form_picture):
    random_hex = secrets.token_hex(8)
    f_name, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pictures', picture_fn)

    # Resize picture
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    
    prev_picture = os.path.join(current_app.root_path, 'static/profile_pictures', current_user.image_file)
    if os.path.exists(prev_picture) and current_user.image_file != 'default.png':
        os.remove(prev_picture)

    return picture_fn


def send_reset_email(user):
    token = user.get_reset_token()

    msg = Message('Password Reset Request', sender='theluckycarrot1@gmail.com', recipients=[user.email])

    msg.body = f"""To complete your password reset, visit the link below.

{url_for('users.reset_token', token=token, _external=True)}

If you did not request a password reset, then ignore this email and your password will not be changed.
"""
    mail.send(msg)
