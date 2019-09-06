from demo_app.models.todo import Todo
from framework.routes import (
    redirect,
    current_user,
    login_required,
    html_response
)
from framework.utils import log


def index(request):
    """
    todo 首页的路由函数
    """
    u = current_user(request)
    todos = Todo.all(user_id=u.id)
    return html_response('todo_index.html', todos=todos)


def add(request):
    """
    用于增加新 todo 的路由函数
    """
    form = request.form()
    u = current_user(request)

    Todo.add(form, u.id)
    # 浏览器发送数据过来被处理后, 重定向到首页
    # 浏览器在请求新首页的时候, 就能看到新增的数据了
    return redirect('/todo/index')


def delete(request):
    todo_id = int(request.query['id'])
    Todo.delete(todo_id)
    return redirect('/todo/index')


def edit(request):
    """
    todo 首页的路由函数
    """
    # 替换模板文件中的标记字符串
    todo_id = int(request.query['id'])
    t = Todo.one(id=todo_id)
    return html_response('todo_edit.html', todo_id=todo_id, todo_title=t.title)


# @login_required
def update(request):
    """
    用于增加新 todo 的路由函数
    """
    form = request.form()
    log('todo update', form, form['id'], type(form['id']))
    todo_id = int(form['id'])
    Todo.update(todo_id, title=form['title'])
    # 浏览器发送数据过来被处理后, 重定向到首页
    # 浏览器在请求新首页的时候, 就能看到新增的数据了
    return redirect('/todo/index')


def same_user_required(route_function):
    def f(request):
        log('same_user_required', route_function)
        u = current_user(request)
        if request.method == 'GET':
            todo_id = int(request.query['id'])
        elif request.method == 'POST':
            todo_id = int(request.form()['id'])
        else:
            raise ValueError('不支持的请求方法', request.method)

        t = Todo.one(id=todo_id)
        if t.user_id == u.id:
            return route_function(request)
        else:
            return redirect('/todo')
    return f


def route_dict():
    """
    路由字典
    key 是路由(路由就是 path)
    value 是路由处理函数(就是响应)
    """
    d = {
        '/todo/index': index,
        '/todo/add': add,
        '/todo/delete': login_required(same_user_required(delete)),
        '/todo/edit': login_required(same_user_required(edit)),
        '/todo/update': login_required(same_user_required(update)),
    }
    return d
