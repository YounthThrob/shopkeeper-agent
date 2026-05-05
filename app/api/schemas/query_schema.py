from pydantic import BaseModel

class QuerySchema(BaseModel):
    """
    查询参数
    """
    # 前端请求体中的query字段，用来承接用户输入的查询语句
    query: str