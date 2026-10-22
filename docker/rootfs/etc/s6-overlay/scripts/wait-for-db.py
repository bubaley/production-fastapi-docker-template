"""Block until PostgreSQL accepts a connection with the app's SQL_* settings.

Gives up after DB_WAIT_TIMEOUT seconds (default 60). Reads the same variables and defaults
as app.core.settings without importing the app, so it does not depend on app code.
"""

import asyncio
import os
import sys
import time

import asyncpg


async def main() -> int:
    host = os.environ.get('SQL_HOST', 'localhost')
    port = int(os.environ.get('SQL_PORT', '5432'))
    timeout = float(os.environ.get('DB_WAIT_TIMEOUT', '60'))
    deadline = time.monotonic() + timeout
    while True:
        try:
            conn = await asyncpg.connect(
                host=host,
                port=port,
                user=os.environ.get('SQL_USER', 'postgres'),
                password=os.environ.get('SQL_PASSWORD', 'postgres'),
                database=os.environ.get('SQL_DATABASE', 'postgres'),
                timeout=5,
            )
        except Exception as exc:
            if time.monotonic() >= deadline:
                print(f'wait-for-db: {host}:{port} not ready after {timeout:.0f}s: {exc!r}', file=sys.stderr)
                return 1
            print(f'wait-for-db: {host}:{port} not ready ({type(exc).__name__}), retrying', file=sys.stderr)
            await asyncio.sleep(2)
        else:
            await conn.close()
            print(f'wait-for-db: {host}:{port} is ready')
            return 0


if __name__ == '__main__':
    sys.exit(asyncio.run(main()))
