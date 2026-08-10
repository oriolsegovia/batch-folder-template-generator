# Batch Folder Template Generator

A small **local-first Windows desktop utility** for generating many folders from a pasted list of numeric IDs and copying the same set of template files into each folder.

The public repository intentionally contains **no real administrative documents, personal data, credentials, production paths or organization-specific templates**.

## Why this repository is public-safe

The original workflow was designed for repetitive administrative folder preparation. This repository publishes only the reusable software pattern:

- paste one numeric ID per line;
- choose a destination;
- create folders in bulk;
- copy local template files;
- skip or complete existing folders;
- light/dark mode;
- local execution only.

Actual production templates must stay outside Git and are intentionally excluded by `.gitignore`.

## Quick start

1. Install Python 3.11+.
2. Run `pip install -r requirements.txt`.
3. Copy `config.example.json` to `config.json`.
4. Create a local `templates/` folder.
5. Place only templates you are authorized to use inside `templates/`.
6. Run `python app.py`.

## Windows build

Run:

```bat
build_windows.bat
```

The resulting `.exe` is created under `dist/`.

> Important: never publish a production `.exe` if it embeds confidential templates. PyInstaller packaging is not encryption and bundled files can be extracted.

## Privacy and security

- No telemetry.
- No network calls.
- No cloud storage.
- No personal data is required by the application itself.
- IDs are processed locally.
- Template contents remain local.
- Production templates, builds, executables and logs are excluded from Git.

See [SECURITY.md](SECURITY.md).

## Repository structure

```text
app.py
config.example.json
templates.example/
requirements.txt
build_windows.bat
.gitignore
SECURITY.md
LICENSE
```

## License

MIT.
