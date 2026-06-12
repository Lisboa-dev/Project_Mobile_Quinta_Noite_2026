class CacheService:

    def __init__(
        self,
        redis_client,
        default_ttl: int
    ):
        self.redis = redis_client
        self.default_ttl = default_ttl

    async def set(
        self,
        key: str,
        value: str
    ):

        await self.redis.set(
            key,
            value,
            ex=self.default_ttl
        )