from __future__ import annotations

import asyncio
import os
import re
import sys

from dataclasses import dataclass
from enum import IntEnum
from enum import auto
from glob import glob
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Protocol

import dearpygui.dearpygui as dpg

from html_style_enhancer.enhance import TODAY_DATE
from html_style_enhancer.enhance import enhance
from html_style_enhancer.enhance import generate_styling
from html_style_enhancer.log import LOGGER_FORMAT_STR
from html_style_enhancer.log import logger
from html_style_enhancer.settings import Settings


if TYPE_CHECKING:
    from typing import Any

WINDOW_WIDTH = 840
WINDOW_HEIGHT = 800


@dataclass(slots=True, kw_only=True)
class Configuration:
    input_file: str
    output_file: str
    selector: str
    font: str
    font_size: int
    font_color: str
    background_image: str
    today_date: str
    log_file: str
    test_mode: bool
    html_source_column: str
    html_source_modified_column: str


class ElementTag(IntEnum):
    OUTPUT_FILE = auto()
    SELECTOR = auto()
    FONT = auto()
    FONT_SIZE = auto()
    FONT_COLOR = auto()
    BACKGROUND_IMAGE = auto()
    SELECTED_DATA_FILE = auto()
    FILE_DIALOG = auto()
    STYLING_PREVIEW = auto()


# ? Attributes of GUI that we want to pass around DearPyGUI elements
class StatefulData(Protocol):
    configuration: Configuration


@dataclass(slots=True)
class GUI:
    configuration: Configuration

    def file_selected(self, sender: str, app_data: dict[str, dict[str, str]]):
        logger.info("Selecting ... ")
        dpg.set_value(
            ElementTag.SELECTED_DATA_FILE,
            Path(list(app_data["selections"].values())[0]).name,
        )
        self.configuration.input_file = list(app_data["selections"].values())[0]
        logger.success(f"File selected: {self.configuration.input_file}")

    def update_styling_preview(self):
        """Update the styling preview text field with current settings"""
        try:
            output_file = dpg.get_value(ElementTag.OUTPUT_FILE)
            selector = dpg.get_value(ElementTag.SELECTOR)
            font = dpg.get_value(ElementTag.FONT)
            font_size = int(dpg.get_value(ElementTag.FONT_SIZE))
            font_color = dpg.get_value(ElementTag.FONT_COLOR)
            background_image = dpg.get_value(ElementTag.BACKGROUND_IMAGE)

            # Convert color picker values to rgb format
            font_color_rgb = (
                f"rgb({int(font_color[0])},{int(font_color[1])},{int(font_color[2])})"
            )

            # Create temporary settings for preview
            temp_settings = Settings(
                test_mode=self.configuration.test_mode,
                log_file=self.configuration.log_file,
                input_file=self.configuration.input_file,
                output_file=output_file,
                selector=selector,
                font=font,
                font_size=font_size,
                font_color=font_color_rgb,
                background_image=background_image,
                html_source_column=self.configuration.html_source_column,
                html_source_modified_column=self.configuration.html_source_modified_column,
            )

            styling = f'<div style="width:100%;margin:0 auto;{generate_styling(temp_settings)}"></div>'
            dpg.set_value(ElementTag.STYLING_PREVIEW, styling)
        except (ValueError, TypeError):
            dpg.set_value(ElementTag.STYLING_PREVIEW, "Invalid settings")

    def create(self, font: str):
        if not os.path.exists(self.configuration.input_file):
            self.configuration.input_file = glob("INPUT_*.xlsx")[0]

        with dpg.file_dialog(
            directory_selector=False,
            show=False,
            callback=self.file_selected,
            tag=ElementTag.FILE_DIALOG,
            height=540,
            width=720,
        ):
            dpg.add_file_extension(".xlsx", color=(255, 255, 0, 255))
            dpg.add_file_extension(".csv", color=(255, 0, 255, 255))

        dpg.add_button(
            label="Choose the input file",
            callback=lambda: dpg.show_item(ElementTag.FILE_DIALOG),
        )
        dpg.add_text(
            tag=ElementTag.SELECTED_DATA_FILE,
            default_value=self.configuration.input_file,
            color=(255, 0, 0, 255),
        )

        with dpg.group(width=WINDOW_WIDTH - 40):
            dpg.add_text("Output File Name")
            dpg.add_input_text(
                default_value=self.configuration.output_file,
                tag=ElementTag.OUTPUT_FILE,
                callback=lambda: self.update_styling_preview(),
            )

            dpg.add_text("Selector")
            dpg.add_input_text(
                default_value=self.configuration.selector,
                tag=ElementTag.SELECTOR,
                callback=lambda: self.update_styling_preview(),
            )

            dpg.add_text("Font")
            dpg.add_input_text(
                default_value=self.configuration.font,
                tag=ElementTag.FONT,
                callback=lambda: self.update_styling_preview(),
            )

            dpg.add_text("Font Size")
            dpg.add_input_text(
                default_value=str(self.configuration.font_size),
                tag=ElementTag.FONT_SIZE,
                callback=lambda: self.update_styling_preview(),
            )

        with dpg.group(width=WINDOW_WIDTH // 2):
            dpg.add_text("Font Color")
            r, g, b = re.findall(
                r"rgb\((\d+),\s*(\d+),\s*(\d+)\)", self.configuration.font_color
            )[0]
            r, g, b = int(r), int(g), int(b)
            dpg.add_color_picker(
                default_value=(r, g, b, 0),
                tag=ElementTag.FONT_COLOR,
                callback=lambda: self.update_styling_preview(),
            )

        with dpg.group(width=WINDOW_WIDTH - 46):
            dpg.add_text("Background Image URL")
            dpg.add_input_text(
                default_value=self.configuration.background_image,
                tag=ElementTag.BACKGROUND_IMAGE,
                callback=lambda: self.update_styling_preview(),
            )

            dpg.add_text("Generated Styling Preview")
            with dpg.child_window(
                width=WINDOW_WIDTH - 40,
                height=100,
                autosize_x=False,
                autosize_y=False,
                border=True,
            ):
                dpg.add_text(
                    default_value="",
                    tag=ElementTag.STYLING_PREVIEW,
                    wrap=WINDOW_WIDTH - 40,
                )

        # Initialize the styling preview
        self.update_styling_preview()

        dpg.add_button(
            label="Proceed",
            callback=proceed_callback,
            user_data=self,
        )

        dpg.bind_font(font)


async def run(settings: Settings) -> None:
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

    configuration = Configuration(
        input_file=settings.input_file,
        output_file=settings.output_file,
        selector=settings.selector,
        font=settings.font,
        font_size=settings.font_size,
        font_color=settings.font_color,
        background_image=settings.background_image,
        today_date=TODAY_DATE,
        log_file=settings.log_file,
        test_mode=settings.test_mode,
        html_source_column=settings.html_source_column,
        html_source_modified_column=settings.html_source_modified_column,
    )
    gui = GUI(configuration)
    logger.info(f"Today's date: <blue>{configuration.today_date}</blue>")

    dpg.create_context()

    font: Any
    with dpg.font_registry(tag="korean"):
        with dpg.font("NanumBarunGothic.otf", 18) as font:  # type: ignore
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Default)
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Korean)
            dpg.add_font_range(0x3100, 0x3FF0)
            dpg.add_font_chars([0x3105, 0x3107, 0x3108])
            dpg.add_char_remap(0x3084, 0x0025)

    with dpg.window(tag="Primary Window", autosize=True):
        gui.create(font)  # type: ignore

    dpg.create_viewport(
        title="HTML Style Enhancer",
        width=WINDOW_WIDTH,
        height=WINDOW_HEIGHT,
        small_icon="icon.ico",
        large_icon="icon.ico",
    )
    dpg.setup_dearpygui()
    dpg.show_viewport()

    dpg.set_primary_window("Primary Window", True)
    dpg.start_dearpygui()
    dpg.destroy_context()


