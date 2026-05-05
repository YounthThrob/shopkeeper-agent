import json

from langchain_huggingface import HuggingFaceEndpointEmbeddings
from ..agent.context import DataAgentContext
from ..agent.graph import graph
from ..agent.state import DataAgentState
from ..repositories.es.value_es_repository import ValueESRepository
from ..repositories.mysql.dw.dw_mysql_repository import DWMySQLRepository
from ..repositories.mysql.meta.meta_mysql_repository import MetaMySQLRepository
from ..repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository
from ..repositories.qdrant.metric_qdrant_repository import MetricQdrantRepository

class QueryService:
    """
    查询服务
    """
    def __init__(
            self,
            meta_mysql_repository: MetaMySQLRepository,
            dw_mysql_repository: DWMySQLRepository,
            column_qdrant_repository: ColumnQdrantRepository,
            metric_qdrant_repository: MetricQdrantRepository,
            value_es_repository: ValueESRepository,
            embedding_client: HuggingFaceEndpointEmbeddings,
    ):
        """
        初始化查询服务
        """
        # MySQL 仓储，负责按 id 补齐字段、表、主外键信息\
        self.meta_mysql_repository = meta_mysql_repository
        # 数据仓库仓储，
        self.dw_mysql_repository = dw_mysql_repository

        # 召回链路依赖的向量检索、Embeding和全文检索能力由依赖层注入
        self.column_qdrant_repository = column_qdrant_repository
        self.metric_qdrant_repository = metric_qdrant_repository
        self.value_es_repository = value_es_repository
        self.embedding_client = embedding_client

    async def query(self, query: str):
        """
        执行查询
        """
        # State 只会被图节点读写和合并的业务数据,外部工具对象不塞进State
        state = DataAgentState(query= query)

        # context 保存本次图执行需要复用的外部依赖，节点通过runtime.context 读取
        context = DataAgentContext(
            column_qdrant_repository=self.column_qdrant_repository,
            embedding_client=self.embedding_client,
            metric_qdrant_repository=self.metric_qdrant_repository,
            value_es_repository=self.value_es_repository,
            meta_mysql_repository=self.meta_mysql_repository,
            dw_mysql_repository=self.dw_mysql_repository,
        )

        try:
            # stream_mode="custom" 对应节点内部 writer(...) 写出的进度消息
            async for chunk in graph.astream(
                    input=state,
                    context=context,
                    stream_mode="custom",
            ):
                # SSE 要求每条消息以 data: 开头，并以两个换行符结束
                # ensure_ascii=False 保留中文进度文案，default=str 兜底处理日期等非 JSON 类型
                yield f"data: {json.dumps(chunk, ensure_ascii=False, default=str)}\n\n"
        except Exception as e:
            # 流式接口已经开始返回后不能再改 HTTP 状态码，因此把异常也包装成一条 SSE 消息
            error = {"type": "error", "message": str(e)}
            yield f"data: {json.dumps(error, ensure_ascii=False, default=str)}\n\n"
