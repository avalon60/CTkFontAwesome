import tkinter as tk
from tkinter import ttk

import ctkfontawesome


class IconBrowser(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CTkFontAwesome Browser")
        self.geometry("980x640")
        self.minsize(840, 520)

        self.all_icons = ctkfontawesome.icon_names()
        self.filtered_icons = self.all_icons[:]
        self.current_image = None

        self.search_var = tk.StringVar()
        self.fill_var = tk.StringVar(value="#1f6aa5")
        self.size_var = tk.IntVar(value=96)
        self.status_var = tk.StringVar()
        self.selected_name_var = tk.StringVar(value="Select an icon")

        self._build_ui()
        self._populate_list()
        if self.filtered_icons:
            self.listbox.selection_set(0)
            self._on_selection(None)

    def _build_ui(self):
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        left = ttk.Frame(self, padding=12)
        left.grid(row=0, column=0, sticky="nsew")
        left.rowconfigure(2, weight=1)

        ttk.Label(left, text="Search").grid(row=0, column=0, sticky="w")
        search_entry = ttk.Entry(left, textvariable=self.search_var, width=32)
        search_entry.grid(row=1, column=0, sticky="ew", pady=(4, 12))
        search_entry.bind("<KeyRelease>", self._on_search)

        self.count_label = ttk.Label(left, text="")
        self.count_label.grid(row=2, column=0, sticky="sw", pady=(0, 4))

        list_frame = ttk.Frame(left)
        list_frame.grid(row=3, column=0, sticky="nsew")
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)

        self.listbox = tk.Listbox(list_frame, exportselection=False, width=34)
        self.listbox.grid(row=0, column=0, sticky="nsew")
        self.listbox.bind("<<ListboxSelect>>", self._on_selection)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.listbox.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.listbox.configure(yscrollcommand=scrollbar.set)

        right = ttk.Frame(self, padding=12)
        right.grid(row=0, column=1, sticky="nsew")
        right.columnconfigure(0, weight=1)
        right.rowconfigure(3, weight=1)

        ttk.Label(right, textvariable=self.selected_name_var, font=("", 16, "bold")).grid(
            row=0, column=0, sticky="w"
        )

        controls = ttk.Frame(right)
        controls.grid(row=1, column=0, sticky="ew", pady=(12, 12))
        controls.columnconfigure(5, weight=1)

        ttk.Label(controls, text="Fill").grid(row=0, column=0, sticky="w")
        fill_entry = ttk.Entry(controls, textvariable=self.fill_var, width=12)
        fill_entry.grid(row=0, column=1, sticky="w", padx=(6, 16))
        fill_entry.bind("<Return>", self._refresh_preview)

        ttk.Label(controls, text="Size").grid(row=0, column=2, sticky="w")
        size_spin = tk.Spinbox(
            controls,
            from_=16,
            to=256,
            increment=8,
            textvariable=self.size_var,
            width=6,
            command=self._refresh_preview,
        )
        size_spin.grid(row=0, column=3, sticky="w", padx=(6, 16))
        size_spin.bind("<Return>", self._refresh_preview)

        ttk.Button(controls, text="Refresh", command=self._refresh_preview).grid(
            row=0, column=4, sticky="w", padx=(0, 16)
        )
        ttk.Button(controls, text="Copy Name", command=self._copy_name).grid(
            row=0, column=5, sticky="w"
        )
        ttk.Button(controls, text="Copy Code", command=self._copy_code).grid(
            row=0, column=6, sticky="w", padx=(8, 0)
        )

        self.preview_frame = ttk.LabelFrame(right, text="Preview", padding=16)
        self.preview_frame.grid(row=2, column=0, sticky="nsew")
        self.preview_frame.columnconfigure(0, weight=1)
        self.preview_frame.rowconfigure(0, weight=1)

        self.preview_label = ttk.Label(self.preview_frame, anchor="center", justify="center")
        self.preview_label.grid(row=0, column=0, sticky="nsew")

        details = ttk.LabelFrame(right, text="CustomTkinter Snippet", padding=12)
        details.grid(row=3, column=0, sticky="nsew", pady=(12, 0))
        details.columnconfigure(0, weight=1)
        details.rowconfigure(0, weight=1)

        self.code_text = tk.Text(details, wrap="none", height=14)
        self.code_text.grid(row=0, column=0, sticky="nsew")
        self.code_text.configure(state="disabled")

        details_scroll = ttk.Scrollbar(details, orient="vertical", command=self.code_text.yview)
        details_scroll.grid(row=0, column=1, sticky="ns")
        self.code_text.configure(yscrollcommand=details_scroll.set)

        status = ttk.Label(self, textvariable=self.status_var, anchor="w", padding=(12, 0, 12, 10))
        status.grid(row=1, column=0, columnspan=2, sticky="ew")

    def _populate_list(self):
        self.listbox.delete(0, tk.END)
        for name in self.filtered_icons:
            self.listbox.insert(tk.END, name)
        self.count_label.configure(text=f"{len(self.filtered_icons)} icons")

    def _on_search(self, _event):
        term = self.search_var.get().strip().lower()
        if not term:
            self.filtered_icons = self.all_icons[:]
        else:
            self.filtered_icons = [name for name in self.all_icons if term in name.lower()]
        self._populate_list()
        if self.filtered_icons:
            self.listbox.selection_set(0)
            self._on_selection(None)
        else:
            self.selected_name_var.set("No matches")
            self._set_code_text("")
            self.preview_label.configure(image="", text="")
            self.status_var.set("No icons match the current filter.")

    def _on_selection(self, _event):
        selection = self.listbox.curselection()
        if not selection:
            return
        name = self.filtered_icons[selection[0]]
        self.selected_name_var.set(name)
        self._render_preview(name)

    def _refresh_preview(self, _event=None):
        selection = self.listbox.curselection()
        if not selection:
            return
        self._render_preview(self.filtered_icons[selection[0]])

    def _render_preview(self, name):
        self._set_code_text(self._build_code_snippet(name))

        try:
            image = ctkfontawesome.icon_to_image(
                name,
                fill=self.fill_var.get().strip() or None,
                scale_to_width=self.size_var.get(),
            )
        except Exception as exc:
            self.current_image = None
            self.preview_label.configure(
                image="",
                text="Image preview unavailable\n\n"
                "Install optional dependencies:\n"
                "pip install 'ctkfontawesome[images]'",
            )
            self.status_var.set(f"{type(exc).__name__}: {exc}")
            return

        self.current_image = image
        self.preview_label.configure(image=image, text="")
        self.status_var.set(f"Previewing '{name}' at {self.size_var.get()}px.")

    def _set_code_text(self, value):
        self.code_text.configure(state="normal")
        self.code_text.delete("1.0", tk.END)
        self.code_text.insert("1.0", value)
        self.code_text.configure(state="disabled")

    def _copy_name(self):
        selection = self.listbox.curselection()
        if not selection:
            return
        name = self.filtered_icons[selection[0]]
        self.clipboard_clear()
        self.clipboard_append(name)
        self.status_var.set(f"Copied icon name '{name}'.")

    def _copy_code(self):
        selection = self.listbox.curselection()
        if not selection:
            return
        name = self.filtered_icons[selection[0]]
        self.clipboard_clear()
        self.clipboard_append(self._build_code_snippet(name))
        self.status_var.set(f"Copied CustomTkinter snippet for '{name}'.")

    def _build_code_snippet(self, name):
        fill = self.fill_var.get().strip() or "#1f6aa5"
        size = self.size_var.get()
        return (
            "import customtkinter as ctk\n"
            "from ctkfontawesome import icon_to_image\n\n"
            "app = ctk.CTk()\n\n"
            f"icon = icon_to_image(\"{name}\", fill=\"{fill}\", scale_to_width={size})\n"
            "button = ctk.CTkButton(\n"
            "    app,\n"
            "    text=\"\",\n"
            "    image=icon,\n"
            "    width=44,\n"
            "    height=44,\n"
            ")\n"
            "button.pack(padx=20, pady=20)\n\n"
            "app.mainloop()\n"
        )



def main():
    app = IconBrowser()
    app.mainloop()


if __name__ == "__main__":
    main()
