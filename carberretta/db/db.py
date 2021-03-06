from os.path import isdir

from aiosqlite import connect
from apscheduler.triggers.cron import CronTrigger


class Database:
    def __init__(self, bot):
        self.bot = bot
        self.path = f"{self.bot._dynamic}/database.db3"
        self.build_path = f"{self.bot._static}/build.sql"
        self._calls = 0

        self.bot.scheduler.add_job(self.commit, CronTrigger(second=0))

    async def connect(self):
        if not isdir(self.bot._dynamic):
            # If cloned, this dir likely won't exist, so make it.
            from os import makedirs

            makedirs(self.bot._dynamic)

        self.cxn = await connect(self.path)
        await self.execute("pragma journal_mode=wal")
        await self.executescript(self.build_path)
        await self.commit()

    async def commit(self):
        await self.cxn.commit()

    async def close(self):
        await self.commit()
        await self.cxn.close()

    async def sync(self):
        await self.commit()

    async def field(self, command, *values):
        cur = await self.cxn.execute(command, tuple(values))
        self._calls += 1

        if (row := await cur.fetchone()) is not None:
            return row[0]

    async def record(self, command, *values):
        cur = await self.cxn.execute(command, tuple(values))
        self._calls += 1

        return await cur.fetchone()

    async def records(self, command, *values):
        cur = await self.cxn.execute(command, tuple(values))
        self._calls += 1

        return await cur.fetchall()

    async def column(self, command, *values):
        cur = await self.cxn.execute(command, tuple(values))
        self._calls += 1

        return [row[0] for row in await cur.fetchall()]

    async def execute(self, command, *values):
        await self.cxn.execute(command, tuple(values))
        self._calls += 1

    async def executemany(self, command, valueset):
        await self.cxn.executemany(command, valueset)
        self._calls += 1

    async def executescript(self, path, **kwargs):
        with open(path, "r", encoding="utf-8") as script:
            await self.cxn.executescript(script.read().format(**kwargs))

        self._calls += 1