def proceed_callback(sender: Any, app_data: Any, stateful: StatefulData):
    output_file: str = dpg.get_value(ElementTag.OUTPUT_FILE)
    selector: str = dpg.get_value(ElementTag.SELECTOR)
    font: str = dpg.get_value(ElementTag.FONT)
    font_size: str = dpg.get_value(ElementTag.FONT_SIZE)
    font_color: str = dpg.get_value(ElementTag.FONT_COLOR)
    background_image: str = dpg.get_value(ElementTag.BACKGROUND_IMAGE)

    font_color = f"rgb({int(font_color[0])},{int(font_color[1])},{int(font_color[2])})"

    logger.info(f"Output File Name: <blue>{output_file}</blue>")
    logger.info(f"Selector: <blue>{selector}</blue>")
    logger.info(f"Font: <blue>{font}</blue>")
    logger.info(f"Font Size: <blue>{font_size}</blue>")
    logger.info(f"Font Color: <blue>{font_color}</blue>")
    logger.info(f"Background Image URL: <blue>{background_image}</blue>")

    settings = Settings(
        test_mode=stateful.configuration.test_mode,
        log_file=stateful.configuration.log_file,
        input_file=stateful.configuration.input_file,
        output_file=output_file,
        selector=selector,
        font=font,
        font_size=int(font_size),
        font_color=font_color,
        background_image=background_image,
        html_source_column=stateful.configuration.html_source_column,
        html_source_modified_column=stateful.configuration.html_source_modified_column,
    )

    asyncio.run(enhance(settings))
