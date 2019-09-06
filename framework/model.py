import json
import os
import typing

import pymysql

from framework.utils import log


# noinspection SqlNoDataSourceInspection,SqlResolve
class SQLModel(object):

    def __init__(self, form):
        self.id = form.get('id', None)

    @classmethod
    def table_name(cls):
        return '{}'.format(cls.__name__)

    @classmethod
    def new(cls, form):
        # cls(form) 相当于 User(form)
        m = cls(form)
        _id = cls.insert(m.__dict__)
        m.id = _id
        return m

    @classmethod
    def _pymysql_connection(cls):
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='13971725491jh',
            db='web8',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection

    @classmethod
    def insert(cls, form: typing.Dict[str, str]):
        # INSERT INTO
        #     `user` (`username`, `password`, `email`)
        # VALUES
        #     (`xxx`, `123`, `xxx@xxx.com`)
        connection = cls._pymysql_connection()
        try:
            sql_keys = []
            sql_values = []
            for k in form.keys():
                sql_keys.append('`{}`'.format(k))
                sql_values.append('%s')
            formatted_sql_keys = ', '.join(sql_keys)
            formatted_sql_values = ', '.join(sql_values)

            sql_insert = 'INSERT INTO `{}` ({}) VALUES ({});'.format(
                cls.table_name(), formatted_sql_keys, formatted_sql_values
            )
            log('ORM insert <{}>'.format(sql_insert))
            values = tuple(form.values())
            with connection.cursor() as cursor:
                log('ORM execute <{}>'.format(cursor.mogrify(sql_insert, values)))
                cursor.execute(sql_insert, values)
                # 避免和内置函数 id 重名，所以用 _id
                _id = cursor.lastrowid
            connection.commit()
        finally:
            connection.close()

        # 先 commit，再关闭链接，再返回
        return _id

    @classmethod
    def one(cls, **kwargs):
        sql_where = ' AND '.join(
            ['`{}`=%s'.format(k) for k in kwargs.keys()]
        )
        sql_select = 'SELECT * FROM {} WHERE {}'.format(cls.table_name(), sql_where)
        log('ORM one <{}>'.format(sql_select))

        values = tuple(kwargs.values())
        connection = cls._pymysql_connection()
        try:
            with connection.cursor() as cursor:
                log('ORM execute <{}>'.format(cursor.mogrify(sql_select, values)))
                cursor.execute(sql_select, values)
                result = cursor.fetchone()
        finally:
            log('finally 一定会被执行，就算 在 return 之后')
            connection.close()

        if result is None:
            return None
        else:
            m = cls(result)
        return m

    @classmethod
    def all(cls, **kwargs):
        # SELECT * FROM User WHERE username='xxx' AND password='xxx'
        sql_select = 'SELECT * FROM {}'.format(cls.table_name())

        if len(kwargs) > 0:
            sql_where = ' AND '.join(
                ['`{}`=%s'.format(k) for k in kwargs.keys()]
            )
            sql_select = '{} WHERE {}'.format(sql_select, sql_where)
        log('ORM all <{}>'.format(sql_select))

        values = tuple(kwargs.values())
        connection = cls._pymysql_connection()
        try:
            with connection.cursor() as cursor:
                log('ORM execute <{}>'.format(cursor.mogrify(sql_select, values)))
                cursor.execute(sql_select, values)
                result = cursor.fetchall()
        finally:
            connection.close()

        ms = []
        for row in result:
            m = cls(row)
            ms.append(m)
        return ms

    @classmethod
    def delete(cls, id):
        sql_delete = 'DELETE FROM {} WHERE `id`=%s'.format(cls.table_name())
        log('ORM delete <{}>'.format(sql_delete))

        connection = cls._pymysql_connection()
        try:
            with connection.cursor() as cursor:
                log('ORM execute <{}>'.format(cursor.mogrify(sql_delete, (id,))))
                cursor.execute(sql_delete, (id,))
            connection.commit()
        finally:
            connection.close()

    @classmethod
    def update(cls, id, **kwargs):
        # UPDATE
        # 	`User`
        # SET
        # 	`username`=%s, `password`=%s
        # WHERE `id`=%s;
        sql_set = ', '.join(
            ['`{}`=%s'.format(k) for k in kwargs.keys()]
        )
        sql_update = 'UPDATE {} SET {} WHERE `id`=%s'.format(
            cls.table_name(),
            sql_set,
        )
        log('ORM update <{}>'.format(sql_update.replace('\n', ' ')))

        values = list(kwargs.values())
        values.append(id)
        values = tuple(values)

        connection = cls._pymysql_connection()
        try:
            with connection.cursor() as cursor:
                log('ORM execute <{}>'.format(cursor.mogrify(sql_update, values)))
                cursor.execute(sql_update, values)
            connection.commit()
        finally:
            connection.close()


