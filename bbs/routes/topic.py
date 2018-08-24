from flask import (
    render_template,
    request,
    redirect,
    url_for,
    Blueprint,
)

from routes import *

from models.topic import Topic
from models.board import Board

main = Blueprint('topic', __name__)


@main.route("/")
def index():
    query = request.args
    board_id = int(query.get('tab', -1))
    if board_id == -1 or board_id == 0:
        ms = Topic.all()
    else:
        ms = Topic.find_all(board_id=board_id)
    bs = Board.all()
    # print("ms[0] debug", ms[0].replies)
    return render_template("topic/index.html", ms=ms, bs=bs)


@main.route('/<int:topic_id>')
def detail(topic_id):
    m = Topic.get(topic_id)
    return render_template("topic/detail.html", topic=m)


@main.route("/add", methods=["POST"])
def add():
    form = request.form
    u = current_user()
    m = Topic.new(form, user_id=u.id)
    print("wori", form.get('board_id', "no"))
    return redirect(url_for(".detail", topic_id=m.id))


@main.route("/new")
def new():
    bs = Board.all()
    return render_template("topic/new.html", bs=bs)
