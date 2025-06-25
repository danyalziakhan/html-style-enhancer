chcp 65001
@echo off
rem get current this batch file directory
set dir=%~dp0

CALL .venv\Scripts\activate
CALL .venv\Scripts\python run.py --gui --input_file "INPUT_FILE.xlsx" --output_file "RESULT.xlsx" --selector "div[style='width:100%%%%; margin:0 auto']" --html_source_column "상품상세설명\n[필수]" --html_source_modified_column "상품상세설명\n[사방넷]" --font Roboto --font_size 24 --font_color "rgb(112, 69, 69)" --background_image "https://img.freepik.com/free-vector/network-mesh-wire-digital-technology-background_1017-27428.jpg?w=1380&t=st=1668158296~exp=1668158896~hmac=2a8f507f48081339e88a558d2edff0273c9b96098f1c222a533a636babc1996d"

pause