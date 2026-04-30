import asyncio
from typing import Optional

from elasticsearch import AsyncElasticsearch
from ..conf.app_config import ESConfig,app_config

class ESClientManager:
    def __init__(self,es_config: ESConfig):
        # 保存ES配置对象,后面初始化客户端时会从这里读取host和port
        self.es_config = es_config
        self.es_client : Optional[AsyncElasticsearch] = None

    def __get_url(self):
        # 根据配置文件按拼出ES的URL
        return f"http://{self.es_config.host}:{self.es_config.port}"

    def init(self):
        # 初始化ES连接
        # hosts 之所以时列表，是为了兼容ES 常见的集群连接方式
        self.es_client = AsyncElasticsearch(hosts=[self.__get_url()])

    async def close(self):
        # 在程序退出时统一断开连接
        await self.es_client.close()

# 创建ESClientManager对象、
es_client_manager = ESClientManager(app_config.es)


if __name__ == "__main__":
    es_client_manager.init()

    async def test():
        client = es_client_manager.es_client

        if not await client.indices.exists(index="my-books"):
            await client.indices.create(
                index="my-books",
                mappings={
                    "dynamic": False,
                    "properties": {
                        "name": {"type": "text"},
                        "author": {"type": "text"},
                        "release_date": {"type": "date", "format": "yyyy-MM-dd"},
                        "page_count": {"type": "integer"},
                    },
                },
            )

        await client.bulk(
            operations=[
                {"index": {"_index": "my-books"}},
                {
                    "name": "Revelation Space",
                    "author": "Alastair Reynolds",
                    "release_date": "2000-03-15",
                    "page_count": 585,
                },
                {"index": {"_index": "my-books"}},
                {
                    "name": "1984",
                    "author": "George Orwell",
                    "release_date": "1985-06-01",
                    "page_count": 328,
                },
                {"index": {"_index": "my-books"}},
                {
                    "name": "Fahrenheit 451",
                    "author": "Ray Bradbury",
                    "release_date": "1953-10-15",
                    "page_count": 227,
                },
                {"index": {"_index": "my-books"}},
                {
                    "name": "Brave New World",
                    "author": "Aldous Huxley",
                    "release_date": "1932-06-01",
                    "page_count": 268,
                },
                {"index": {"_index": "my-books"}},
                {
                    "name": "The Handmaids Tale",
                    "author": "Margaret Atwood",
                    "release_date": "1985-06-01",
                    "page_count": 311,
                },
            ],
        )

        resp = await client.search(
            index="my-books",
            query={"match": {"name": "brave"}},
        )

        print(resp)

    try:
        asyncio.run(test())
    finally:
        asyncio.run(es_client_manager.close())


