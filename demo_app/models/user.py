import hashlib

from framework.model import SQLModel
from demo_app.models.user_role import UserRole


class User(SQLModel):
    """
    User 是一个保存用户数据的 model
    现在只有两个属性 username 和 password
    """

    # noinspection SqlNoDataSourceInspection
    # mysql 原生支持枚举
    sql_create = """
    CREATE TABLE `User` (
        `id`         INT NOT NULL AUTO_INCREMENT,
        `username`   VARCHAR(255) NOT NULL,
        `password`   VARCHAR(255) NOT NULL,
        `role`       ENUM('normal', 'admin'), 
        PRIMARY KEY (`id`)
    );
    """

    def __init__(self, form):
        super().__init__(form)
        self.username = form.get('username', '')
        self.password = form.get('password', '')
        self.role = form.get('role', UserRole.normal)
        # self.role = form.get('role', 'normal')


    @staticmethod
    def guest():
        form = dict(
            role=UserRole.guest,
            # role='guest',
            username='[游客]',
            id=-1,
        )
        u = User(form)
        return u

    def is_guest(self):
        # return self.username == '【游客】'
        # return self.role == 'guest'
        return self.role == UserRole.guest

    @staticmethod
    def salted_password(password):
        salt = 'jdklajskldjkassapsqwekjsldasdasqwweq'
        salted = password + salt
        hashed = hashlib.sha256(salted.encode()).hexdigest()
        return hashed

    @classmethod
    def login_user(cls, form):
        username = form['username']
        salted = cls.salted_password(form['password'])
        u = User.one(username=username, password=salted)
        if u is None:
            result = '用户名或者密码错误'
        else:
            result = '登录成功'
        return u, result

    @classmethod
    def register_user(cls, form: dict):
        # 避免修改参数引起副作用
        form = form.copy()
        valid = len(form['username']) > 2 and len(form['password']) > 2
        if valid:
            form['password'] = cls.salted_password(form['password'])
            User.new(form)
            return '注册成功<br> <pre>{}</pre>'.format(User.all())
        else:
            return '用户名或者密码长度必须大于2'
