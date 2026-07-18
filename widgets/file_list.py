import customtkinter as ctk
from PIL import Image
import os
from theme import tr, ICONS, FONT, FONT_BOLD, FONT_SMALL, Colors


class FileItem(ctk.CTkFrame):
    def __init__(self, master, file_path, index, on_delete=None, on_up=None, on_down=None, on_select_pages=None, **kwargs):
        super().__init__(master, **kwargs)
        self.file_path = file_path
        self.page_selection = None

        self.configure(fg_color=("#ffffff", Colors.CARD), corner_radius=12, height=54)
        self.grid_propagate(False)
        self.grid_columnconfigure(2, weight=1)

        idx_frame = ctk.CTkFrame(self, fg_color=(Colors.PRIMARY, "#243044"),
                                  corner_radius=8, width=28, height=28)
        idx_frame.grid(row=0, column=0, padx=(12, 4), pady=13)
        idx_frame.grid_propagate(False)
        self.idx_lbl = ctk.CTkLabel(idx_frame, text=str(index),
                                     font=("Segoe UI", 11, "bold"),
                                     text_color=("#ffffff", Colors.PRIMARY_LIGHT))
        self.idx_lbl.place(relx=0.5, rely=0.5, anchor="center")

        ext = os.path.splitext(file_path)[1].lower()
        icon = ICONS["pdf"] if ext == ".pdf" else ICONS["image"]
        ctk.CTkLabel(self, text=icon, font=("Segoe UI", 18), width=30,
                      text_color=(Colors.PRIMARY, Colors.PRIMARY_LIGHT)).grid(row=0, column=1, padx=2, pady=8)

        name = os.path.basename(file_path)
        size = os.path.getsize(file_path)
        size_str = f"{size / 1024:.1f} KB" if size < 1024 * 1024 else f"{size / (1024 * 1024):.1f} MB"
        info = f"{name}  \u00b7  {size_str}"

        ctk.CTkLabel(self, text=info, font=FONT, anchor="w",
                      justify="left", text_color=("#0f172a", Colors.TEXT)
                      ).grid(row=0, column=2, padx=8, pady=8, sticky="w")

        self.sel_lbl = ctk.CTkLabel(self, text="", font=FONT_SMALL,
                                     text_color=(Colors.PRIMARY, Colors.PRIMARY_LIGHT))
        self.sel_lbl.grid(row=0, column=3, padx=2)

        btn_f = ctk.CTkFrame(self, fg_color="transparent")
        btn_f.grid(row=0, column=4, padx=6, pady=4)

        if on_up:
            ctk.CTkButton(btn_f, text=ICONS["up"], width=28, height=28,
                           font=("Segoe UI", 11),
                           fg_color="transparent",
                           hover_color=("#f1f5f9", Colors.SURFACE_ALT),
                           text_color=("#64748b", Colors.TEXT_MUTED),
                           corner_radius=8,
                           command=lambda: on_up(self)).pack(side="left", padx=1)
        if on_down:
            ctk.CTkButton(btn_f, text=ICONS["down"], width=28, height=28,
                           font=("Segoe UI", 11),
                           fg_color="transparent",
                           hover_color=("#f1f5f9", Colors.SURFACE_ALT),
                           text_color=("#64748b", Colors.TEXT_MUTED),
                           corner_radius=8,
                           command=lambda: on_down(self)).pack(side="left", padx=1)

        if ext == ".pdf" and on_select_pages:
            ctk.CTkButton(btn_f, text=tr("select_pages"), width=90, height=28,
                           font=FONT_SMALL,
                           fg_color="transparent",
                           hover_color=("#f1f5f9", Colors.SURFACE_ALT),
                           text_color=(Colors.PRIMARY, Colors.PRIMARY_LIGHT),
                           corner_radius=18,
                           command=lambda: on_select_pages(self)).pack(side="left", padx=2)

        ctk.CTkButton(btn_f, text=ICONS["close"], width=28, height=28,
                       font=("Segoe UI", 12),
                       fg_color="transparent",
                       hover_color=("#fef2f2", "#2d1015"),
                       text_color=("#ef4444", "#f87171"),
                       corner_radius=8,
                       command=lambda: on_delete(self) if on_delete else None).pack(side="left", padx=1)

    def set_page_selection(self, selected_pages, total_pages):
        self.page_selection = selected_pages
        if selected_pages and len(selected_pages) < total_pages:
            self.sel_lbl.configure(text=f"{len(selected_pages)}/{total_pages}")
        else:
            self.sel_lbl.configure(text="")


class FileList(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.items = []
        self.configure(fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)

    def add_file(self, file_path, on_select_pages=None):
        item = FileItem(self, file_path, len(self.items) + 1,
                        on_delete=self.remove_file,
                        on_up=self.move_up,
                        on_down=self.move_down,
                        on_select_pages=on_select_pages)
        item.grid(row=len(self.items), column=0, padx=4, pady=3, sticky="ew")
        self.items.append(item)
        self._refresh_indices()
        return item

    def remove_file(self, item):
        if item in self.items:
            self.items.remove(item)
            item.destroy()
            self._refresh_indices()

    def clear_all(self):
        for item in self.items[:]:
            item.destroy()
        self.items.clear()

    def move_up(self, item):
        i = self.items.index(item)
        if i > 0:
            self.items[i], self.items[i-1] = self.items[i-1], self.items[i]
            self._rearrange()
            self._refresh_indices()

    def move_down(self, item):
        i = self.items.index(item)
        if i < len(self.items) - 1:
            self.items[i], self.items[i+1] = self.items[i+1], self.items[i]
            self._rearrange()
            self._refresh_indices()

    def _rearrange(self):
        for i, it in enumerate(self.items):
            it.grid(row=i, column=0, padx=4, pady=3, sticky="ew")

    def _refresh_indices(self):
        for i, it in enumerate(self.items):
            it.idx_lbl.configure(text=str(i + 1))

    def get_file_paths(self):
        return [it.file_path for it in self.items]

    def get_page_selections(self):
        return [it.page_selection for it in self.items]

    def get_item_count(self):
        return len(self.items)