def save(data, path):
    """
    本函数把一个 dict 或者 list 写入文件
    data 是 dict 或者 list
    path 是保存文件的路径
    """
    # json 是一个序列化/反序列化(上课会讲这两个名词) list/dict 的库
    # indent 是缩进
    # ensure_ascii=False 用于保存中文
    log('save 当前工作目录和数据相对路径 {} {}'.format(os.getcwd(), path))
    log('save 序列化前\n<{}>'.format(data))
    s = json.dumps(data, indent=2, ensure_ascii=False)
    log('save 序列化后\n<{}>'.format(s))
    with open(path, 'w+', encoding='utf-8') as f:
        f.write(s)


def load(path):
    """
    本函数从一个文件中载入数据并转化为 dict 或者 list
    path 是保存文件的路径
    """

    log('load 当前工作目录和数据相对路径 {} {}'.format(os.getcwd(), path))
    # 文件不存在就写入默认空数组文件
    if not os.path.exists(path):
        log('load 路径不存在，写入默认空数组数据。')
        # db 文件夹不存在，save 会报错
        # xx.txt 不存在，会自动创建
        save([], path)

    with open(path, 'r', encoding='utf-8') as f:
        s = f.read()
    log('load 反序列化前和\n<{}>'.format(s))
    data = json.loads(s)
    log('load 反序列化后\n<{}>'.format(data))
    return data


class Model(object):
    """
    Model 是所有 model 的基类
    @classmethod 是一个套路用法
    例如
    user = User()
    user.db_path() 返回 User.txt
    """

    def __init__(self, form):
        self.id = form.get('id', None)
        # self.id = None

    @classmethod
    def db_path(cls):
        """
        cls 是类名, 谁调用的类名就是谁的
        classmethod 有一个参数是 class(这里我们用 cls 这个名字)
        所以我们可以得到 class 的名字
        """
        classname = cls.__name__
        path = 'db/{}.txt'.format(classname)
        return path

    @classmethod
    def new(cls, form):
        # cls(form) 相当于 User(form)
        m = cls(form)
        return m

    @classmethod
    def delete(cls, id):
        ms = cls.all()
        for i, m in enumerate(ms):
            if m.id == id:
                del ms[i]
                break

        # 保存
        # __dict__ 是包含了对象所有属性和值的字典
        data = [m.__dict__ for m in ms]
        path = cls.db_path()
        save(data, path)

    @classmethod
    def all(cls):
        """
        all 方法(类里面的函数叫方法)使用 load 函数得到所有的 models
        """
        path = cls.db_path()
        models = load(path)
        log('models in all', models)
        # 这里用了列表推导生成一个包含所有 实例 的 list
        # m 是 dict, 用 cls.new(m) 可以初始化一个 cls 的实例
        # 不明白就 log 大法看看这些都是啥
        ms = [cls(m) for m in models]
        return ms

    @classmethod
    def find_by(cls, **kwargs):
        log('find_by kwargs', kwargs)

        for m in cls.all():
            exist = True
            for k, v in kwargs.items():
                if not hasattr(m, k) or not getattr(m, k) == v:
                    exist = False
            if exist:
                return m

    @classmethod
    def find_all(cls, **kwargs):
        log('find_all kwargs', kwargs)
        models = []

        for m in cls.all():
            exist = True
            for k, v in kwargs.items():
                log('for loop in find all', m, k, v, hasattr(m, k), getattr(m, k), getattr(m, k) == v)
                if not hasattr(m, k) or not getattr(m, k) == v:
                    exist = False
            if exist:
                models.append(m)

        return models

    def save(self):
        """
        用 all 方法读取文件中的所有 model 并生成一个 list
        把 self 添加进去并且保存进文件
        """

        models = self.all()
        log('models', models)

        if self.id is None:
            # 加上 id
            if len(models) > 0:
                log('不是第一个元素', models[-1].id)
                self.id = models[-1].id + 1
            else:
                log('第一个元素')
                self.id = 0
            models.append(self)
        else:
            # 有 id 说明已经是存在于数据文件中的数据
            # 那么就找到这条数据并替换
            for i, m in enumerate(models):
                if m.id == self.id:
                    models[i] = self

        # 保存
        # __dict__ 是包含了对象所有属性和值的字典
        data = [m.__dict__ for m in models]
        path = self.db_path()
        save(data, path)

    def __repr__(self):
        """
        __repr__ 是一个魔法方法
        简单来说, 它的作用是得到类的 字符串表达 形式
        比如 print(u) 实际上是 print(u.__repr__())
        不明白就看书或者 搜
        """
        classname = self.__class__.__name__
        properties = ['{}: ({})'.format(k, v) for k, v in self.__dict__.items()]
        s = '\n'.join(properties)
        return '< {}\n{} >\n'.format(classname, s)
