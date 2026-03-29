from functools import lru_cache

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from procurebrain.config.settings import settings


@lru_cache(maxsize=1)
def get_mongo_client() -> AsyncIOMotorClient:
    return AsyncIOMotorClient(settings.mongodb_uri)


def get_database() -> AsyncIOMotorDatabase:
    return get_mongo_client()[settings.mongodb_db_name]


async def ping_mongo() -> bool:
    result = await get_database().command("ping")
    return bool(result.get("ok"))
