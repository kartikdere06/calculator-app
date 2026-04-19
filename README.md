# Calculator App

A colorful desktop calculator built with `Python` and `PySide6`.

This project includes:
- basic calculator mode
- scientific calculator mode
- calculation history
- answer memory (`ANS`)
- memory buttons (`MC`, `MR`, `MS`)
- grand total (`GT`)
- dark and light mode
- keyboard support

## Tech Stack

- `Python 3`
- `PySide6`
- `Git` and `GitHub`

## Features

- Basic operations: `+`, `-`, `*`, `/`
- Percentage support
- Repeated `=` behavior
- Brackets `(` and `)`
- Power `^`
- Square root
- `sin`, `cos`, `tan`
- Negative number toggle
- Calculation history with reuse
- Clear history
- Grand total tracking
- Scientific mode on/off
- Dark / light theme toggle

## Project Files

- `main.py` - main calculator application
- `run.bat` - run the app on Windows
- `requirements.txt` - Python dependencies
- `.gitignore` - ignored files for Git
- `history.txt` - saved calculation history

## How To Run

Open `cmd` or terminal in the project folder:

```cmd
cd C:\Users\ganes\calculator-app
venv\Scripts\activate.bat
python main.py
```

You can also run:

```cmd
run.bat
```

## Installation

If setting up the project again:

```cmd
cd C:\Users\ganes
git clone https://github.com/kartikdere06/calculator-app.git
cd calculator-app
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
python main.py
```

## Controls

### Buttons

- `C` clears the display
- `Back` deletes the last character
- `ANS` inserts the last answer
- `MC` clears memory
- `MR` recalls memory
- `MS` stores memory
- `GT` shows grand total
- `Scientific: ON/OFF` switches advanced features
- `Light Mode` / `Dark Mode` switches theme

### Keyboard

- Number keys: `0-9`
- Operators: `+`, `-`, `*`, `/`
- Brackets: `(` and `)`
- Decimal: `.`
- Percent: `%`
- Power: `^`
- `Enter` = calculate
- `Backspace` = delete last character
- `Delete` or `Esc` = clear
- `s` = `sin`
- `c` = `cos`
- `t` = `tan`
- `r` = square root
- `a` = `ANS`
- `m` = memory recall

## Percentage Behavior

Examples:

- `200 + 10 % = 220`
- `200 - 10 % = 180`
- `200 * 10 % = 20`
- Basic mode: `9 / % = 100`
- Scientific mode: `9 / % = 11.1111111111`

## History

- Each completed calculation is stored in history
- Click a history item to reuse its result
- History is saved in `history.txt`

## Grand Total

- Every completed result is added to `GT`
- Press `GT` to see the running grand total

## GitHub

Repository:

- <https://github.com/kartikdere06/calculator-app>

To push new changes:

```cmd
git add .
git commit -m "Update calculator app"
git push
```

## Notes

- This project is currently designed for Windows usage
- The app uses `PySide6` for the GUI
- Some button labels may be affected by terminal/file encoding depending on the editor
