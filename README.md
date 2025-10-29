# YouTube Playlist Downloader

Standalone GUI app and script to download YouTube playlists using `yt-dlp` with a modern CustomTkinter GUI.

This repository contains both the Python source (`myScript.py`) and a built executable (created with PyInstaller) so you can run the app from source or as a standalone `.exe` on Windows.

---

## Features

- Download entire playlists (highest available quality).
- Per-video status and progress in the GUI list.
- Choose output directory (Browse button) or use the default folder.
- Optional `ffmpeg` support for merging and format conversion (place `ffmpeg.exe` next to the script/exe or available on PATH).
- Works as a Python script or as a compiled standalone executable.

---

## Requirements (running from source)

- Python 3.8+ (3.9/3.10/3.11 recommended)
- pip packages:
  - `yt-dlp`
  - `customtkinter`

Install requirements:

```powershell
python -m pip install --upgrade pip
pip install yt-dlp customtkinter
```

Optional for merging/conversions:

- `ffmpeg` executable (Windows: `ffmpeg.exe`) available on PATH or placed in the same folder as the script/exe.

---

## Project structure (important files)

- `myScript.py` — main application source (GUI + download logic).
- `youtube_downloader.spec` — PyInstaller spec used to build the executable.
- `build/` — PyInstaller build artifacts from a previous build (can be ignored or removed).
- `README.md` — this file.

If you compiled the app, you will also find a `dist/` folder (or the single exe) next to your build output depending on how you ran PyInstaller.

---

## Run from source (development)

1. Ensure requirements are installed (see above).
2. From the repository folder run:

```powershell
# Windows PowerShell
cd "e:\Coding\python coding\Youtube_Downloader"
python myScript.py
```

The GUI window will open. Paste a playlist URL, choose or accept the output directory, and click the Download button.

Notes:
- Running from a terminal prints logs and exceptions to help debugging.
- If `yt-dlp` complains about missing `ffmpeg` when merging, either install ffmpeg and add it to PATH, or copy `ffmpeg.exe` next to `myScript.py`.

---

## Run the compiled executable (Windows)

If you already built the executable with PyInstaller, run the generated `.exe` from your `dist/` folder or wherever you placed it. Example (PowerShell):

```powershell
cd "e:\Coding\python coding\Youtube_Downloader\dist"
.\youtube_downloader.exe
```

Recommendations:
- Put `ffmpeg.exe` in the same folder as the `.exe` if you need merging/conversion.
- If SmartScreen or AV warns about an unsigned exe, you can right-click -> Properties -> Unblock (for local testing) or sign the binary for distribution.

---

## Packaging (how this exe was built)

This project was packaged with PyInstaller. Example PyInstaller command that produces a single-file exe and bundles `ffmpeg.exe` next to it (adjust paths as needed):

```powershell
pyinstaller --onefile --add-binary "ffmpeg.exe;." --name youtube_downloader myScript.py
```

Notes on packaging:
- `--onefile` creates a single EXE that unpacks at runtime (useful for distribution).
- `--add-binary "ffmpeg.exe;."` copies `ffmpeg.exe` next to the exe at runtime.
- Check the generated `warn-*.txt` in `build/` if PyInstaller warns about missing modules.

---

## Troubleshooting

- "yt-dlp not found" when running exe: ensure the exe was built correctly. If running from source, run `pip install yt-dlp`.
- "ffmpeg not found" / Mux errors: place `ffmpeg.exe` next to the script/exe or install ffmpeg and add to PATH.
- Long playlists take time to enumerate — allow the app a minute to fetch metadata for large playlists.
- If output files are incomplete, try running `yt-dlp` manually in a terminal with the same URL to inspect errors.

Debug tips:
- Run `python myScript.py` from PowerShell to see printed tracebacks.
- Use `yt-dlp -F <url>` in a terminal to inspect available formats for troubleshooting format selection.

---

## Contributing

- If you want to improve the GUI, add features, or fix bugs, open a PR with a short description and test steps.
- Keep changes focused and document any new dependencies.

---

## License

Add a `LICENSE` file to this repo to declare a license. If you want a permissive license, consider MIT:

```
MIT License
Copyright (c) YEAR Your Name

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions: ...
```

Replace `YEAR` and `Your Name` as appropriate.

---

If you want, I can also:

- Add a short `USAGE.md` with screenshots or sample commands.
- Add a `requirements.txt` and a small `build` script for reproducible packaging.
- Commit this `README.md` into the repository for you.

Thanks — tell me which extra items you'd like me to add next.
# YouTube-Playlist-Downloader
Simple modern GUI app to download YouTube playlists in the highest available quality
