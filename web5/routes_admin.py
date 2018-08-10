from models import User
from routes_todo import redirect
from routes_todo import login_required
from routes_todo import template
from routes_todo import response_with_headers
from routes import current_user


def current_user_instance(request):
    uname = current_user(request)
    u = User.find_by(username=uname)
    return u


def index(request):
    """
    增加一个路由 / admin / users
    只有 id 为 1 的用户可以访问这个页面, 其他用户访问会定向到 / login
    这个页面显示了所有的用户 包括 id username password
    :param request:
    :return:
    """
    headers = {
        'Content-Type': 'text/html',
    }
    userlist = ''
    # 检验登陆后访问这个页面
    u = current_user_instance(request)
    if u.id != 1:
        return redirect('/login')
    else:
        # 得到所有用户
        us = User.all()
        for u in us:
            id = u.id
            username = u.username
            password = u.password
            userlist += '<h2>id: {} username: {} password:{}</h2>'.format(id, username, password)
        header = response_with_headers(headers)
        admin_index = template('admin.html')
        admin_index = admin_index.replace('{{userlist}}', userlist)
        r = header + '\r\n\r\n' + admin_index
        return r.encode('utf-8')


def update(request):
    # 差一个检查管理员的函数
    if request.method != 'POST':
        return redirect('http://localhost:3000/admin/users')
    form = request.form()
    id = int(form.get('id', '-1'))
    password = form.get('password', '-1')
    # 检查 id 存不存在
    # 得到那个的 user
    u = User.find_by(id=id)
    if u is None:
        return redirect('/')
    u.password = password
    u.save()
    return index(request)


route_admin = {
    '/admin/users': login_required(index),
    '/admin/users/update': login_required(update)
}
