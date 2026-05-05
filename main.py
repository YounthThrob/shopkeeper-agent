from fastapi import FastAPI
from app.api.lifespan import lifespan
from app.api.routers import query_router

# lifespan 交给fastapi管理，用于在服务启动和关闭时统一初始化与释放外部客户端
app = FastAPI(lifespan=lifespan)
# 注册路由
app.include_router(query_router)
