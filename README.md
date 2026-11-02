# SamCalculator

A fast, clean calculator for **Windows** and **Android** with a modern phone-style look. Dark and light themes, scientific mode, unit converter, calculation history with notes, and your own background image. Written with Python (pywebview) around a single HTML interface. It works completely offline and sends nothing to the internet.

> Fully vibe-coded with Gemini and Claude, without subscriptions.

## Features

### Calculator
- Basic operations, parentheses, sign toggle, decimal point.
- Phone-style percentages (`100 + 10 %` = 110).
- **Live preview**: the result appears under the number before you press "=".
- **Cursor editing**: tap or drag across the number to move a cursor, then insert or delete digits anywhere in the expression.
- Custom expression parser without `eval`: safe and predictable, with clear error messages (for example, division by zero).
- Adjustable digit size for the number, the expression and the preview.

### Scientific mode
- sin, cos, tan and inverse functions, ln, log, √, ∛, power `^`, square and cube, factorial, π, e, absolute value.
- Degrees and radians switch.

### History
- Slides out in portrait layout; permanent column in landscape layout.
- Add a note to any entry, or delete a single entry (or clear everything).
- Click an expression to put it back into the calculator.
- Adjustable width: drag the divider in landscape layout, or use the slider for portrait layout.
- Saved between launches.

### Converter
- Length, temperature, weight, volume, data, speed, network speed (Mbit/s, MB/s and more), time, area and tips.
- **Dates mode**: days, months and years between two dates.
- Custom unit picker that matches the app design.

### Appearance
- Light and dark themes (or automatic), accent colour palette plus your own colour with an eyedropper.
- Custom background image, kept at full quality.
- Sliders for panel transparency, button transparency, panel blur, background dimming, icon size and digit size.
- English and Russian interface.

### Windows
- The layout adapts to any window size: it stays sharp, scales up on large monitors and shrinks without cutting anything off.
- The layout switches between portrait and landscape by itself when you stretch the window (can be turned off).
- Always-on-top option, window title bar that follows the app theme (Windows 11).
- Settings and history are saved automatically.

### Android
- Signed release APK. Landscape layout turns on automatically when you rotate the phone.
- Note field sits right above the keyboard; the Back button closes panels first.
- Fullscreen mode around the camera cutout, icon size slider.
- Optional app icon that follows the phone theme (light or dark).

## Data storage

Windows keeps its files in `%APPDATA%\SamCalculator`:
- `settings.json`: settings, including the selected background image;
- `history.json`: calculation history and notes.

Delete these files to reset the app. Error logs (`calculator_error.log`, `calculator_debug.log`) are stored next to the program, or in the temporary folder if writing there is not allowed.

## Installation

- **Windows:** download the installer (`SamCalculatorSetup.exe`) from the **Releases** section and run it. No Python or other libraries are required: everything is bundled.
- **Android:** download `SamCalculator.apk` from **Releases**, open it on your phone and allow installation from this source. Updates install over the previous version.

Requirements for Windows: **Windows 10 or 11** and **Microsoft Edge WebView2 Runtime** (already included in Windows 11 and up-to-date Windows 10). If the window does not open, install WebView2 Runtime from Microsoft.

> Windows SmartScreen may show an "unknown publisher" warning because the app is not code-signed. Click **More info → Run anyway**.

## Building from source

### Windows
Requires Python 3.9+ and Windows.

```bat
pip install pywebview pyinstaller
pyinstaller --noconsole --onedir --clean --icon favicon.ico ^
  --add-data "samcalculator.html;." --add-data "favicon.ico;." ^
  --name SamCalculator app.py
```

Or just run `build.bat`. The program appears in `dist\SamCalculator`. To run without building: `python app.py`.

### Android
The project lives in the `android` folder (a thin native WebView wrapper around the same HTML file). The workflow `.github/workflows/android.yml` builds a signed release APK on GitHub; the signing key is taken from repository secrets.

## Project files

| File | Purpose |
|---|---|
| `app.py` | Window, data storage, always-on-top, icon, title bar colour |
| `samcalculator.html` | The whole interface and calculation logic (used on Windows and Android) |
| `favicon.ico` | Windows icon |
| `build.bat` | Windows build script |
| `android/` | Android app project |
| `.github/workflows/android.yml` | Automatic APK build |

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
