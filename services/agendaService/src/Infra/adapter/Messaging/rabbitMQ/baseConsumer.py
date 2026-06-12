# infra/rabbitmq/consumers/base_consumer.py

import json


class BaseConsumer:

    async def consume(self, message):

        async with message.process():

            payload = json.loads(
                message.body.decode()
            )

            await self.handle(payload)

    async def handle(self, payload):

        raise NotImplementedError