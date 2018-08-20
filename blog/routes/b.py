from flask import (
    render_template,
    request,
    redirect,
    url_for,
    Blueprint,
)

from models.b import (
    Blog,
    BlogComment,
)

# todo 搞懂这句话是什么意思
main = Blueprint('blog', __name__)
'''
1. 拆分有哪些页面
    1. 显示所有文章的页面
        1.1 最上面是一个 新建文章的 link 
        1.2 下面是所有文章的列表 
    2. 显示 单文章 的页面
        2.1 显示 内容 标题 作者
    3. 新建 文章 的页面
        3.1 三个 input 窗口
2. 组织有哪些数据，把数据的操作实现
    1. Blog 数据
        1. id int
        2. author
        3. content
        4. created_time
    2. Blog 的方法有哪些
        1. 创建
        2. 根据 id 拿到一个 blog
    3. BlogComment
        1. id
        2. author
        3. comment
        4. create_time
        5.blog_id
    4. BlogComment 方法
        1.new
        2.blog_id find
3. 逻辑 产品经理，
    1. / 
        显示 新建文章
        显示所有文章
    2. /new
        显示创建页面
    3. /add
        创建一个博客
    4. /comment/add
        增加一个 comment
4. 开始实现代码
5. 剩下的部分一点点补全
6. 美化页面 视觉
7. 交互细节 交互
'''


@main.route("/")
def index():
    all_blog = Blog.all()
    return render_template('blog_index.html', blogs=all_blog)


@main.route("/add", methods=["POST"])
def add():
    form = request.form
    Blog.new(form)
    return redirect(url_for(".index"))


@main.route("/new", methods=["GET"])
def new():
    return render_template("blog_new.html")


@main.route("/<int:blog_id>", methods=["GET"])
def view(blog_id):
    comments = BlogComment.find_all(blog_id=blog_id)
    blog = Blog.find(blog_id)
    return render_template("blog_view.html", blog=blog, comments=comments)


@main.route("/comment/add", methods=["POST"])
def comment_add():
    form = request.form
    BlogComment.new(form)
    return redirect(url_for(".view"))

