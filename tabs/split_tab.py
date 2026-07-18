import customtkinter as ctk
import os
import threading
from tkinter import filedialog
from theme import tr, ICONS, FONT, FONT_BOLD, FONT_SMALL, FONT_LARGE, Colors
from widgets.name_dialog import NameDialog
from widgets.toast import Toast
from utils.pdf_ops import extract_pages_single, extract_pages_multiple, get_page_count, get_page_thumbnail


class SplitTab(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="transparent")
        self.pdf_path = None
        self.checkboxes = []
        self.card_refs = []
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.grid(row=0, column=0, padx=28, pady=(28, 4), sticky="ew")
        hdr.grid_columnconfigure(1, weight=1)

        icon_bg = ctk.CTkFrame(hdr, width=40, height=40, corner_radius=12,
                                fg_color="#ff6600")
        icon_bg.grid(row=0, column=0, sticky="w")
        icon_bg.grid_propagate(False)
        ctk.CTkLabel(icon_bg, text="✂", font=("Segoe UI", 18),
                      text_color="#ffffff").place(relx=0.5, rely=0.5, anchor="center")

        self.title = ctk.CTkLabel(hdr, text=tr("split"), font=FONT_LARGE,
                                  text_color=("#0f172a", Colors.TEXT))
        self.title.grid(row=0, column=1, sticky="w", padx=(12, 0))

        self.desc = ctk.CTkLabel(hdr, text=tr("split_desc"), font=("Segoe UI", 12),
                                 text_color=("#64748b", Colors.TEXT_MUTED))
        self.desc.grid(row=1, column=1, sticky="w", padx=(12, 0), pady=(2, 0))

        accent = ctk.CTkFrame(hdr, height=3, fg_color="#ff6600",
                               corner_radius=2)
        accent.grid(row=2, column=0, columnspan=2, sticky="ew", padx=0, pady=(10, 0))

        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.grid(row=1, column=0, padx=28, pady=(10, 8), sticky="ew")
        bar.grid_columnconfigure(2, weight=1)

        self.open_btn = ctk.CTkButton(bar, text=f"  {ICONS['folder']}  {tr('browse_pdf')}",
                                       height=38,
                                       font=FONT,
                                       fg_color="transparent",
                                       border_color=Colors.PRIMARY,
                                       border_width=2,
                                       hover_color=("#d4f0ee", Colors.SURFACE_ALT),
                                       text_color=Colors.PRIMARY,
                                       corner_radius=20,
                                       command=self.open_pdf)
        self.open_btn.grid(row=0, column=0, padx=2)

        self.sel_all_btn = ctk.CTkButton(bar, text=tr("select_all"), height=38,
                                           font=FONT,
                                           fg_color="transparent",
                                           hover_color=("#f1f5f9", Colors.SURFACE_ALT),
                                           text_color=("#64748b", Colors.TEXT_MUTED),
                                           corner_radius=18,
                                           command=self.toggle_select_all, state="disabled")
        self.sel_all_btn.grid(row=0, column=1, padx=2)

        self.fn_lbl = ctk.CTkLabel(bar, text="", font=FONT_SMALL,
                                    text_color=("#64748b", Colors.TEXT_MUTED))
        self.fn_lbl.grid(row=0, column=2, padx=8, sticky="e")

        opt_bar = ctk.CTkFrame(self, fg_color="transparent")
        opt_bar.grid(row=2, column=0, padx=28, sticky="ew")
        opt_bar.grid_columnconfigure(0, weight=1)

        self.info_lbl = ctk.CTkLabel(opt_bar, text="", font=FONT_SMALL,
                                      text_color=("#64748b", Colors.TEXT_MUTED))
        self.info_lbl.grid(row=0, column=0, padx=2, sticky="w")

        self.out_type = ctk.StringVar(value="single")
        ctk.CTkRadioButton(opt_bar, text=tr("single_file"), variable=self.out_type,
                            value="single", font=FONT,
                            fg_color=Colors.PRIMARY, hover_color=Colors.PRIMARY_HOVER,
                            text_color=("#0f172a", Colors.TEXT)
                            ).grid(row=0, column=1, padx=8)
        ctk.CTkRadioButton(opt_bar, text=tr("separate_files"), variable=self.out_type,
                            value="multiple", font=FONT,
                            fg_color=Colors.PRIMARY, hover_color=Colors.PRIMARY_HOVER,
                            text_color=("#0f172a", Colors.TEXT)
                            ).grid(row=0, column=2, padx=8)

        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.grid(row=3, column=0, padx=28, pady=4, sticky="nsew")

        self.empty_lbl = ctk.CTkLabel(self.scroll,
                                       text=f"{ICONS['pdf']}\n{tr('drop_pdf')}",
                                       font=("Segoe UI", 14),
                                       text_color=("#94a3b8", Colors.TEXT_MUTED))
        self.empty_lbl.pack(expand=True, pady=80)

        bot = ctk.CTkFrame(self, fg_color="transparent")
        bot.grid(row=4, column=0, padx=28, pady=(8, 24), sticky="ew")
        bot.grid_columnconfigure(0, weight=1)

        self.progress = ctk.CTkProgressBar(bot, height=6, corner_radius=3,
                                            progress_color=Colors.PRIMARY)
        self.progress.grid(row=0, column=0, padx=2, pady=8, sticky="ew")
        self.progress.set(0)

        self.extract_btn = ctk.CTkButton(bot,
                                          text=f"  {tr('extract_btn')}  {ICONS['arrow_right']}",
                                          height=44,
                                          font=FONT_BOLD,
                                          fg_color=Colors.PRIMARY,
                                          hover_color=Colors.PRIMARY_HOVER,
                                          corner_radius=22,
                                          text_color="#ffffff",
                                          command=self.extract_pages, state="disabled")
        self.extract_btn.grid(row=0, column=1, padx=8)

    def open_pdf(self, path=None):
        if not path:
            path = filedialog.askopenfilename(title=tr("browse_pdf"),
                                              filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")])
        if not path:
            return
        if not path.lower().endswith(".pdf"):
            Toast.show(self, tr("error"), "error")
            return

        self.pdf_path = path
        self._clear_cards()

        self.empty_lbl.pack_forget()
        self.fn_lbl.configure(text=os.path.basename(path))

        total = get_page_count(path)
        self.info_lbl.configure(text=f"{ICONS['pdf']} {os.path.basename(path)}  ·  {total} {tr('pages')}")

        cols = max(2, min(5, (self.scroll.winfo_width() - 20) // 150))
        for i in range(cols):
            self.scroll.grid_columnconfigure(i, weight=1, uniform="pgc")

        for i in range(total):
            r = i // cols
            c = i % cols

            card = ctk.CTkFrame(self.scroll, fg_color=("#ffffff", Colors.CARD),
                                 corner_radius=10, height=185,
                                 border_width=1, border_color=("#dce6ef", Colors.BORDER))
            card.grid(row=r, column=c, padx=4, pady=4, sticky="nsew")
            card.grid_propagate(False)
            card.grid_columnconfigure(0, weight=1)
            self.card_refs.append(card)

            var = ctk.BooleanVar(value=True)
            cb = ctk.CTkCheckBox(card, text=f"{tr('page')} {i+1}", variable=var,
                                  font=FONT_SMALL,
                                  fg_color=Colors.PRIMARY, hover_color=Colors.PRIMARY_HOVER,
                                  text_color=("#0f172a", Colors.TEXT))
            cb.grid(row=0, column=0, padx=8, pady=(6, 0), sticky="w")
            self.checkboxes.append(var)

            img_lbl = ctk.CTkLabel(card, text="", width=120, height=140)
            img_lbl.grid(row=1, column=0, padx=4, pady=(0, 4))

            try:
                img = get_page_thumbnail(path, i)
                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(img.width, img.height))
                img_lbl.configure(image=ctk_img, text="")
            except:
                img_lbl.configure(text=f"{tr('page')} {i+1}")

        self.extract_btn.configure(state="normal")
        self.sel_all_btn.configure(state="normal")

    def _clear_cards(self):
        for w in self.card_refs:
            w.destroy()
        self.card_refs.clear()
        self.checkboxes.clear()

    def toggle_select_all(self):
        on = not all(cb.get() for cb in self.checkboxes)
        for cb in self.checkboxes:
            cb.set(on)
        self.sel_all_btn.configure(text=tr("deselect_all") if on else tr("select_all"))

    def handle_drop(self, paths):
        if paths:
            self.open_pdf(paths[0])

    def extract_pages(self):
        if not self.pdf_path:
            return
        selected = [i for i, cb in enumerate(self.checkboxes) if cb.get()]
        if not selected:
            Toast.show(self, tr("no_pdf"), "warning")
            return

        dlg = NameDialog(self)
        name = dlg.get_result()
        if not name:
            return

        if self.out_type.get() == "single":
            if not name.lower().endswith(".pdf"):
                name += ".pdf"
            out = filedialog.asksaveasfilename(title=tr("save_as"), defaultextension=".pdf",
                                                filetypes=[("PDF files", "*.pdf")], initialfile=name)
            if not out:
                return
            self._start_extract("single", selected, out, None, None)
        else:
            out_dir = filedialog.askdirectory(title=tr("select_folder"))
            if not out_dir:
                return
            self._start_extract("multiple", selected, None, out_dir, name)

    def _start_extract(self, mode, pages, out, out_dir, base):
        self.extract_btn.configure(state="disabled", text=tr("processing"))
        self.progress.set(0)
        self.progress.start()

        if mode == "single":
            thread = threading.Thread(target=self._do_single, args=(pages, out), daemon=True)
        else:
            thread = threading.Thread(target=self._do_multi, args=(pages, out_dir, base), daemon=True)
        thread.start()

    def _do_single(self, pages, out):
        try:
            extract_pages_single(self.pdf_path, pages, out)
            self.after(0, self._done, True, tr("success_extract"))
        except Exception as e:
            self.after(0, self._done, False, str(e))

    def _do_multi(self, pages, out_dir, base):
        try:
            extract_pages_multiple(self.pdf_path, pages, out_dir, base)
            self.after(0, self._done, True, f"{len(pages)} {tr('files')} {tr('success_extract')}")
        except Exception as e:
            self.after(0, self._done, False, str(e))

    def _done(self, ok, msg):
        self.progress.stop()
        self.progress.set(1)
        self.extract_btn.configure(state="normal",
                                    text=f"  {tr('extract_btn')}  {ICONS['arrow_right']}")
        if ok:
            Toast.show(self, msg, "success")
        else:
            Toast.show(self, msg, "error")

    def update_language(self):
        self.title.configure(text=tr("split"))
        self.desc.configure(text=tr("split_desc"))
        self.open_btn.configure(text=f"  {ICONS['folder']}  {tr('browse_pdf')}")
        self.extract_btn.configure(text=f"  {tr('extract_btn')}  {ICONS['arrow_right']}")
