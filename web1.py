import socket
import ssl

"""
解析 url 返回 (protocol host port path)
有的时候有的函数, 它本身就美不起来, 你要做的就是老老实实写
url 是字符串, 可能的值如下
    'g.cn'
    'g.cn/'
    'g.cn:3000'
    'g.cn:3000/search'
    'http://g.cn'
    'https://g.cn'
    'http://g.cn/'
    返回代表端口的字符串, 比如 '80' 或者 '3000'
    注意, 如上课资料所述, 80 是默认端口
"""


def log(*args, **kw):
    print('log:', *args, **kw)


def parsed_url(url):
    """
        解析 url 返回 (protocol host port path)
        有的时候有的函数, 它本身就美不起来, 你要做的就是老老实实写
    """
    # 检查协议
    protocol = 'http'
    if url[:7] == 'http://':
        u = url.split('://')[1]
    elif url[:8] == 'https://':
        protocol = 'https'
        u = url.split('://')[1]
    else:
        # '://' 定位 然后取第一个 / 的位置来切片
        u = url

    # https://g.cn:1234/hello
    # g.cn:1234/hello

    # 检查默认 path
    i = u.find('/')
    if i == -1:
        host = u
        path = '/'
    else:
        host = u[:i]
        path = u[i:]

    # 检查端口
    port_dict = {
        'http': 80,
        'https': 443,
    }
    # 默认端口
    port = port_dict[protocol]
    # if host.find(':') != -1:
    if ':' in host:
        h = host.split(':')
        host = h[0]
        port = int(h[1])

    return protocol, host, port, path


def socket_by_protocal(protocal):
    # sockets = {
    #     'http': socket.socket,
    #     'https': ssl.wrap_socket(socket.socket()),
    # }
    # return sockets[protocal]
    if protocal == 'http':
        s = socket.socket()
    else:
        s = ssl.wrap_socket(socket.socket())

    return s


def response_by_socket(s):
    response = b''
    buffer_size = 1024
    while True:
        r = s.recv(buffer_size)
        if len(r) == 0:
            break
        response += r

    return response


def parsed_response(r):
    header, body = r.split('\r\n\r\n', 1)
    h = header.split('\r\n')
    status_code = h[0].split()[1]
    status_code = int(status_code)

    headers = {}
    for line in h[1:]:
        k, v = line.split(': ')
        headers[k] = v
    return status_code, headers, body


def get(url):
    protocal, host, port, path = parsed_url(url)
    # 不写 how 写 what
    s = socket_by_protocal(protocal)
    s.connect((host, port))

    request = 'GET {} HTTP/1.1\r\nHost: {}\r\nConnection: close\r\n\r\n'.format(path, host)
    encoding = 'utf-8'
    s.send(request.encode(encoding))

    response = response_by_socket(s)
    r = response.decode(encoding)

    status_code, headers, body = parsed_response(r)
    if status_code in [301, 302]:
        url = headers['location']
        return get(url)

    # log('zhao:', status_code, headers, body)
    return status_code, headers, body


def main():
    url = 'http://www.baidu.com/'
    status_code, headers, body = get(url)
    log(body)


# 下面以 test 开头的是单元测试的函数
def test_parsed_url():
    http = 'http'
    https = 'https'
    host = 'g.cn'
    path = '/'
    test_items = (
        ('http://g.cn/', (http, host, 80, path)),
        ('http://g.cn/', (http, host, 80, path)),
        ('http://g.cn:90', (http, host, 90, path)),
        ('http://g.cn:90/', (http, host, 90, path)),
        #
        ('https://g.cn', (https, host, 443, path)),
        ('https://g.cn:233/', (https, host, 233, path)),
    )

    for t in test_items:
        url, expected = t
        u = parsed_url(url)

        e = "parsed_url ERROR, ({}) ({}) ({})".format(url, u, expected)
        # log("({}) ({}) ".format(url, u))
        assert u == expected, e


def test_parsed_response():
    """
    测试是否能正确解析响应
    """
    # NOTE, 行末的 \ 表示连接多行字符串
    response = 'HTTP/1.1 301 Moved Permanently\r\n' \
               'Content-Type: text/html\r\n' \
               'Location: https://movie.douban.com/top250\r\n' \
               'Content-Length: 178\r\n\r\n' \
               'test body'
    status_code, header, body = parsed_response(response)
    assert status_code == 301
    assert len(list(header.keys())) == 3
    assert body == 'test body'
    # log(status_code, header, body)


def test_get():
    """
    测试是否能正确处理 HTTP 和 HTTPS
    """
    urls = [
        'http://movie.douban.com/top250',
        'https://movie.douban.com/top250',
    ]
    # 这里就直接调用了 get 如果出错就会挂, 测试得比较简单
    for u in urls:
        get(u)


def test():
    test_parsed_url()
    test_parsed_response()
    test_get()


if __name__ == '__main__':
    # test()
    main()


