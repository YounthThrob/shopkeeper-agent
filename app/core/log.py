import sys
from loguru import logger
from pathlib import Path
from ..conf.app_config import app_config
from context import request_id_ctx_var


# 统一日志格式，包含时间，级别，请求id和调用位置等关键信息
log_format ={
    "<green>{time:YYYY-MM-DD HH:mm:sss.SSS}</green> |"
    "<level>{level: <8}</level> |"
    "<magenta>request_id - {extrap[request_id]}</magenta> |"
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> -"
    "<level>{message}</level>"
}


# 通过Loguru patch 钩子 把上下文中的request_id写入每条日志的extra字段
def inject_request_id(record):
    request_id = request_id_ctx_var.get()
    record["extra"]["request_id"] = request_id


# 移除Logru 默认的输出目标，避免和项目自定义配置重复打印
logger.remove()

# 生成带 request_id 注入能力的日志格式 ，后续业务统一使用
logger = logger.patch(inject_request_id)

# 根据配置决定是否输出控制台日志，适合本地开发和容器标准输出采集
if app_config.logging.console.enable:
    logger.add(sinks =sys.stdout, level=app_config.logging.console.level, format=log_format)

# 根据配置决定是否写入文件日志，并在启动时确保日志目录存在
if app_config.logging.file.enable:
    path = Path(app_config.logging.file.path)
    path.mkdir(parents=True, exist_ok=True)
    logger.add(
        sink=path / "app.log",
        level=app_config.logging.file.level,
        format=log_format,
        rotation=app_config.logging.file.rotation,
        retention=app_config.logging.file.retention,
        encoding="utf-8",
    )