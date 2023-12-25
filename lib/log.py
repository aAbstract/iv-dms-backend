import os
from datetime import datetime
import colorama
from models.logs import Log
from database.mongo_driver import get_database


_LOG_TAG_COLOR_MAP = {
    'ERROR': f"{colorama.Back.RED}[ERROR]{colorama.Style.RESET_ALL}",
    'INFO': '[INFO]',
    'DEBUG': '[DEBUG]',
}


def _format_log(log: Log):
    return f"[{log.datetime.strftime('%Y-%m-%d %H:%M:%S')}] {_LOG_TAG_COLOR_MAP[log.level]} [{log.source}] {log.description}"


async def add_log(source: str, level: str, desc: str):
    log = Log(
        datetime=datetime.now(),
        level=level,
        source=source,
        description=desc
    )

    formated_log = _format_log(log)
    print(formated_log)
    if os.environ['ENV'] == 'prod':
        await get_database().get_collection('logs').insert_one(log.model_dump())
