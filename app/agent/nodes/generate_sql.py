"""
SQL 生成节点

负责根据用户问题和前面整理出的表结构 指标 日期 数据库环境生成候选 SQL。
本节点只生成 SQL，不做校验和执行，后续会交给 validate_sql 和 run_sql 继续处理。
"""
import yaml
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime

from ..context import DataAgentContext
from ..llm import llm
from ..state import DataAgentState
from ...core.log import logger
from ...prompt.prompt_loader import load_prompt

async def generate_sql(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    """ 基于已检索和过滤的上下文 生成SQL"""
    writer = runtime.stream_writer
    writer("生成 SQL")

    # 这些上下文你都是由前置节点完成的，模型只在给定表 字段 指标口径范围生成SQL
    table_infos=state["table_infos"]
    metric_infos=state["metric_infos"]
    date_info=state["date_info"]
    db_info=state["db_info"]
    query = state["query"]
    prompt = PromptTemplate(
        template=load_prompt("generate_sql"),
        input_variables=["query", "table_infos", "metric_infos", "date_info", "db_info"],
    )
    # SQL 生成节点只需要纯文本sql，不能要求模型输出json或者markdown代码块
    output_parser = StrOutputParser()
    chain = prompt | llm | output_parser

    result = await chain.ainvoke(
        {
            "query": query,
            "table_infos": yaml.dump(table_infos, allow_unicode=True, sort_keys=False),
            "metric_infos": yaml.dump(metric_infos, allow_unicode=True, sort_keys=False),
            "date_info": yaml.dump(date_info, allow_unicode=True, sort_keys=False),
            "db_info": yaml.dump(db_info, allow_unicode=True, sort_keys=False)
        }
    )
    logger.info(f"生成的SQL：{result}")
    return {"sql": result}
