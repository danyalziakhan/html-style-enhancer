from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class Settings:
    test_mode: bool
    log_file: str
    input_file: str
    font: str
    font_size: int
    font_color: str
    background_image: str
    html_source_column: str
    html_source_modified_column: str
