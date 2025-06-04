TORTOISE_ORM = {
    # 连接信息
    "connections": {
        "default": {
            "engine": "tortoise.backends.mysql",
            'credentials': {
                'host': 'nj-cdb-kxg7ixmv.sql.tencentcdb.com',
                'port': '63975',
                'user': 'root',
                'password': '$XjcTkbeVye@BEe#PRkINU,PHm1KVRL1QwCx',
                'database': 'core-manager',
                'minsize': 1,
                'maxsize': 5,
                'charset': 'utf8mb4',
                "echo": True
            }
        },
        "secondary": {
            "engine": "tortoise.backends.mysql",
            'credentials': {
                'host': '127.0.0.1',
                'port': '3306',
                'user': 'root',
                'password': 'qz666888',
                'database': 'core-manager',
                'minsize': 1,
                'maxsize': 5,
                'charset': 'utf8mb4',
                "echo": True
            }
        },
        "prod": {
            "engine": "tortoise.backends.mysql",
            'credentials': {
                'host': '127.0.0.1',
                'port': '8806',
                'user': 'root',
                'password': 'qz666888',
                'database': 'core-manager',
                'minsize': 1,
                'maxsize': 5,
                'charset': 'utf8mb4',
                "echo": True
            }
        }
    },
    "apps": {
        "models": {
            # 把需要的模型导进一个module 直接使用module
            "models": ["core.server.entity", "aerich.models"],
            "default_connection": "default",
        },
    },
    'use_tz': False,
    'timezone': 'Asia/Shanghai',
}
