from flask import (
    render_template,
    request,
    redirect,
    url_for,
    Blueprint,
    send_from_directory,
)
from routes import *
from werkzeug.utils import secure_filename
from models.user import User
from config import user_file_director
import os


def allow_file(filename):
    suffix = filename.split('.')[-1]
    from config import accept_user_file_type
    return suffix in accept_user_file_type


main = Blueprint('profile', __name__)


@main.route("/")
def index():
    print("执行")
    u = current_user()
    return render_template("profile/profile.html", user=u)


@main.route("/addimg", methods=["POST"])
def add_img():
    u = current_user()

    if u is None:
        return redirect(url_for("index.id"))

    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)

    if allow_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(user_file_director, filename))
        u.portrait = filename
        u.save()

    return redirect(url_for(".index"))


@main.route("/uploads/<filename>")
def uploads(filename):
    return send_from_directory(user_file_director, filename)
