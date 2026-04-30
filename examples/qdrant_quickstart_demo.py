import asyncio
from qdrant_client import AsyncQdrantClient,models

QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "demo"
VECTOR_SIZE = 4

async def recreate_collection(client):
    # Delete collection if exists
    if await client.collection_exists(COLLECTION_NAME):
        await client.delete_collection(COLLECTION_NAME)

    # Create collection
    await client.create_collection(
        COLLECTION_NAME,
        vectors_config = models.VectorParams(size=VECTOR_SIZE, distance=models.Distance.COSINE),
    )
    print(f"1.创建集合{COLLECTION_NAME}")

async def add_vectors(client):
    collection_name = COLLECTION_NAME
    # Add vectors
    await client.upsert(
        collection_name,
        points = [
            models.PointStruct(
                id = 1,
                vector = [0.05, 0.61, 0.76, 0.74],
                payload = {"name": "订单分析","type":"report"},
            ),
            models.PointStruct(
                id = 2,
                vector = [0.19, 0.81, 0.86, 0.08],
                payload = {"name": "销量趋势","type":"metric"},
            ),
            models.PointStruct(
                id = 3,
                vector = [0.36, 0.53, 0.88, 0.24],
                payload = {"name": "区域销售额","type":"dimension"},
            )
        ]
    )
    print(f"2.添加3个向量点")

async def search_vectors(client):
    # Search
    query_vector =[0.2,0.1,0.9,0.7]
    result = await client.query_points(
        collection_name = COLLECTION_NAME,
        query= query_vector,
        limit=3,
        with_payload=True
    )
    print(f"3.查询向量{query_vector}")
    print("查询结果：")
    for i,point in enumerate(result.points,start=1):
        print(f"{i},id={point.id} ,score={point.score:.4f} ,payload={point.payload}")

async def main():
    client = AsyncQdrantClient(QDRANT_URL)
    try:
        await recreate_collection(client)
        await add_vectors(client)
        await search_vectors(client)
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())