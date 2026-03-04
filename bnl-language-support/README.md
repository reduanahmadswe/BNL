# BNL Language Support

Custom language support for `.bnl` (Banglish language) files with syntax highlighting and file execution.

## Features

- Banglish syntax highlighting (`dorlam`, `dekhao`, `guraw`, `shesh`, etc.)
- Word operators highlighting (`jog`, `biyog`, `gun`, `vag`)
- Comments (`#`), numbers, strings, and identifiers support
- Run `.bnl` file directly from VS Code command palette

## Run BNL code (output in terminal)

1. Open any `.bnl` file.
2. Press `Ctrl+Shift+P` and run: `BNL: Run Current File`
3. Output will appear in a terminal named `BNL Runner`.

## Requirement

- Python must be installed on user's machine.

If Python command is not `python`, user can set:

- `Settings` -> search `bnl.pythonPath`
- Example value: `C:/Python313/python.exe`
