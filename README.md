# One UI-style Calculator

Fully vibe-coded desktop calculator for Windows/Android created using Gemini and Claude without subscriptions, styled after Samsung Calculator, featuring dark and light themes, a scientific mode, a converter, history with notes, and custom backgrounds. Built with Python (pywebview) using a single HTML file for the interface, it works completely offline and sends nothing to the internet.

## Features

### Calculator
- Standard operations: addition, subtraction, multiplication, division, parentheses, sign toggle, decimal comma.
- Samsung-style percentages (`100 + 10 %` = 110).
- **Live Preview**: the result is displayed in gray beneath the input before pressing "=".
- Custom expression parser without `eval`: safe and predictable. Division by zero and other errors display clear messages.
- Vertical (phone) and horizontal layouts; the window resizes dynamically.

### Scientific Mode
- sin, cos, tan and inverse functions, ln, log, √, ∛, exponentiation `^`, square and cube, factorial, π, e, absolute value.
- Degrees and radians toggle.

### History
- Slides out from the side without blocking the workspace; clicking outside closes the panel.
- Add custom notes to any entry.
- Clicking an expression inserts it back into the calculator.
- **Persistent storage between launches** (`history.json` file).

### Converter
- Multiple units categories, such as length and tips.
- **Dates mode**: calculate the exact days, months, and years between two dates.
- Convenient numeric keypad, semi-transparent background.

### Appearance and Settings
- Light and dark themes, custom accent color selection.
- Russian and English interface (switchable in settings).
- Custom background: choose any image from your computer.
- Sliders for panel and button transparency, and background dimming.
- Pin window on top.
- Settings are saved automatically.

### Clipboard
- Copy results or full calculations with a single click.

## Data Storage

Located in `%APPDATA%\SamsungCalculator`:
- `settings.json`: configuration, including the selected background image;
- `history.json`: calculation history and notes.

You can delete these files to reset the app. Error logs (`calculator_error.log` and `calculator_debug.log`) are stored next to the executable (or in the temporary folder if write access is restricted).

## Installation for Users

Download the installer SamCalculator1.1.exe for Windows 10/11 or SamCalculator.apk for Android from the **Releases** section. No Python or external libraries required: everything is bundled inside.

Requires **Windows 10 or 11** and **Microsoft Edge WebView2 Runtime**. It is pre-installed on Windows 11 and modern Windows 10 builds. If the window fails to open, install it from the Microsoft website.

## Building from Source

Requires Python 3.9+ and Windows.

```bat
pip install pywebview pyinstaller
pyinstaller --noconsole --onedir --clean --icon favicon.ico ^
  --add-data "samscalculator.html;." --add-data "favicon.ico;." ^
  --name SamsCalculator app.py
```

Alternatively, simply run `build.bat`. The compiled executable will appear in the `dist` folder.

To run without building: `python app.py`.

## Project Files

| File | Purpose |
|---|---|
| `app.py` | Window management, data persistence, always-on-top toggle, icon |
| `samscalculator.html` | Complete interface and calculation logic |
| `favicon.ico` | Application icon |
| `build.bat` | Exe build script |

## License

MIT License

Copyright (c) 2026 RelexUA

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Credits

Created with the help of Gemini and Claude. Special thanks for assistance to Larga https://github.com/Argosha
