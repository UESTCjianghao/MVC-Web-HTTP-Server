import socket
import urllib.parse
import threading


from framework.utils import log
from framework.routes import (
    error,
)


class BaseRequest(object):
    def __init__(self):
        self.body = ''
        self.method = ''
        self.path = ''
        self.query = {}
        self.headers = {}
        self.cookies = {}

    def form(self):
        body = urllib.parse.unquote_plus(self.body)
        log('form', self.body)
        log('form', body)
        args = body.split('&')
        f = {}
        log('args', args)
        for arg in args:
            k, v = arg.split('=')
            f[k] = v
        log('form() 字典', f)
        return f


# 定义一个 class 用于保存请求的数据
class Request(BaseRequest):
    def __init__(self, raw_data):
        super().__init__()
        # 只能 split 一次，因为 body 中可能有换行
        header, self.body = raw_data.split('\r\n\r\n', 1)
        h = header.split('\r\n')

        parts = h[0].split()
        self.method = parts[0]
        path = parts[1]
        self.parse_path(path)
        log('请求 path 和 query', self.path, self.query)

        self.add_headers(h[1:])
        log('请求 headers', self.headers)
        log('请求 cookies', self.cookies)

    def add_headers(self, header):
        """
        Cookie: user=xxx
        """
        lines = header
        for line in lines:
            k, v = line.split(': ', 1)
            self.headers[k] = v

        if 'Cookie' in self.headers:
            cookies = self.headers['Cookie']
            # 浏览器发来的 cookie 只有一个值
            parts = cookies.split('; ')
            for part in parts:
                k, v = part.split('=', 1)
                self.cookies[k] = v

    def parse_path(self, path):
        """
        输入: /xxx?message=hello&author=xx
        返回
        (xxx, {
            'message': 'hello',
            'author': 'xxx',
        })
        """
        index = path.find('?')
        if index == -1:
            self.path = path
            self.query = {}
        else:
            path, query_string = path.split('?', 1)
            args = query_string.split('&')
            query = {}
            for arg in args:
                k, v = arg.split('=')
                query[k] = v
            self.path = path
            self.query = query


def request_from_connection(connection):
    request = b''
    buffer_size = 1024
    while True:
        r = connection.recv(buffer_size)
        request += r
        # 取到的数据长度不够 buffer_size 的时候，说明数据已经取完了。
        if len(r) < buffer_size:
            return request


def response_for_path(request, route):
    """
    根据 path 调用相应的处理函数
    没有处理的 path 会返回 404
    """
    # 注册外部的路由
    response = route.get(request.path, error)
    return response(request)


def process_connection(connection, route):
    with connection:
        r = request_from_connection(connection)
        log('http 请求:<\n{}\n>'.format(r.decode()))
        r = r.decode()
        if len(r) > 0:
            # 把原始请求数据传给 Request 对象
            request = Request(r)
            # 用 response_for_path 函数来得到 path 对应的响应内容
            response = response_for_path(request, route)
            index = response.find(b'Content-Type: text/html')
            if index == -1:
                start = response.find(b'\r\n\r\n')
                gif_length = len(response[start:])
                gif_header = response[:start]
                log('http 响应头部: <{}> 内容长度：<{}>'.format(gif_header, gif_length))
            else:
                log("http 响应:<\n{}\n>".format(response.decode()))
            # 把响应发送给客户端
            connection.sendall(response)
        else:
            connection.sendall(b'')


def run(host, port, route):
    """
    启动服务器
    """
    # 初始化 socket 套路
    # 使用 with 可以保证程序中断的时候正确关闭 socket 释放占用的端口
    log('开始运行于', 'http://{}:{}'.format(host, port))
    with socket.socket() as s:
        s.bind((host, port))
        # 无限循环来处理请求
        # 监听 接受 读取请求数据 解码成字符串
        # noinspection PyArgumentList
        s.listen()
        while True:
            connection, address = s.accept()
            log('请求 ip 和 端口 <{}>\n'.format(address))
            t = threading.Thread(target=process_connection, args=(connection, route))
            t.start()


