from motor.motor_asyncio import AsyncIOMotorClient
from loguru import logger
from app.core.config import settings

client: AsyncIOMotorClient = None
db = None


async def connect_db():
    global client, db
    logger.info("Connecting to MongoDB...")
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]
    await db.resumes.create_index("session_id")
    await db.analyses.create_index("resume_id")
    logger.info("MongoDB connected successfully")


async def disconnect_db():
    global client
    if client:
        client.close()
        logger.info("MongoDB disconnected")


def get_db():
    return db
