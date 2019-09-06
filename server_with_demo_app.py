from demo_app import all_route_dict
from framework.server import run

if __name__ == '__main__':
    # 生成配置并且运行程序
    config = dict(
        host='localhost',
        port=3000,
    )
    run(host='localhost', port=3000, route=all_route_dict())