class WsgiRequest(BaseRequest):
    # {'wsgi.errors': <gunicorn.http.wsgi.WSGIErrorsWrapper object at 0x7fa090b316d8>,
    # 'wsgi.version': (1, 0), 'wsgi.multithread': False, 'wsgi.multiprocess': True,
    # 'wsgi.run_once': False, 'wsgi.file_wrapper': <class 'gunicorn.http.wsgi.FileWrapper'>,
    # 'SERVER_SOFTWARE': 'gunicorn/19.7.1',
    # 'wsgi.input': <gunicorn.http.body.Body object at 0x7fa090b31e10>,
    # 'gunicorn.socket': <socket.socket fd=12, family=AddressFamily.AF_INET, type=SocketKind.SOCK_STREAM, proto=0,
    # laddr=('127.0.0.1', 8000), raddr=('127.0.0.1', 51312)>,
    # 'REQUEST_METHOD': 'GET', 'QUERY_STRING': '', 'RAW_URI': '/', 'SERVER_PROTOCOL': 'HTTP/1.1',
    # 'HTTP_HOST': '127.0.0.1:8000', 'HTTP_USER_AGENT': 'curl/7.58.0', 'HTTP_ACCEPT': '*/*',
    # 'HTTP_COOKIE': 'session=vvvv', 'wsgi.url_scheme': 'http', 'REMOTE_ADDR': '127.0.0.1',
    # 'REMOTE_PORT': '51312', 'SERVER_NAME': '127.0.0.1', 'SERVER_PORT': '8000', 'PATH_INFO': '/', 'SCRIPT_NAME': ''}
    def __init__(self, environ):
        super().__init__()
        self.raw = environ
        self.path = environ['PATH_INFO']
        self.query = environ['QUERY_STRING']
        log('请求 path 和 query', self.path, self.query)
        from gunicorn.http.body import Body
        body: Body = environ['wsgi.input']
        log('body', body.read())
        self.body = body.read().decode(encoding='utf-8')
        self.headers = environ
        self.cookies = {}
        self.add_cookie(environ.get('HTTP_COOKIE', ''))
        log('请求 headers', self.headers)
        log('请求 cookies', self.cookies)

    def add_cookie(self, raw_cookie):
        if len(raw_cookie) > 0:
            parts = raw_cookie.split('; ')
            for part in parts:
                k, v = part.split('=', 1)
                self.cookies[k] = v

    def form(self):
        body = urllib.parse.unquote_plus(self.body)
        log('form', self.body)
        log('form', body)
        args = body.split('&')
        f = {}
        log('args', args)
        for arg in args:
            k, v = arg.split('=')
            f[k] = v
        log('form() 字典', f)
        return f


class WsgiResponse(object):
    def __init__(self, raw_data: bytes):
        # 只能 split 一次，因为 body 中可能有换行
        data = raw_data.decode(encoding='utf-8')
        raw_header, self.body = raw_data.split(b'\r\n\r\n', 1)
        header = raw_header.decode()
        h = header.split('\r\n')

        parts = h[0].split()
        self.status = '{} {}'.format(parts[1], parts[2])
        log('响应状态', self.status)

        self.headers = {}
        self.add_headers(h[1:])
        log('响应 headers', self.headers)

    def add_headers(self, header):
        """
        Cookie: user=xxx
        """
        lines = header
        for line in lines:
            k, v = line.split(': ', 1)
            self.headers[k] = v


def configured_wsgi_app(route):
    def wsgi_app(environ, start_response):
        log('raw environ request', environ)
        request = WsgiRequest(environ)
        raw_response = response_for_path(request, route=route)
        response = WsgiResponse(raw_response)
        log('response', response.status, response.headers, response.body)
        # data = b"Hello, World!\n"
        # start_response("200 OK", [
        #     ("Content-Type", "text/plain"),
        #     ("Content-Length", str(len(data)))
        # ])
        data = response.body
        headers = list(response.headers.items())
        status = response.status
        start_response(status, headers)
        return iter([data])

    return wsgi_app
