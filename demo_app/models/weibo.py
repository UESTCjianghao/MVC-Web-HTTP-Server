from framework.model import SQLModel
from demo_app.models.comment import Comment
from demo_app.models.user import User


class Weibo(SQLModel):
    """
    微博类
    """

    sql_create = """
    CREATE TABLE `Weibo` (
        `id`         INT NOT NULL AUTO_INCREMENT,
        `content`      VARCHAR(255) NOT NULL,
        `user_id`    INT NOT NULL,
        PRIMARY KEY (`id`)
    );
    """

    def __init__(self, form):
        super().__init__(form)
        self.content = form.get('content', '')
        # 和别的数据关联的方式, 用 user_id 表明拥有它的 user 实例
        self.user_id = form.get('user_id', -1)

    @classmethod
    def add(cls, form, user_id):
        form['user_id'] = user_id
        w = Weibo.new(form)
        return w

    def comments(self):
        cs = Comment.all(weibo_id=self.id)
        return cs

    def user(self):
        u = User.one(id=self.user_id)
        return u
