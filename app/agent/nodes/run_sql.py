"""
SQL 执行节点

负责执行最终 SQL，并记录查询结果。
它是当前 SQL 闭环的结束节点，执行完成后流程进入 END。
"""

from langgraph.runtime import Runtime
from ..context import DataAgentContext
from ..state import DataAgentState
from ...core.log import logger

async def run_sql(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    """执行 SQL，并记录查询结果"""
    writer = runtime.stream_writer
    writer("执行 SQL")

    # 读取 generate_sql 或 correct_sql 生成的 SQL
    sql = state["sql"]

    # SQL可用性交给真实数据仓判断，这里从运行时上下文取DWMySQLRepository
    dw_mysql_repository = runtime.context["dw_mysql_repository"]

    # 执行 SQL
    result = await dw_mysql_repository.execute(sql)

    logger.info(f"SQL {sql} 执行结果：{result}")