from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv
from omegaconf import OmegaConf
import os
load_dotenv(Path(__file__).parent.parent.parent / ".env")

# 文件日志配置，对应logging.file这一组参数
@dataclass
class File:
    enable: bool
    level: str
    path: str
    rotation: str
    retention: str

# 控制台日志配置，对应logging.console这一组参数
@dataclass
class Console:
    enable: bool
    level: str

# 把File 和 Console 组合起来，形成loggingConfig这一组参数
@dataclass
class LoggingConfig:
    file: File
    console: Console

# 数据库配置
@dataclass
class DBConfig:
    host: str
    port: int
    user: str
    password: str
    database: str

# qdrant 配置
@dataclass
class QdrantConfig:
    host: str
    port: int
    embedding_size: int

# Embedding 配置
@dataclass
class EmbeddingConfig:
    host: str
    port: int
    model: str

# ES 配置
@dataclass
class ESConfig:
    host: str
    port: int
    index: str

# LLM 配置
@dataclass
class LLMConfig:
    model_name: str
    api_key: str
    base_url: str

# AppConfig 配置 是整个项目的配置的总入口
# 这里的字段名，需要和app_config.yaml的顶层字段名一致
@dataclass
class AppConfig:
    logging: LoggingConfig
    db_meta: DBConfig
    db_dw: DBConfig
    qdrant: QdrantConfig
    embedding: EmbeddingConfig
    es: ESConfig
    llm: LLMConfig


# 从当前文件 app/conf/app_config.py 出发，回到项目根目录
# 再定位到 conf/app_config.yaml 这个配置文件
config_file = Path(__file__).parent.parent.parent / "conf" / "app_config.yaml"

# 加载配置文件
config = OmegaConf.load(config_file)

# 设置 OmegaConf 使用环境变量解析
OmegaConf.register_new_resolver("env", lambda x: os.environ.get(x, ""), replace=True)

# 根据AppConfig生成一份结构化配置 schema
schema = OmegaConf.structured(AppConfig)

# 把配置文件里的内容，映射到 schema 中，并返回一个结构化配置
app_config : AppConfig = OmegaConf.to_object(OmegaConf.merge(schema, config))

if __name__ == "__main__":
    print(app_config.es.host)