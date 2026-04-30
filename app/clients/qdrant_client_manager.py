import asyncio
import random
from typing import Optional
from qdrant_client import AsyncQdrantClient,models
from ..conf.app_config import QdrantConfig,app_config

class QdrantClientManager:
    def __init__(self,qdrant_config: QdrantConfig):
        # 初始化配置对象
        self.qdrant_config = qdrant_config
        self.qdrant_client : Optional[AsyncQdrantClient] = None

    def __get_url(self):
        # 根据配置文件按拼出Qdrant的URL
        return f"http://{self.qdrant_config.host}:{self.qdrant_config.port}"

    def init(self):
        # 初始化Qdrant连接
        self.qdrant_client = AsyncQdrantClient(self.__get_url())

    async def close(self):
        # 关闭Qdrant连接
        await self.qdrant_client.close()

# 创建QdrantClientManager对象
# 后续项目中的模块中，需要使用QdrantClientManager对象，则直接引用该对象即可
qdrant_client_manager = QdrantClientManager(app_config.qdrant)

if __name__ == "__main__":
    # 测试代码
    # 先初始化客户端，后面的测试逻辑才能真正访问 Qdrant
    qdrant_client_manager.init()


    async def test():
        # 取出真正的 Qdrant 异步客户端
        client = qdrant_client_manager.qdrant_client

        # 如果集合不存在，就先创建一个集合
        if not await client.collection_exists("my_collection"):
            await client.create_collection(
                collection_name="my_collection",
                vectors_config=models.VectorParams(
                    # 当前集合中的向量维度是 10
                    size=10,
                    # 使用余弦相似度作为距离计算方式
                    distance=models.Distance.COSINE,
                ),
            )

        # 向集合中写入 100 个随机 point
        # 每个 point 都有一个 id 和一个 10 维向量
        await client.upsert(
            collection_name="my_collection",
            points=[
                models.PointStruct(
                    id=i,
                    vector=[random.random() for _ in range(10)],
                )
                for i in range(100)
            ],
        )

        # 用一个随机生成的查询向量做相似度检索
        # limit=10 表示最多返回 10 条结果
        # score_threshold=0.8 表示只保留分数不低于 0.8 的结果
        res = await client.query_points(
            collection_name="my_collection",
            query=[random.random() for _ in range(10)],  # type: ignore
            limit=10,
            score_threshold=0.8,
        )

        # 打印查询结果，便于观察 point 的 id、score 等信息
        print(res)

    # 运行异步测试函数
    asyncio.run(test())