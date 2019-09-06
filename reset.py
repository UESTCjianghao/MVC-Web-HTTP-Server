import pymysql

from demo_app.models.comment import Comment
from demo_app.models.todo import Todo
from demo_app.models.user import User
from demo_app.models.session import Session
from demo_app.models.weibo import Weibo
from framework.utils import random_string


# noinspection SqlNoDataSourceInspection,SqlResolve
def test():
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='13971725491jh',
        db='web8',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

    with connection.cursor() as cursor:
        cursor.execute('DROP DATABASE IF EXISTS`web8`')
        cursor.execute('CREATE DATABASE `web8` CHARACTER SET utf8mb4')
        cursor.execute('USE `web8`')

        cursor.execute(User.sql_create)
        cursor.execute(Session.sql_create)
        cursor.execute(Todo.sql_create)
        cursor.execute(Weibo.sql_create)
        cursor.execute(Comment.sql_create)

    connection.commit()
    connection.close()

    form = dict(
        username='test',
        password='123',
    )
    User.register_user(form)
    u, result = User.login_user(form)
    assert u is not None, result
    form = dict(
        username='testt',
        password='123',
    )
    User.register_user(form)

    session_id = random_string()
    form = dict(
        session_id=session_id,
        user_id=u.id,
    )
    Session.new(form)
    s: Session = Session.one(session_id=session_id)
    assert s.session_id == session_id

    form = dict(
        title='test todo',
        user_id=u.id,
    )
    t = Todo.add(form, u.id)
    assert t.title == 'test todo'

    form = dict(
        content='test weibo',
        user_id=u.id,
    )
    w = Weibo.add(form, u.id)
    assert w.content == 'test weibo'

    form = dict(
        content='test comment',
        user_id=u.id,
    )
    c = Comment.add(form, u.id, w.id)
    assert c.content == 'test comment'


if __name__ == '__main__':
    test()
