import asyncio

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine,async_sessionmaker

from ..conf.app_config import app_config,DBConfig

class MySQLClientManager:
    def __init__(self, db_config: DBConfig):
        # 数据库配置
        self.config = db_config
        # 创建数据库引擎
        self.engine : AsyncEngine | None = None
        # session_factory 用来按需创建新的AsyncSession
        self.session_factory = None

    def __get_url(self):
        # mysql+asyncmy 表示：连接MySQL，并使用asyncmy作为异步驱动
        return f"mysql+asyncmy://{self.config.user}:{self.config.password}@{self.config.host}:{self.config.port}/{self.config.database}?charset=utf8mb4"

    def init(self):
        # 创建数据库引擎,相当于先把“数据库连接能力”准备好
        self.engine = create_async_engine(self.__get_url(), pool_size = 10, pool_pre_ping = True)
        # 基于engine创建session_factory（会话工厂），后面真正查库时再拿一个session
        self.session_factory = async_sessionmaker(self.engine, autoflush=True,expire_on_commit = False)

    async def close(self):
        # 关闭数据库连接
        await self.engine.dispose()

# 一套连元素据库，一套连数仓模拟库
meta_mysql_client_manager = MySQLClientManager(app_config.db_meta)
dw_mysql_client_manager = MySQLClientManager(app_config.db_dw)

if __name__ == "__main__":
    # 这里演示的是数仓库查询，所以先初始化 dw 这一套客户端
    dw_mysql_client_manager.init()


    async def test():
        # 通过 session_factory 创建一次数据库会话
        async with dw_mysql_client_manager.session_factory() as session:
            sql = "select * from fact_order limit 10"
            # text(sql) 表示把原生 SQL 语句交给 SQLAlchemy 执行
            result = await session.execute(text(sql))

            # mappings().fetchall() 会把结果转成“按列名访问”的行对象列表
            rows = result.mappings().fetchall()

            # 下面三行只是为了帮助观察返回结果的结构
            print(type(rows))
            print(type(rows[0]))
            print(rows[0]["order_id"])


    asyncio.run(test())