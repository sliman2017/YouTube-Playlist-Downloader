# YouTube Playlist Downloader

Standalone GUI app and script to download YouTube playlists using `yt-dlp` with a modern CustomTkinter GUI.

This repository contains both the Python source (`myScript.py`) and a built executable (created with PyInstaller) so you can run the app from source or as a standalone `.exe` on Windows.

---

![alt text](https://github.com/sliman2017/YouTube-Playlist-Downloader/blob/improve/enhance_design/screenshots/youtube%20downlaoder%2001.png?raw=true)

---

![alt text](https://github.com/sliman2017/YouTube-Playlist-Downloader/blob/improve/enhance_design/screenshots/youtube%20downlaoder%2002.png?raw=true)

---
## Features

- Download entire playlists (highest available quality).
- Per-video status and progress in the GUI list.
- Choose output directory (Browse button) or use the default folder.
- Optional `ffmpeg` support for merging and format conversion (place `ffmpeg.exe` next to the script/exe or available on PATH).
- Works as a Python script or as a compiled standalone executable.

---
```markdown
# YouTube Playlist Downloader

Standalone GUI app and script to download YouTube playlists using `yt-dlp` with a modern CustomTkinter GUI.

This repository contains both the Python source (`myScript.py`) and a built executable (created with PyInstaller) so you can run the app from source or as a standalone `.exe` on Windows.

---

![alt text](https://github.com/sliman2017/YouTube-Playlist-Downloader/blob/main/youtube%20downloader.png?raw=true)


## Features

- Download entire playlists (highest available quality) with selectable target quality.
- Dual-view interface: starts compact, expands to an expanded download dashboard when a download starts.
- Per-video status, progress and thumbnail in a detailed video list (each video card shows title, thumbnail, individual progress, speed and status).
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

## Dual-view UI (redesign overview)

The app now uses a two-view system: a compact input window for quick starts, and an expanded download dashboard that appears while downloads run.

### 1) Compact Input View (start state)

- Window size: ~550×650 px (compact and focused)
- Controls:
  - URL input with Paste button
  - Save Location with Browse button
  - Quality selector (Highest / 1080p / 720p / Audio Only)
  - Start Download button

### 2) Expanded Download View (appears when a download starts)

- Window size: ~1200×800 px (detailed dashboard)

Top control bar (live info)
- Playlist title and summary stats
- Video count
- Total size downloaded so far
- Real-time total speed indicator
- Pause button (visual placeholder)
- Cancel button (stops downloads and returns to compact view)

Overall progress area
- Status message and percentage indicator
- Gradient progress bar for visual polish

Video list (main area)
- Each video is shown as a card (larger layout):
  - Thumbnail area (140×85 px) with video index
  - Full title (truncated visually up to ~80 chars)
  - Download info: downloaded size / total • current speed
  - Individual progress bar (turns green when complete)
  - Status states: Waiting → Downloading → Merging → Done

UX notes
- The app starts compact for quick input. When downloads begin the UI expands to show the full dashboard and live statistics. Users may cancel to return to the compact view at any time.

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

## Troubleshooting

- "yt-dlp not found" when running exe: ensure the exe was built correctly. If running from source, run `pip install yt-dlp`.
- "ffmpeg not found" / Mux errors: place `ffmpeg.exe` next to the script/exe or install ffmpeg and add to PATH.
- Long playlists take time to enumerate — allow the app a minute to fetch metadata for large playlists.
- If output files are incomplete, try running `yt-dlp` manually in a terminal with the same URL to inspect errors.

Debug tips:
- Run `python myScript.py` from PowerShell to see printed tracebacks.
- Use `yt-dlp -F <url>` in a terminal to inspect available formats for troubleshooting format selection.

---

## New features summary

- Quality selection before starting a download (choose Highest, 1080p, 720p, or Audio Only).
- Cancel download to return to the compact input view.
- Live aggregated statistics (total speed, total downloaded size, video count).
- Playlist title display (real playlist name shown in the top bar).
- Larger video cards with thumbnail placeholders for clearer information.

---

## Contributing

- If you want to improve the GUI, add features, or fix bugs, open a PR with a short description and test steps.
- Keep changes focused and document any new dependencies.

---

``` 
