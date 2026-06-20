import asyncio

class EventBus:
    def __init__(self) -> None:
        self._subscribers: list[asyncio.Queue] = []

    def subscribe(self) -> asyncio.Queue:
        queue: asyncio.Queue = asyncio.Queue()
        self._subscribers.append(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue) -> None:
        if queue in self._subscribers:
            self._subscribers.remove(queue)

    async def publish(self, message: dict) -> None:
        for subscriber in list(self._subscribers):
            try:
                subscriber.put_nowait(message)
            except asyncio.QueueFull:
                continue

event_bus = EventBus()