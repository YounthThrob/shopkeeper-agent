# Shopkeeper Agent

Shopkeeper Agent 是一个面向电商数据分析场景的自然语言问数服务。用户输入中文问题后，系统会通过 LangGraph 编排智能体流程，召回相关字段、字段取值和业务指标，生成 SQL，校验 SQL，并在数据仓库中执行查询，最终通过 SSE 流式返回执行过程和结果。

项目内置了一套电商示例数仓，包括地区、客户、商品、日期和订单事实表，适合用来演示“问一句业务问题，自动生成并执行 SQL”的完整链路。

## 功能特性

- 自然语言到 SQL 的问数接口
- 基于 LangGraph 的多节点 Agent 工作流
- 字段和指标的向量召回
- 字段真实取值的 Elasticsearch 全文召回
- 元数据配置化构建，支持表、字段、别名、指标定义
- FastAPI SSE 流式响应
- Docker Compose 一键启动 MySQL、Qdrant、Elasticsearch、Kibana 和 Embedding 服务

## 技术栈

- Python 3.10+
- FastAPI
- LangGraph / LangChain
- DeepSeek-compatible LLM API
- MySQL 8.0
- Qdrant
- Elasticsearch 8
- Hugging Face Text Embeddings Inference
- uv

## 项目结构

```text
.
├── app
│   ├── agent              # LangGraph 问数智能体、状态和节点
│   ├── api                # FastAPI 路由、依赖和生命周期管理
│   ├── clients            # MySQL、Qdrant、ES、Embedding 客户端管理
│   ├── conf               # 应用配置加载
│   ├── entities           # 业务实体
│   ├── models             # SQLAlchemy ORM 模型
│   ├── repositories       # MySQL、Qdrant、ES 数据访问层
│   ├── scripts            # 元数据知识库构建脚本
│   └── services           # 查询服务和元数据构建服务
├── conf
│   ├── app_config.yaml    # 应用运行配置
│   └── meta_config.yaml   # 表、字段、指标元数据配置
├── docker                 # 本地依赖服务和初始化 SQL
├── prompts                # Agent 节点使用的提示词模板
├── main.py                # FastAPI 应用入口
└── pyproject.toml
```

## 环境准备

### 1. 安装依赖

本项目使用 `uv` 管理 Python 依赖：

```bash
uv sync
```

### 2. 配置环境变量

在项目根目录创建或修改 `.env`：

```env
DB_PASSWORD=123456
LLM_API_KEY=your_llm_api_key
```

`conf/app_config.yaml` 默认读取这些环境变量：

- `DB_PASSWORD`：MySQL root 用户密码
- `LLM_API_KEY`：大模型 API Key

如需修改数据库、Qdrant、Elasticsearch、Embedding 或 LLM 地址，可调整 `conf/app_config.yaml`。

### 3. 启动基础设施

进入 `docker` 目录并启动服务：

```bash
cd docker
docker compose up -d
```

启动后默认服务地址：

| 服务 | 地址 |
| --- | --- |
| MySQL | `localhost:3306` |
| Qdrant | `localhost:6333` |
| Elasticsearch | `localhost:9200` |
| Kibana | `localhost:5601` |
| Embedding | `localhost:8081` |

Docker 会自动执行 `docker/mysql` 下的初始化 SQL，创建示例 `meta` 和 `dw` 数据库。

## 构建元数据知识库

基础设施启动后，需要把 `conf/meta_config.yaml` 中的表、字段、指标信息同步到 MySQL、Qdrant 和 Elasticsearch：

```bash
uv run python -m app.scripts.build_meta_knowledge -c conf/meta_config.yaml
```

该脚本会依次完成：

- 将表信息、字段信息写入 `meta` 数据库
- 从 `dw` 数据库读取字段类型和示例值
- 将字段元数据写入 Qdrant 向量集合
- 将配置为 `sync: true` 的字段取值写入 Elasticsearch
- 将指标信息和指标依赖字段写入 `meta` 数据库
- 将指标元数据写入 Qdrant 向量集合

## 启动应用

在项目根目录运行：

```bash
uv run fastapi dev main.py
```

或使用 Uvicorn：

```bash
uv run uvicorn main:app --reload
```

默认访问地址：

- API 文档：`http://127.0.0.1:8000/docs`
- 查询接口：`POST http://127.0.0.1:8000/api/query`

## 调用示例

接口使用 SSE 流式返回，示例请求：

```bash
curl -N -X POST "http://127.0.0.1:8000/api/query" \
  -H "Content-Type: application/json" \
  -d "{\"query\":\"统计华北地区的销售总额\"}"
```

请求体格式：

```json
{
  "query": "统计华北地区的销售总额"
}
```

响应会以 `text/event-stream` 形式逐段返回 Agent 执行过程，例如关键词抽取、字段召回、指标召回、SQL 生成、SQL 执行结果等。

## 问数流程

当前 Agent 流程由 `app/agent/graph.py` 编排：

```text
用户问题
  ↓
抽取关键词
  ↓
并行召回字段、字段取值、指标
  ↓
合并召回信息
  ↓
过滤候选表和候选指标
  ↓
补充 SQL 上下文
  ↓
生成 SQL
  ↓
校验 SQL
  ↓
必要时修正 SQL
  ↓
执行 SQL 并返回结果
```

## 元数据配置说明

`conf/meta_config.yaml` 用于描述问数系统可理解的数据资产。

表配置示例：

```yaml
tables:
  - name: fact_order
    role: fact
    description: 订单事实表
    columns:
      - name: order_amount
        role: measure
        description: 订单金额
        alias: [销售额, 订单金额, 收入]
        sync: false
```

指标配置示例：

```yaml
metrics:
  - name: GMV
    description: 所有订单成交金额的总和
    relevant_columns:
      - fact_order.order_amount
    alias: [成交总额, 订单总额]
```

字段中的 `sync` 控制是否把该字段的真实取值同步到 Elasticsearch，用于后续值召回。通常适合对地区、品类、品牌、会员等级等低基数字段开启。

## 常见问题

### Embedding 服务启动较慢

Embedding 容器需要加载 `docker/embedding/bge-large-zh-v1.5` 下的模型文件，首次启动可能需要等待一段时间。构建元数据知识库前，请确认 `http://localhost:8081` 已经可访问。

### 连接 MySQL 失败

检查 `.env` 中的 `DB_PASSWORD` 是否与 `docker/docker-compose.yaml` 中的 `MYSQL_ROOT_PASSWORD` 一致。当前 Docker 默认密码为 `123456`。

### LLM 调用失败

检查 `.env` 中的 `LLM_API_KEY` 是否已配置，并确认 `conf/app_config.yaml` 中的 `llm.base_url` 和 `llm.model_name` 与实际服务兼容。

### 修改元数据后没有生效

修改 `conf/meta_config.yaml` 后，需要重新执行：

```bash
uv run python -m app.scripts.build_meta_knowledge -c conf/meta_config.yaml
```

## 开发备注

- 日志配置位于 `conf/app_config.yaml` 的 `logging` 节点。
- Prompt 模板位于 `prompts` 目录。
- 查询接口依赖应用启动时初始化的外部客户端，见 `app/api/lifespan.py`。
- 元数据构建脚本会直接访问 MySQL、Qdrant、Elasticsearch 和 Embedding 服务，运行前需确保这些服务已启动。
