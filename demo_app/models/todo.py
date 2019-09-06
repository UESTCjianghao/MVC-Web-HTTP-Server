from framework.model import SQLModel


class Todo(SQLModel):
    """
    针对我们的数据 TODO
    我们要做 4 件事情
    C create 创建数据
    R read 读取数据
    U update 更新数据
    D delete 删除数据

    Todo.new() 来创建一个 todo
    """

    # noinspection SqlNoDataSourceInspection
    sql_create = """
    CREATE TABLE `Todo` (
        `id`         INT NOT NULL AUTO_INCREMENT,
        `title`      VARCHAR(255) NOT NULL,
        `user_id`    INT NOT NULL,
        PRIMARY KEY (`id`)
    );
    """

    def __init__(self, form):
        super().__init__(form)
        self.title = form.get('title', '')
        self.user_id = form.get('user_id', -1)

    @classmethod
    def add(cls, form, user_id):
        form['user_id'] = user_id
        t = Todo.new(form)
        return t
