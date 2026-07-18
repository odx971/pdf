import customtkinter as ctk
import os
import threading
from tkinter import filedialog
from theme import tr, ICONS, FONT, FONT_BOLD, FONT_SMALL, FONT_LARGE, Colors
from widgets.file_list import FileList
from widgets.page_selector import PageSelectorDialog
from widgets.name_dialog import NameDialog
from widgets.toast import Toast
from utils.pdf_ops import merge_pdfs, get_page_count


class MergeTab(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.app_ref = None

        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.grid(row=0, column=0, padx=28, pady=(28, 4), sticky="ew")
        hdr.grid_columnconfigure(1, weight=1)

        icon_bg = ctk.CTkFrame(hdr, width=40, height=40, corner_radius=12,
                                fg_color="#ff0000")
        icon_bg.grid(row=0, column=0, sticky="w")
        icon_bg.grid_propagate(False)
        ctk.CTkLabel(icon_bg, text="📎", font=("Segoe UI", 18),
                      text_color="#ffffff").place(relx=0.5, rely=0.5, anchor="center")

        self.title = ctk.CTkLabel(hdr, text=tr("merge"), font=FONT_LARGE,
                                  text_color=("#0f172a", Colors.TEXT))
        self.title.grid(row=0, column=1, sticky="w", padx=(12, 0))

        self.desc = ctk.CTkLabel(hdr, text=tr("merge_desc"), font=("Segoe UI", 12),
                                 text_color=("#64748b", Colors.TEXT_MUTED))
        self.desc.grid(row=1, column=1, sticky="w", padx=(12, 0), pady=(2, 0))

        accent = ctk.CTkFrame(hdr, height=3, fg_color=Colors.PRIMARY,
                               corner_radius=2)
        accent.grid(row=2, column=0, columnspan=2, sticky="ew", padx=0, pady=(10, 0))

        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.grid(row=1, column=0, padx=28, pady=(10, 8), sticky="ew")
        bar.grid_columnconfigure(1, weight=1)

        self.browse_btn = ctk.CTkButton(bar, text=f"  {ICONS['folder']}  {tr('browse_pdf')}",
                                         height=38,
                                         font=FONT,
                                         fg_color="transparent",
                                         border_color=Colors.PRIMARY,
                                         border_width=2,
                                         hover_color=("#d4f0ee", Colors.SURFACE_ALT),
                                         text_color=Colors.PRIMARY,
                                         corner_radius=20,
                                         command=self.browse_files)
        self.browse_btn.grid(row=0, column=0, padx=2)

        self.clear_btn = ctk.CTkButton(bar, text=f"  {ICONS['trash']}  {tr('clear_all')}",
                                        height=38,
                                        font=FONT,
                                        fg_color="transparent",
                                        hover_color=("#fef2f2", "#2d1015"),
                                        text_color=("#ef4444", "#f87171"),
                                        corner_radius=18,
                                        command=self.clear_all)
        self.clear_btn.grid(row=0, column=1, padx=2, sticky="w")

        self.cnt_lbl = ctk.CTkLabel(bar, text="", font=FONT_SMALL,
                                     text_color=("#64748b", Colors.TEXT_MUTED))
        self.cnt_lbl.grid(row=0, column=2, padx=8, sticky="e")

        self.flist = FileList(self)
        self.flist.grid(row=2, column=0, padx=28, pady=4, sticky="nsew")

        self.drop_overlay = ctk.CTkFrame(self.flist, fg_color="transparent")
        self.drop_overlay.place(relx=0.5, rely=0.3, anchor="center")

        ctk.CTkLabel(self.drop_overlay, text=ICONS["merge"], font=("Segoe UI", 44),
                       text_color=("#99f6e4", Colors.TEXT_MUTED)).pack()
        ctk.CTkLabel(self.drop_overlay, text=tr("drop_pdf"), font=("Segoe UI", 14),
                      text_color=("#64748b", Colors.TEXT_MUTED)).pack(pady=(4, 0))
        browse_lbl = ctk.CTkLabel(self.drop_overlay, text=tr("or_browse"),
                                   font=FONT_SMALL,
                                   text_color=("#0d9488", Colors.PRIMARY),
                                   cursor="hand2")
        browse_lbl.pack(pady=(4, 0))
        browse_lbl.bind("<Button-1>", lambda e: self.browse_files())

        bot = ctk.CTkFrame(self, fg_color="transparent")
        bot.grid(row=3, column=0, padx=28, pady=(8, 24), sticky="ew")
        bot.grid_columnconfigure(0, weight=1)

        self.progress = ctk.CTkProgressBar(bot, height=6, corner_radius=3,
                                            progress_color=Colors.PRIMARY)
        self.progress.grid(row=0, column=0, padx=2, pady=8, sticky="ew")
        self.progress.set(0)

        self.merge_btn = ctk.CTkButton(bot, text=f"  {tr('merge_btn')}  {ICONS['arrow_right']}",
                                        height=44,
                                        font=FONT_BOLD,
                                        fg_color=Colors.PRIMARY,
                                        hover_color=Colors.PRIMARY_HOVER,
                                        corner_radius=22,
                                        text_color="#ffffff",
                                        command=self.merge_files)
        self.merge_btn.grid(row=0, column=1, padx=8)

    def browse_files(self):
        files = filedialog.askopenfilenames(title=tr("browse_pdf"),
                                            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")])
        for f in files:
            if f.lower().endswith(".pdf"):
                self.flist.add_file(f, on_select_pages=self.open_page_selector)
        self._update_count()

    def clear_all(self):
        self.flist.clear_all()
        self.progress.set(0)
        self._update_count()

    def open_page_selector(self, item):
        dlg = PageSelectorDialog(self, item.file_path)
        self.wait_window(dlg)
        res = dlg.get_result()
        if res is not None:
            item.set_page_selection(res, get_page_count(item.file_path))

    def _update_count(self):
        c = self.flist.get_item_count()
        self.cnt_lbl.configure(text=f"{c} {tr('files')}" if c else "")

    def handle_drop(self, paths):
        for p in paths:
            if p.lower().endswith(".pdf"):
                self.flist.add_file(p, on_select_pages=self.open_page_selector)
        self._update_count()

    def merge_files(self):
        paths = self.flist.get_file_paths()
        if not paths:
            Toast.show(self, tr("no_files"), "warning")
            return

        selections = self.flist.get_page_selections()
        for s in selections:
            if s is not None and len(s) == 0:
                Toast.show(self, tr("no_pdf"), "warning")
                return

        dlg = NameDialog(self)
        name = dlg.get_result()
        if not name:
            return
        if not name.lower().endswith(".pdf"):
            name += ".pdf"

        out = filedialog.asksaveasfilename(title=tr("save_as"), defaultextension=".pdf",
                                            filetypes=[("PDF files", "*.pdf")], initialfile=name)
        if not out:
            return

        self.merge_btn.configure(state="disabled", text=tr("processing"))
        self.progress.set(0)
        self.progress.start()

        thread = threading.Thread(target=self._do, args=(paths, selections, out), daemon=True)
        thread.start()

    def _do(self, paths, selections, out):
        try:
            merge_pdfs(paths, selections, out)
            self.after(0, self._done, True, out)
        except Exception as e:
            self.after(0, self._done, False, str(e))

    def _done(self, ok, res):
        self.progress.stop()
        self.progress.set(1)
        self.merge_btn.configure(state="normal",
                                  text=f"  {tr('merge_btn')}  {ICONS['arrow_right']}")
        if ok:
            Toast.show(self, tr("success_merge"), "success")
        else:
            Toast.show(self, str(res), "error")

    def update_language(self):
        self.title.configure(text=tr("merge"))
        self.desc.configure(text=tr("merge_desc"))
        self.browse_btn.configure(text=f"  {ICONS['folder']}  {tr('browse_pdf')}")
        self.clear_btn.configure(text=f"  {ICONS['trash']}  {tr('clear_all')}")
        self.merge_btn.configure(text=f"  {tr('merge_btn')}  {ICONS['arrow_right']}")
