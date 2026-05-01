import asyncio
from typing import Optional

from langchain_openai import OpenAIEmbeddings

from ..conf.app_config import app_config,EmbeddingConfig

class EmbeddingClientManager:
    def __init__(self,embedding_config: EmbeddingConfig):
        # 获取Embedding配置对象
        self.embedding_config = embedding_config
        self.embedding_client : Optional[OpenAIEmbeddings] = None

    def __get_url(self):
        # 根据配置文件按拼出Embedding的URL
        return f"http://{self.embedding_config.host}:{self.embedding_config.port}"

    def init(self):
        # 初始化Embedding连接
        self.embedding_client = OpenAIEmbeddings(
            openai_api_base=self.__get_url(),
            openai_api_key="mock-key",
            model=self.embedding_config.model,
            check_embedding_ctx_length=False
        )

# 模块级单例
embedding_client_manager = EmbeddingClientManager(app_config.embedding)

if __name__ == "__main__":
    # 本地调试入口：初始化客户端后执行一次最小化向量化调用
    embedding_client_manager.init()
    client = embedding_client_manager.embedding_client

    async def test():
        # 使用示例文本验证 Embedding 服务是否可正常响应
        text = "What is deep learning?"
        query_result = await client.aembed_query(text)
        # 只打印前 3 个维度，便于快速确认返回结果结构正确
        print(query_result[:3])

    # 运行调试测试
    asyncio.run(test())