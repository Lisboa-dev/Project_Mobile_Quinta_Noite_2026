# infra/rabbitmq/publisher.py

import json
import aio_pika

class EventPublisher:

    def __init__(self, exchange):

        self.exchange = exchange

    async def publish(
        self,
        routing_key,
        payload
    ):

        message = aio_pika.Message(
            body=json.dumps(payload).encode()
        )

        await self.exchange.publish(
            message,
            routing_key=routing_key
        )
