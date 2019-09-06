import time

from framework.model import SQLModel
from demo_app.models.user import User
from framework.utils import log, random_string


class Session(SQLModel):
    """
    Session 是用来保存 session 的 model
    """

    # noinspection SqlNoDataSourceInspection
    sql_create = """
    CREATE TABLE `Session` (
        `id`         INT NOT NULL AUTO_INCREMENT,
        `session_id` VARCHAR(255) NOT NULL,
        `user_id`    INT NOT NULL,
        `expired_time`     INT NOT NULL,
        PRIMARY KEY (`id`)
    );
    """

    def __init__(self, form):
        super().__init__(form)
        self.session_id = form.get('session_id', '')
        self.user_id = form.get('user_id', -1)
        self.expired_time = form.get('expired_time', time.time() + 3600)

    def expired(self):
        now = time.time()
        result = self.expired_time < now
        log('expired', result, self.expired_time, now)
        return result

        # if self.expired_time < now:
        #     return True
        # else:
        #     return False
        # return self.expired_time < now

    @classmethod
    def add(cls, user_id):
        session_id = random_string()
        form = dict(
            session_id=session_id,
            user_id=user_id,
        )
        Session.new(form)
        return session_id

    @classmethod
    def find_user(cls, session_id):
        s = cls.one(session_id=session_id)
        if s is None or s.expired():
            return User.guest()
        else:
            u = User.one(id=s.user_id)
            if u is None:
                return User.guest()
            else:
                return u
