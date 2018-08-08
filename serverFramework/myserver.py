from utils import log
import socket
import urllib.parse

from routes import route_static
from routes import route_dict


class Request(object):
    def __init__(self):
        self.method = 'GET'
        self.path = ''
        self.query = {}
        self.body = ''
        self.headers = {}
        self.cookies = {}

    def add_cookies(self):
        """
        height=169; user=gua
        :return:
        """
        cookies = self.headers.get('Cookie', '')
        kvs = cookies.split('; ')
        log('cookie', kvs)
        for kv in kvs:
            if '=' in kv:
                k, v = kv.split('=')
                self.cookies[k] = v

    def add_headers(self, header):
        """
        :param header:
        [
            'Accept-Language: zh-CN,zh;q=0.8'
            'Cookie: height=169; user=gua'
        ]
        :return:
        """
        lines = header
        for line in lines:
            k, v = line.split(':', 1)
            self.headers[k] = v
        # 清除 cookies
        self.cookies = {}
        self.add_cookies()

    # 现在还不知道这个函数的意义
    def form(self):
        body = urllib.parse.unquote(self.body)
        args = body.split('&')
        f = {}
        for arg in args:
            k, v = arg.split('=')
            f[k] = v
        return f


request = Request()


def error(request, code=404):
    """
    根据不同的 code 响应错误
    :param request:
    :param code:
    :return:
    """
    e = {
        404: b'HTTP/1.x 404 NOT FOUND\r\n\r\n<h1>NOT FOUND</h1>',
    }

    return e.get(code, b'')


def parsed_path(path):
    """
    :param path: /asdasd?message=hello&author=gua
                /asdasd
    :return:
    """
    query = {}
    if '?' not in path:
        return path, query
    path, query_string = path.split('?', 1)
    args = query_string.split('&')
    for arg in args:
        k, v = arg.split('=')
        query[k] = v
    return path, query


def response_for_path(path):
    path, query = parsed_path(path)
    request.path = path
    request.query = query
    log('path and query', path, query)
    """
    根据 path 调用相应的处理函数
    没有处理的 path 会返回 404
    """
    r = {
        '/static': route_static,
        # '/': route_index,
        # '/login': route_login,
        # '/messages': route_message,
    }
    r.update(route_dict)
    response = r.get(path, error)
    return response(request)


def run(host='', port=5210):
    """
    :param host:
    :param port:
    :return:
    启动服务器:
    """
    log('start at:', '{}:{}'.format(host, port))
    rs = ''
    with socket.socket() as s:
        s.bind((host, port))
        # 无限循环处理请求
        while True:
            s.listen(3)
            connection, address = s.accept()
            # while True:
            #     r = connection.recv(1000)
            #     r = r.decode('utf-8')
            #     log('r:::', r)
            #     if r == '':
            #         break
            #     rs += r
            r = connection.recv(1000)
            r = r.decode('utf-8')
            rs = r
            log('r:::', r)
            # chrome 会发空请求导致 split 得到空 list
            # 判断一下是不是空 防止程序崩溃
            log('rs :::', rs)
            if len(rs.split()) < 2:
                continue
            path = rs.split()[1]
            # 设置 request 的 method
            request.method = rs.split()[0]
            request.add_headers(rs.split('\r\n\r\n', 1)[0].split('\r\n')[1:])
            # 把 body 放入 request 中
            request.body = rs.split('\r\n\r\n', 1)[1]
            # 用
            response = response_for_path(path)
            # 把响应发送给客户端
            connection.sendall(response)
            connection.close()


def main():
    config = dict(
        host='',
        port=5210,
    )
    run(**config)


if __name__ == '__main__':
    main()
