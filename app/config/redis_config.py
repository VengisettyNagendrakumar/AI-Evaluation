from app.config.settings import settings


class RedisConfig:

    HOST = settings.REDIS_HOST

    PORT = settings.REDIS_PORT

    DB = 0

    DECODE_RESPONSES = True