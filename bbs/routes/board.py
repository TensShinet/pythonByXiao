from flask import (
    render_template,
    request,
    redirect,
    url_for,
    Blueprint,
)

from routes import *

from models.board import Board


main = Blueprint('broad', __name__)


@main.route("/admin")
def index():
    return render_template("board/admin.html")


@main.route("/add", methods=["POST"])
def add():
    form = request.form
    u = current_user()
    b_len = len(Board.all())
    m = Board.new(form, board_id=b_len+1)
    return redirect(url_for("topic.index", bs=m))

