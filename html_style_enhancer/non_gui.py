from __future__ import annotations

import sys

from typing import TYPE_CHECKING

from html_style_enhancer.log import LOGGER_FORMAT_STR
from html_style_enhancer.log import logger
from html_style_enhancer.enhance import enhance


if TYPE_CHECKING:
    from html_style_enhancer.settings import Settings


async def run(settings: Settings):
    logger.remove()
    if settings.test_mode:
        logger.add(
            sys.stderr,
            format=LOGGER_FORMAT_STR,
            level="DEBUG",
            colorize=True,
            enqueue=True,
        )
    else:
        logger.add(
            sys.stderr,
            format=LOGGER_FORMAT_STR,
            level="INFO",
            colorize=True,
            enqueue=True,
        )
    logger.add(
        settings.log_file,
        format=LOGGER_FORMAT_STR,
        enqueue=True,
        encoding="utf-8-sig",
        level="DEBUG",
    )

    await enhance(settings)
