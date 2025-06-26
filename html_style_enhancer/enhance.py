from __future__ import annotations

import os
import re

from datetime import datetime
from functools import cache
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Any

import pandas as pd

from aiofile import AIOFile
from bs4 import BeautifulSoup

from html_style_enhancer.excel import copy_dataframe_cells_to_excel_template
from html_style_enhancer.excel import get_column_mapping
from html_style_enhancer.log import logger


if TYPE_CHECKING:
    from html_style_enhancer.settings import Settings

TODAY_DATE = f"{datetime.now().strftime('%Y%m%d')}"


@cache
def compile_regex(r: str):
    return re.compile(r)


@cache
def parse_int(text: str) -> int:
    """
    Strips the non-numeric characters in a text and convert to int

    Will throw error if string has no digit
    """
    try:
        return int("".join(compile_regex(r"(\d)").findall(text)))
    except ValueError as e:
        raise ValueError(
            f"Text don't have any digit: '{text}', so it cannot be converted to int"
        ) from e


def get_html_sources(settings: Settings) -> list[str]:
    df = pd.read_excel(settings.input_file, dtype="str")

    for column in [
        settings.html_source_column,
        settings.html_source_modified_column,
    ]:
        try:
            df[column]
        except KeyError as e:
            error = f'"{column}" column is not present in file "{os.path.basename(settings.input_file)}"'
            raise KeyError(error) from e

    return df[settings.html_source_column].astype(str).tolist()


def generate_styling(settings: Settings):
    return f"""font-family:'{settings.font}';font-size:{settings.font_size}px;color:{settings.font_color};background-image:url('{settings.background_image}');background-repeat:no-repeat;background-position:center center;height:100%;"""


async def enhance(settings: Settings):
    logger.log("ACTION", f"Reading <blue>{settings.input_file}</> ...")

    html_sources = get_html_sources(settings)

    series_list: list[dict[str, str]] = []

    logger.log("ACTION", "Generating HTML Styling (it will take some time) ...")

    for idx, html_source in enumerate(html_sources, start=1):
        html_path = os.path.join("temp", TODAY_DATE, f"html_{idx}.html")
        os.makedirs(os.path.join("temp", TODAY_DATE), exist_ok=True)

        async with AIOFile(html_path, "w", encoding="utf-8") as f:
            await f.write(html_source)

        async with AIOFile(html_path, "r", encoding="utf-8") as f:
            document = BeautifulSoup(await f.read(), "html.parser")

        # ? First div element
        tag = document.select_one(settings.selector)
        if not tag:
            raise ValueError(
                f"Element not found in html using selector: {settings.selector}"
            )

        tag["style"] = f"{tag['style']};{generate_styling(settings)}"  # type: ignore

        childrens: Any = tag.children  # type: ignore
        for children in childrens:  # type: ignore
            children["style"] = f"{children['style']};color:inherit;"

        modified_html = str(document)

        async with AIOFile(html_path, "w", encoding="utf-8") as f:
            await f.write(modified_html)

        series: dict[str, str] = {
            settings.html_source_column: html_source,
            settings.html_source_modified_column: modified_html,
        }

        series_list.append(series)

    df = pd.DataFrame(series_list)

    output_filename = os.path.join("output", TODAY_DATE, settings.output_file)

    if os.path.exists(output_filename):
        os.remove(output_filename)

    df.to_excel(output_filename, engine="openpyxl", index=False)

    logger.log(
        "ACTION",
        f"Formatting {Path(output_filename).name} ... <yellow>(it may take a few seconds, so wait for it to be finished.)</>",
    )

    column_mapping = get_column_mapping(settings.input_file, output_filename)

    copy_dataframe_cells_to_excel_template(
        filename=output_filename,
        template_filename=os.path.abspath(settings.input_file),
        column_mapping=column_mapping,
    )

    logger.success(f"File saved to <CYAN><white>{output_filename}</></>")
