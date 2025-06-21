# HTML Style Enhancer

A Python-based tool to enhance raw HTML content embedded in Excel files with custom CSS styling, fonts, colors, and background images.  
Ideal for post-processing scraped content to improve its presentation for platforms or e-commerce sites.

Supports both a **graphical user interface (GUI)** built with [DearPyGui](https://github.com/hoffstadt/DearPyGui) and a fully **automatable CLI** for advanced workflows.

---

## ✨ Features

- 📄 Read HTML from Excel files (`.xlsx`)
- 🎨 Apply background images, fonts, font sizes, and text colors via CSS
- 💾 Output modified HTML into a new column in the same or new file
- 🖥️ User-friendly GUI interface with font/color pickers and file selector
- ⚙️ Command-line interface for automation and scripting

---

## 📦 Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/danyalziakhan/html-style-enhancer.git
   cd html-style-enhancer
   ```

2. Install uv package manager:

   ```bash
   # On macOS and Linux.
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

   ```bash
   # On Windows.
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

   Or, from [PyPI](https://pypi.org/project/uv/):

   ```bash
   # With pip.
   pip install uv
   ```

   ```bash
   # Or pipx.
   pipx install uv
   ```

3. Create virtual environment and install dependencies via `pyproject.toml` using `uv`:

   ```bash
   uv sync
   ```

---

## 🚀 Usage

### ✅ CLI Mode

Use when you want to script or automate the process:

```bash
python run.py \
  --input_file INPUT_FILE.xlsx \
  --html_source_column "상품상세설명\n[필수]" \
  --html_source_modified_column "상품상세설명\n[사방넷]" \
  --font Roboto \
  --font_size 24 \
  --font_color "rgb(112, 69, 69)" \
  --background_image "https://example.com/image.jpg"
```

Or use the provided batch file on Windows:

```bash
run.bat
```

> Note: Ensure you replace `INPUT_FILE.xlsx` with your actual Excel file name and update other parameters if needed.

---

### 🖼️ GUI Mode

Launch a full GUI with file selectors, color pickers, and font dropdowns:

```bash
python run.py --gui \
  --input_file INPUT_FILE.xlsx \
  --html_source_column "상품상세설명\n[필수]" \
  --html_source_modified_column "상품상세설명\n[사방넷]" \
  --font Roboto \
  --font_size 24 \
  --font_color "rgb(112, 69, 69)" \
  --background_image "https://example.com/image.jpg"
```

Or simply run:

```bash
run_gui.bat
```

> The arguments passed to `run.py` are still required in GUI mode as initial defaults, but they can be modified interactively within the GUI.

---

## 🗂 Output

- Modified Excel files are saved in `output/YYYYMMDD/`
- Temporary data and logs are saved in `temp/YYYYMMDD/` and `logs/YYYYMMDD.log`

---

## 🧪 Example Output

Before:

```html
<div>
  <h1>Product A</h1>
  <p>This is a scraped description.</p>
</div>
```

After:

```html
<div
  style="background-image: url('https://example.com/image.jpg'); font-family: Roboto; font-size: 24px; color: rgb(112, 69, 69); padding: 20px;"
>
  <div>
    <h1>Product A</h1>
    <p>This is a scraped description.</p>
  </div>
</div>
```

---

## 🛠 Requirements

- Python 3.10 or 3.11
- Dependencies defined in `pyproject.toml` under `[project]`

---

## 📁 Project Structure

```
html-style-enhancer/
│
├── run.py                 # Main entry point
├── run.bat               # Windows CLI starter
├── run_gui.bat           # Windows GUI starter
├── pyproject.toml
├── README.md
│
└── html_style_enhancer/
    ├── gui.py
    ├── non_gui.py
    ├── enhance.py
    ├── settings.py
    └── log.py
```

---

## 🤝 License

MIT License. Feel free to use or modify this project in personal or commercial work. Contributions welcome.
