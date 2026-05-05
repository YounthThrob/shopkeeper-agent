"""
SQL 校验节点

负责在真正执行查询前，用数据库解析一次生成的 SQ
校验结果不在这里决定流程走向，而是通过 state["error"] 交给 graph.py 的条件边判断
"""

from langgraph.runtime import Runtime
from ..context import DataAgentContext
from ..state import DataAgentState
from ...core.log import logger
from ...repositories.mysql.dw.dw_mysql_repository import DWMySQLRepository

async def validate_sql(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    """校验 SQL,并返回erro 字段控制后续条件分支"""
    writer = runtime.stream_writer
    writer("校验 SQL")

    # 读取 generate_sql 或 correct_sql 生成的 SQL
    sql = state["sql"]

    # SQL可用性交给真实数据仓判断，这里从运行时上下文取DWMySQLRepository
    dw_mysql_repository: DWMySQLRepository = runtime.context["dw_mysql_repository"]

    try:
        # validate 内部使用 explain<sql>,只关心数据库能否成功解析这条sql
        await dw_mysql_repository.validate(sql)
        logger.info(f"SQL {sql} 语法可用")
        return {"error": None}
    except Exception as e:
        logger.error(f"SQL {sql} 语法错误：{e}")
        return {"error": str(e)}
