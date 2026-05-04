from langgraph.graph import StateGraph,START
from .state import DataAgentState
from .context import DataAgentContext

graph_bulider = StateGraph(DataAgentState,DataAgentContext)

# 注册节点：每个节点负责问数链路中的一个清晰步骤
graph_builder.add_node("extract_keywords", extract_keywords)
graph_builder.add_node("recall_column", recall_column)
graph_builder.add_node("recall_value", recall_value)
graph_builder.add_node("recall_metric", recall_metric)

# 从用户问题开始，先抽取关键词作为后续检索的基础
graph_builder.add_edge(START, "extract_keywords")

# 关键词抽取后并行进入三类召回，分别面向字段、字段值和业务指标
graph_builder.add_edge("extract_keywords", "recall_column")
graph_builder.add_edge("extract_keywords", "recall_value")
graph_builder.add_edge("extract_keywords", "recall_metric")

# 三路召回都完成后，再进入统一的信息合并节点
graph_builder.add_edge("recall_column", "merge_retrieved_info")
graph_builder.add_edge("recall_value", "merge_retrieved_info")
graph_builder.add_edge("recall_metric", "merge_retrieved_info")