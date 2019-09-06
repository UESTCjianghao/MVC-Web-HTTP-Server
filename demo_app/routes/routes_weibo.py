from demo_app.models.comment import Comment
from demo_app.models.weibo import Weibo
from framework.routes import (
    redirect,
    current_user,
    html_response,
    login_required,
)
from framework.utils import log


def index(request):
    """
    weibo 首页的路由函数
    """
    if 'user_id' in request.query:
        user_id = int(request.query['user_id'])
    else:
        u = current_user(request)
        user_id = u.id
    weibos = Weibo.all(user_id=user_id)
    # 替换模板文件中的标记字符串
    return html_response('weibo_index.html', weibos=weibos)


def add(request):
    """
    用于增加新 weibo 的路由函数
    """
    u = current_user(request)
    form = request.form()
    Weibo.add(form, u.id)
    # 浏览器发送数据过来被处理后, 重定向到首页
    # 浏览器在请求新首页的时候, 就能看到新增的数据了
    return redirect('/weibo/index')


def delete(request):
    weibo_id = int(request.query['weibo_id'])
    Weibo.delete(weibo_id)
    cs = Comment.all(weibo_id=weibo_id)
    for c in cs:
        c.delete()
    return redirect('/weibo/index')


def edit(request):
    weibo_id = int(request.query['weibo_id'])
    w = Weibo.one(id=weibo_id)
    return html_response('weibo_edit.html', weibo=w)


def update(request):
    """
    用于增加新 weibo 的路由函数
    """
    form = request.form()
    weibo_id = int(form['weibo_id'])
    Weibo.update(weibo_id, content=form['content'])
    # 浏览器发送数据过来被处理后, 重定向到首页
    # 浏览器在请求新首页的时候, 就能看到新增的数据了
    return redirect('/weibo/index')


def comment_add(request):
    u = current_user(request)
    form = request.form()
    weibo_id = int(form['weibo_id'])
    Comment.add(form, u.id, weibo_id)
    return redirect('/weibo/index')


def comment_delete(request):
    comment_id = int(request.query['comment_id'])
    Comment.delete(comment_id)
    return redirect('/weibo/index')


def comment_edit(request):
    comment_id = int(request.query['comment_id'])
    c = Comment.one(id=comment_id)
    return html_response('comment_edit.html', comment=c)


def comment_update(request):
    """
    用于增加新 weibo 的路由函数
    """
    form = request.form()
    comment_id = int(form['comment_id'])
    Comment.update(comment_id, content=form['content'])
    # 浏览器发送数据过来被处理后, 重定向到首页
    # 浏览器在请求新首页的时候, 就能看到新增的数据了
    return redirect('/weibo/index')


def weibo_owner_required(route_function):
    """
    这个函数看起来非常绕，所以你不懂也没关系
    就直接拿来复制粘贴就好了
    """

    # noinspection DuplicatedCode
    def f(request):
        log('weibo_owner_required')
        u = current_user(request)
        id_key = 'weibo_id'
        if id_key in request.query:
            weibo_id = request.query[id_key]
        else:
            weibo_id = request.form()[id_key]
        w = Weibo.one(id=int(weibo_id))

        if w.user_id == u.id:
            log('不是微博作者', w)
            return route_function(request)
        else:
            return redirect('/weibo/index')

    return f


def comment_owner_required(route_function):
    """
    这个函数看起来非常绕，所以你不懂也没关系
    就直接拿来复制粘贴就好了
    """

    # noinspection DuplicatedCode
    def f(request):
        log('comment_owner_required')
        u = current_user(request)
        id_key = 'comment_id'
        if id_key in request.query:
            comment_id = request.query[id_key]
        else:
            comment_id = request.form()[id_key]
        c = Comment.one(id=int(comment_id))

        if c.user_id == u.id:
            log('不是评论作者', c)
            return route_function(request)
        else:
            return redirect('/weibo/index')

    return f


def comment_or_weibo_owner_required(route_function):
    def f(request):
        log('comment_or_weibo_owner_required')
        if request.method == 'GET':
            data = request.query
        elif request.method == 'POST':
            data = request.form()
        else:
            raise ValueError('不支持的方法', request.method)

        comment_key = 'comment_id'
        weibo_key = 'weibo_id'
        if comment_key in data:
            c = Comment.one(id=int(data[comment_key]))
            if c is None:
                return redirect('/weibo/index')
            else:
                user_id = c.user_id
        elif weibo_key in data:
            w = Weibo.one(id=int(data[weibo_key]))
            if w is None:
                return redirect('/weibo/index')
            else:
                user_id = w.user_id
        else:
            raise ValueError('不支持的参数', data)

        u = current_user(request)
        if user_id == u.id:
            log('不是评论或者微博的作者', user_id, u.id)
            return route_function(request)
        else:
            return redirect('/weibo/index')

    return f


def route_dict():
    """
    路由字典
    key 是路由(路由就是 path)
    value 是路由处理函数(就是响应)
    """
    d = {
        '/weibo/index': login_required(index),
        '/weibo/add': login_required(add),
        '/weibo/delete': login_required(weibo_owner_required(delete)),
        '/weibo/edit': login_required(weibo_owner_required(edit)),
        '/weibo/update': login_required(weibo_owner_required(update)),
        # 评论功能
        '/comment/add': login_required(comment_add),
        '/comment/delete': login_required(comment_or_weibo_owner_required(comment_delete)),
        '/comment/edit': login_required(comment_owner_required(comment_edit)),
        '/comment/update': login_required(comment_owner_required(comment_update)),
    }
    return d
