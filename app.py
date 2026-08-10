import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

import customtkinter as ctk
from tkinter import filedialog, messagebox

APP_DIR = Path(__file__).resolve().parent
CONFIG_PATH = APP_DIR / "config.json"
TEMPLATES_DIR = APP_DIR / "templates"

DEFAULT_CONFIG = {
    "app_name": "Batch Folder Template Generator",
    "app_subtitle": "Local desktop utility for batch folder creation",
    "folder_prefix": "Case ",
    "folder_suffix": "",
    "id_pattern": r"^\d+$"
}

ctk.set_default_color_theme("blue")


def load_config():
    config = DEFAULT_CONFIG.copy()
    if CONFIG_PATH.exists():
        user = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        config.update(user)
    return config


def validate_ids(text, pattern):
    rx = re.compile(pattern)
    valid, invalid, duplicates = [], [], []
    seen = set()

    for raw in text.splitlines():
        value = raw.strip()
        if not value:
            continue
        if not rx.fullmatch(value):
            invalid.append(value)
            continue
        if value in seen:
            duplicates.append(value)
            continue
        seen.add(value)
        valid.append(value)

    return valid, invalid, duplicates


def template_files():
    if not TEMPLATES_DIR.exists():
        return []
    return [p for p in sorted(TEMPLATES_DIR.iterdir()) if p.is_file()]


