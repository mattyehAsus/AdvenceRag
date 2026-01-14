import asyncio
import contextlib
from collections.abc import AsyncGenerator
from typing import Any


class StreamWrapper:
    def __init__(self, source_gen: AsyncGenerator, heartbeat_interval: float = 10.0):
        self.source_gen = source_gen
        self.interval = heartbeat_interval
        self.queue = asyncio.Queue()
        self.done = asyncio.Event()

    async def _consume_source(self):
        """生產者：負責讀取原始生成器並放入 Queue"""
        try:
            async for item in self.source_gen:
                await self.queue.put(item)
        except Exception as e:
            await self.queue.put(RuntimeError(f"Stream Error: {e}"))
        finally:
            self.done.set()

    async def iterate(self) -> AsyncGenerator[Any, None]:
        """消費者：封裝了 Queue 讀取與心跳邏輯的迭代器"""
        # 啟動背景生產者任務
        task = asyncio.create_task(self._consume_source())

        try:
            while not self.done.is_set() or not self.queue.empty():
                try:
                    # 在超時時間內嘗試獲取資料
                    item = await asyncio.wait_for(self.queue.get(), timeout=self.interval)

                    # 如果抓到的是異常物件，則拋出
                    if isinstance(item, Exception):
                        raise item
                    yield item

                except asyncio.TimeoutError:
                    # 觸發心跳：yield 一個特殊的標記或 None，交給外部處理
                    if not self.done.is_set():
                        yield ":ping"  # 這裡傳回 :ping 標記
        finally:
            if not task.done():
                task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await task
