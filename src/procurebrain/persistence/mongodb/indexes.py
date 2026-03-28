from procurebrain.persistence.mongodb.client import get_database
from procurebrain.persistence.mongodb.collections import CHAT_SESSIONS, MESSAGES


async def ensure_indexes() -> None:
    db = get_database()
    await db[CHAT_SESSIONS].create_index("updated_at")
    await db[CHAT_SESSIONS].create_index("user_id")
    await db[MESSAGES].create_index("chat_id")
    await db[MESSAGES].create_index("created_at")