class App(ctk.CTk):
    def __init__(self):
        ctk.set_appearance_mode("system")
        super().__init__()

        self.cfg = load_config()
        self.title(self.cfg["app_name"])
        self.geometry("800x650")
        self.minsize(650, 520)

        self.dest_var = ctk.StringVar(value=str(Path.home() / "Desktop"))
        self.existing_mode = ctk.StringVar(value="skip")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._header()
        self._body()
        self._footer()
        self._refresh()

    def _header(self):
        frame = ctk.CTkFrame(self, corner_radius=0)
        frame.grid(row=0, column=0, sticky="ew")
        frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            frame, text=self.cfg["app_name"],
            font=ctk.CTkFont(size=20, weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=18, pady=(12, 0))

        ctk.CTkLabel(
            frame, text=self.cfg["app_subtitle"],
            font=ctk.CTkFont(size=10)
        ).grid(row=1, column=0, sticky="w", padx=18, pady=(0, 10))

        self.theme_btn = ctk.CTkButton(
            frame, text="☾", width=36, height=36,
            corner_radius=18, command=self._toggle_theme
        )
        self.theme_btn.grid(row=0, column=1, rowspan=2, padx=18)

    def _body(self):
        self.scroll = ctk.CTkScrollableFrame(self, corner_radius=0)
        self.scroll.grid(row=1, column=0, sticky="nsew")
        self.scroll.grid_columnconfigure(0, weight=1)

        card1 = ctk.CTkFrame(self.scroll)
        card1.grid(row=0, column=0, sticky="ew", padx=14, pady=7)
        card1.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(card1, text="1 · Destination folder",
                     font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, sticky="w", padx=14, pady=(12, 6)
        )
        row = ctk.CTkFrame(card1, fg_color="transparent")
        row.grid(row=1, column=0, sticky="ew", padx=14, pady=(0, 12))
        row.grid_columnconfigure(0, weight=1)
        ctk.CTkEntry(row, textvariable=self.dest_var, height=36).grid(
            row=0, column=0, sticky="ew", padx=(0, 8)
        )
        ctk.CTkButton(row, text="Browse", width=90, command=self._browse).grid(
            row=0, column=1
        )

        card2 = ctk.CTkFrame(self.scroll)
        card2.grid(row=1, column=0, sticky="ew", padx=14, pady=7)
        card2.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(card2, text="2 · IDs",
                     font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, sticky="w", padx=14, pady=(12, 4)
        )
        ctk.CTkLabel(
            card2, text="Paste one numeric ID per line. No artificial limit.",
            font=ctk.CTkFont(size=10)
        ).grid(row=1, column=0, sticky="w", padx=14, pady=(0, 6))

        self.ids = ctk.CTkTextbox(
            card2, height=150, wrap="none", activate_scrollbars=True
        )
        self.ids.grid(row=2, column=0, sticky="ew", padx=14, pady=(0, 8))
        self.ids.bind("<KeyRelease>", lambda e: self._refresh())

        actions = ctk.CTkFrame(card2, fg_color="transparent")
        actions.grid(row=3, column=0, sticky="ew", padx=14, pady=(0, 12))
        actions.grid_columnconfigure(2, weight=1)
        ctk.CTkButton(actions, text="Paste", command=self._paste, width=90).grid(
            row=0, column=0, padx=(0, 6)
        )
        ctk.CTkButton(actions, text="Clear", command=self._clear, width=80).grid(
            row=0, column=1
        )
        self.count = ctk.CTkLabel(actions, text="0 IDs")
        self.count.grid(row=0, column=3, sticky="e")

        card3 = ctk.CTkFrame(self.scroll)
        card3.grid(row=2, column=0, sticky="ew", padx=14, pady=7)

        ctk.CTkLabel(card3, text="3 · Existing folders",
                     font=ctk.CTkFont(weight="bold")).pack(
            anchor="w", padx=14, pady=(12, 6)
        )
        ctk.CTkRadioButton(
            card3, text="Skip existing folders",
            variable=self.existing_mode, value="skip"
        ).pack(anchor="w", padx=14, pady=3)
        ctk.CTkRadioButton(
            card3, text="Add only missing template files",
            variable=self.existing_mode, value="merge"
        ).pack(anchor="w", padx=14, pady=(3, 12))

        self.log = ctk.CTkTextbox(self.scroll, height=90)
        self.log.grid(row=3, column=0, sticky="ew", padx=14, pady=7)
        self.log.configure(state="disabled")

    def _footer(self):
        footer = ctk.CTkFrame(self, corner_radius=0)
        footer.grid(row=2, column=0, sticky="ew")
        footer.grid_columnconfigure(0, weight=1)
        self.run_btn = ctk.CTkButton(
            footer, text="GENERATE FOLDERS", height=42, command=self._run
        )
        self.run_btn.grid(row=0, column=0, sticky="ew", padx=14, pady=10)

    def _toggle_theme(self):
        if ctk.get_appearance_mode() == "Dark":
            ctk.set_appearance_mode("light")
            self.theme_btn.configure(text="☾")
        else:
            ctk.set_appearance_mode("dark")
            self.theme_btn.configure(text="☀")

    def _browse(self):
        path = filedialog.askdirectory()
        if path:
            self.dest_var.set(path)

    def _paste(self):
        try:
            text = self.clipboard_get()
        except Exception:
            text = ""
        if text:
            self.ids.delete("1.0", "end")
            self.ids.insert("1.0", text)
            self._refresh()

    def _clear(self):
        self.ids.delete("1.0", "end")
        self._refresh()

    def _refresh(self):
        valid, invalid, duplicates = validate_ids(
            self.ids.get("1.0", "end"), self.cfg["id_pattern"]
        )
        text = f"{len(valid)} IDs"
        if invalid:
            text += f" · {len(invalid)} invalid"
        if duplicates:
            text += f" · {len(duplicates)} duplicates"
        self.count.configure(text=text)

    def _write(self, msg):
        self.log.configure(state="normal")
        self.log.insert("end", msg + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")
        self.update_idletasks()

    def _run(self):
        valid, invalid, _ = validate_ids(
            self.ids.get("1.0", "end"), self.cfg["id_pattern"]
        )
        if not valid:
            messagebox.showwarning(self.cfg["app_name"], "No valid IDs found.")
            return
        if invalid:
            messagebox.showerror(
                self.cfg["app_name"],
                "Some values are invalid. Fix them before continuing."
            )
            return

        templates = template_files()
        if not templates:
            messagebox.showerror(
                self.cfg["app_name"],
                "No template files were found in the local templates folder."
            )
            return

        dest = Path(self.dest_var.get().strip())
        dest.mkdir(parents=True, exist_ok=True)

        if not messagebox.askyesno(
            self.cfg["app_name"],
            f"Process {len(valid)} folders with {len(templates)} template file(s)?"
        ):
            return

        for case_id in valid:
            name = f'{self.cfg["folder_prefix"]}{case_id}{self.cfg["folder_suffix"]}'
            target = dest / name

            if target.exists() and self.existing_mode.get() == "skip":
                self._write(f"SKIPPED  {name}")
                continue

            if target.exists():
                for template in templates:
                    dst = target / template.name
                    if not dst.exists():
                        shutil.copy2(template, dst)
                self._write(f"MERGED   {name}")
                continue

            temp_parent = Path(tempfile.mkdtemp(prefix=".batch_", dir=dest))
            try:
                temp_folder = temp_parent / name
                temp_folder.mkdir()
                for template in templates:
                    shutil.copy2(template, temp_folder / template.name)
                temp_folder.replace(target)
                self._write(f"CREATED  {name}")
            finally:
                shutil.rmtree(temp_parent, ignore_errors=True)

        messagebox.showinfo(self.cfg["app_name"], "Done.")


if __name__ == "__main__":
    App().mainloop()
