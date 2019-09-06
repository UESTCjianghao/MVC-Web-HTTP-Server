from framework.model import SQLModel
from demo_app.models.user import User


# from models.weibo import Weibo
from framework.utils import log


class Comment(SQLModel):
    """
    评论类
    """
    sql_create = """
    CREATE TABLE `Comment` (
        `id`          INT NOT NULL AUTO_INCREMENT,
        `content`     VARCHAR(255) NOT NULL,
        `weibo_id`    INT NOT NULL,
        `user_id`     INT NOT NULL,
        PRIMARY KEY (`id`)
    );
    """

    def __init__(self, form, user_id=-1):
        super().__init__(form)
        self.content = form.get('content', '')
        # 和别的数据关联的方式, 用 user_id 表明拥有它的 user 实例
        self.user_id = form.get('user_id', user_id)
        self.weibo_id = int(form.get('weibo_id', -1))

    @classmethod
    def add(cls, form, user_id, weibo_id):
        form['user_id'] = user_id
        form['weibo_id'] = weibo_id
        c = Comment.new(form)
        log('comment add', c, user_id, weibo_id, form)
        return c

    def user(self):
        u = User.one(id=self.user_id)
        return u

    # def weibo(self):
    #     w = Weibo.find_by(id=self.weibo_id)
    #     return w
