import asyncio
import os

from argparse import ArgumentParser
from multiprocessing import freeze_support

from html_style_enhancer.enhance import TODAY_DATE
from html_style_enhancer.log import logger
from html_style_enhancer.settings import Settings


if __name__ == "__main__":
    freeze_support()

    parser = ArgumentParser()

    parser.add_argument(
        "--gui",
        help="Run the program in GUI mode",
        action="store_true",
    )
    parser.add_argument(
        "--test_mode",
        help="Run the program with verbose logging output",
        action="store_true",
    )
    parser.add_argument(
        "--log_file",
        help="Log file path which will override the default path",
        type=str,
        default=os.path.join("logs", f"{TODAY_DATE}.log"),
    )
    parser.add_argument(
        "--input_file",
        help="Input file",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--output_file",
        help="Output file",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--html_source_column",
        help="HTML Source Column",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--html_source_modified_column",
        help="HTML Source Modified Column",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--selector",
        help="CSS Selector of the element to apply styles",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--font",
        help="Font name",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--font_size",
        help="Font size",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--font_color",
        help="Font color",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--background_image",
        help="Background image",
        type=str,
        required=True,
    )
    args = parser.parse_args()

    os.makedirs(os.path.join("output", TODAY_DATE), exist_ok=True)
    os.makedirs(os.path.join("temp", TODAY_DATE), exist_ok=True)

    settings = Settings(
        test_mode=args.test_mode,
        log_file=args.log_file,
        input_file=args.input_file,
        output_file=args.output_file,
        selector=args.selector,
        font=args.font,
        font_size=args.font_size,
        font_color=args.font_color,
        background_image=args.background_image,
        html_source_column=args.html_source_column.replace("\\n", "\n"),
        html_source_modified_column=args.html_source_modified_column.replace(
            "\\n", "\n"
        ),
    )

    if args.gui:
        from html_style_enhancer.gui import run
    else:
        from html_style_enhancer.non_gui import run

    try:
        asyncio.run(run(settings))
    except Exception as err:
        logger.log("UNHANDLED ERROR", err)
        raise err from err

    logger.success("Program has been run successfully")
