from typing import TypedDict

from ..entities.column_info import ColumnInfo
from ..entities.value_info import ValueInfo
from ..entities.metric_info import MetricInfo

class DataState(TypedDict):
    """
    一次问数链路中的核心状态
    """
    query: str # 用户输入的查询语句
    keywords : list[str]  # 抽取的关键字
    retrieved_column_infos: list[ColumnInfo] # 检索到的字段信息
    retrieved_metric_infos: list[MetricInfo] # 检索到的指标信息
    retrieved_value_infos: list[ValueInfo]  # 检索到的取值信息
    error: str # 检验sql时出现的错误信息


