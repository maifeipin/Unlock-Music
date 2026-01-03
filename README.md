# Music Unlocker Automation Suite

A powerful, efficient, and automated toolset to decrypt, clean, and archive your encrypted music collection (NCM, QMC, MGG, etc.).

## 🚀 Features

*   **⚡ High Performance**: Powered by a Go-based core (`um.exe`), resolving hundreds of files in seconds.
*   **🛡️ Robust**: Intelligent error handling, skips non-encrypted files, and detailed summary reports.
*   **🧹 Smart Cleanup**: Automatically deduplicates songs (e.g., `Song (1).mp3`), keeps the best quality version, and removes incomplete downloads.
*   **📦 Auto Archive**: Moves processed files to a NAS or external storage and maintains a history log to prevent re-processing.
*   **⏯️ Resume Capability**: Skips files that have already been successfully processed and archived.

## 📂 Project Structure

*   `unlock.py`: **The Main Tool**. Scans your download folder and batch unlocks music using the compiled Go core.
*   `clean.py`: **The Housekeeper**. Fixes filenames, removes duplicates, and syncs history logs.
*   `archive.py`: **The Mover**. Moves original and converted files to your specific destination (NAS/HDD).
*   `cli/`: Source code for the underlying Go decryption tool (`Unlock Music CLI`).

## 🛠️ Usage

### 1. Unlock Music
decrypts files from your source directory into an `output` folder.

```bash
python unlock.py
```
*Follow the prompts to enter your music download directory.*

### 2. Cleanup (Optional)
If you have messy filenames like `Song (1).mp3` or want to ensure logs are synced:

```bash
python clean.py
```

### 3. Archive
Move finished files to your permanent storage (e.g., local disk or NAS SMB path):

```bash
python archive.py
```

## ⚙️ Compilation (Optional)

The tool relies on `cli/um.exe`. If you need to rebuild it:

1. Install Go (1.23+).
2. Navigate to `cli/`.
3. Run `go build ./cmd/um`.

## 📜 License

This project (the Python wrapper scripts) is released under the **MIT License**.

## 👏 Credits & Acknowledgements

The core decryption engine is powered by **[Unlock Music CLI](https://git.unlock-music.dev/um/cli)**.
*   **Copyright**: (c) 2020-2021 Unlock Music
*   **License**: MIT License

All rights to the decryption algorithms and the `um` binary belong to the original authors. This project is merely an automation wrapper to facilitate batch processing and archiving.
