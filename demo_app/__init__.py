from demo_app.routes.routes_public import route_dict

# 用 from import as 来避免重名
from demo_app.routes.routes_todo import route_dict as routes_todo
from demo_app.routes.routes_weibo import route_dict as routes_weibo


def all_route_dict():
    # 注册路由
    r = route_dict()
    r.update(routes_todo())
    r.update(routes_weibo())
    return r
