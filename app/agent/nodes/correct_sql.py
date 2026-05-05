"""
SQL 修正节点

负责在 SQL 校验失败后，结合原问题 原 SQL 数据库错误和完整上下文做最小必要修正
只有 validate_sql 写入错误信息时，LangGraph 才会进入这个分支
"""
import yaml
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime

from ..context import DataAgentContext
from ..llm import llm
from ..state import DataAgentState
from ...prompt.prompt_loader import load_prompt
from ...core.log import logger

async def correct_sql(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    """根据校验错误修正 SQL 语句"""
    writer = runtime.stream_writer
    writer("修正 SQL")

    # 校验 sql 也需要完整的上下文，避免模型只根据报错修改语法而丢失业务意义
    query = state["query"]
    table_infos= state["table_infos"]
    metric_infos = state["metric_infos"]
    db_info = state["db_info"]
    date_info = state["date_info"]

    # 报错信息
    error = state["error"]
    sql = state["sql"]

    prompt = PromptTemplate(
        template=load_prompt("correct_sql"),
        input_variables=["query", "table_infos", "metric_infos", "db_info", "date_info", "error", "sql"],
    )

    # 输出的sql依然是字符串
    output_parser = StrOutputParser()
    chain = prompt | llm | output_parser
    result = await chain.ainvoke(
        {
            "query": query,
            "table_infos": yaml.dump(table_infos, allow_unicode=True, sort_keys=False),
            "metric_infos": yaml.dump(metric_infos, allow_unicode=True, sort_keys=False),
            "db_info": yaml.dump(db_info, allow_unicode=True, sort_keys=False),
            "date_info": yaml,
            "error": error,
            "sql": sql,
        }
    )

    logger.info(f"修正后的SQL：{result}")
    return {"sql": result}
