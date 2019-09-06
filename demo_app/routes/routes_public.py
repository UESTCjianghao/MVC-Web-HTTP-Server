import os
import urllib.parse

from demo_app.models.session import Session
from demo_app.models.user import User
from framework.routes import (
    current_user,
    html_response,
    redirect
)
from framework.utils import log


def route_index(request):
    """
    主页的处理函数, 返回主页的响应
    """
    u = current_user(request)
    return html_response('index.html', username=u.username)


def route_ajax(request):
    """
    主页的处理函数, 返回主页的响应
    """
    return html_response('ajax.html')


def route_login(request):
    """
    登录页面的路由函数
    """
    log('login, headers', request.headers)
    log('login, cookies', request.cookies)
    user_current = current_user(request)
    log('current user', user_current)

    form = request.form()
    user_login, result = User.login_user(form)
    result = urllib.parse.quote_plus(result)
    if user_login is not None:
        session_id = Session.add(user_login.id)
        headers = {'Set-Cookie': 'session_id={}'.format(session_id)}
    else:
        headers = {}

    # return redirect('/todo')
    return redirect('/login/view', result=result, headers=headers)


def route_login_view(request):
    """
    登录页面视图
    """

    log('login, headers', request.headers)
    log('login, cookies', request.cookies)
    user = current_user(request)
    log('current user', user)

    result = request.query.get('result', '')
    result = urllib.parse.unquote_plus(result)

    return html_response(
        'login.html', result=result, username=user.username
    )


def route_register_view(request):
    user = current_user(request)
    result = request.query.get('result', '')
    result = urllib.parse.unquote_plus(result)
    return html_response(
        'register.html', result=result, username=user.username
    )


def route_register(request):
    form = request.form()
    result = User.register_user(form)
    # 换行符需要编码，不然显示不全
    result = urllib.parse.quote_plus(result)
    return redirect('/register/view', result=result)


def route_static(request):
    """
    静态资源的处理函数, 读取图片并生成响应返回
    """
    filename: str = request.query['file']
    path = os.path.join('demo_app', 'static', filename)

    if filename.endswith('.gif'):
        content_type = b'Content-Type: image/gif'
    elif filename.endswith('.js'):
        content_type = b'Content-Type: application/javascript'
    else:
        raise ValueError('不支持的后缀名', filename)

    with open(path, 'rb') as f:
        header = b'HTTP/1.1 200 OK\r\n' + content_type
        r = header + b'\r\n\r\n' + f.read()
        return r


def route_dict():
    """
    路由字典
    key 是路由(路由就是 path)
    value 是路由处理函数(就是响应)
    """
    # f = login_required(route_message)
    # route_index(request)
    # f(request)
    d = {
        '/': route_index,
        '/static': route_static,
        '/login': route_login,
        '/login/view': route_login_view,
        '/register/view': route_register_view,
        '/register': route_register,
        '/ajax': route_ajax,
    }
    return d
