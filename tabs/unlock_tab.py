import customtkinter as ctk
import os
import threading
from tkinter import filedialog
from theme import tr, ICONS, FONT, FONT_BOLD, FONT_SMALL, FONT_LARGE, Colors
from widgets.name_dialog import NameDialog
from widgets.toast import Toast
from utils.pdf_ops import unlock_pdf, get_page_count, is_pdf_encrypted


class UnlockTab(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="transparent")
        self.pdf_path = None
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.grid(row=0, column=0, padx=28, pady=(28, 4), sticky="ew")

        row = ctk.CTkFrame(hdr, fg_color="transparent")
        row.pack(anchor="w")

        icon_bg = ctk.CTkFrame(row, width=40, height=40, corner_radius=12,
                                fg_color="#00c853")
        icon_bg.pack(side="left")
        icon_bg.pack_propagate(False)
        ctk.CTkLabel(icon_bg, text="🔓", font=("Segoe UI", 18),
                      text_color="#ffffff").place(relx=0.5, rely=0.5, anchor="center")

        self.title = ctk.CTkLabel(row, text=tr("unlock"), font=FONT_LARGE,
                                  text_color=("#0f172a", Colors.TEXT))
        self.title.pack(side="left", padx=(12, 0))

        self.desc = ctk.CTkLabel(hdr, text=tr("unlock_desc"), font=("Segoe UI", 12),
                                 text_color=("#64748b", Colors.TEXT_MUTED), anchor="w")
        self.desc.pack(anchor="w", padx=(52, 0), pady=(2, 0))

        accent = ctk.CTkFrame(hdr, height=3, fg_color="#00c853", corner_radius=2)
        accent.pack(fill="x", padx=0, pady=(10, 0))

        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.grid(row=1, column=0, padx=28, pady=(12, 8), sticky="ew")
        bar.grid_columnconfigure(1, weight=1)

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

        self.fn_lbl = ctk.CTkLabel(bar, text="", font=FONT_SMALL,
                                     text_color=("#64748b", Colors.TEXT_MUTED))
        self.fn_lbl.grid(row=0, column=1, padx=8, sticky="w")

        self.status_lbl = ctk.CTkLabel(bar, text="", font=FONT_BOLD)
        self.status_lbl.grid(row=0, column=2, padx=8, sticky="e")

        center = ctk.CTkFrame(self, fg_color="transparent")
        center.grid(row=2, column=0, padx=28, pady=4, sticky="nsew")
        center.grid_columnconfigure(0, weight=1)
        center.grid_rowconfigure(0, weight=1)

        self.drop_frame = ctk.CTkFrame(center,
                                        fg_color=("#ffffff", Colors.CARD),
                                        corner_radius=14, border_width=2,
                                        border_color=("#5eead4", Colors.BORDER))
        self.drop_frame.grid(row=0, column=0, sticky="nsew")
        self.drop_frame.grid_columnconfigure(0, weight=1)
        self.drop_frame.grid_rowconfigure(0, weight=1)

        self.empty_state = ctk.CTkFrame(self.drop_frame, fg_color="transparent")
        self.empty_state.grid(row=0, column=0, pady=60)

        ctk.CTkLabel(self.empty_state, text=ICONS["lock"], font=("Segoe UI", 52),
                      text_color=("#94a3b8", Colors.TEXT_MUTED)).pack()
        ctk.CTkLabel(self.empty_state, text=tr("drop_pdf"), font=("Segoe UI", 14),
                      text_color=("#64748b", Colors.TEXT_MUTED)).pack(pady=(10, 0))
        ctk.CTkLabel(self.empty_state, text=tr("or_browse"), font=FONT_SMALL,
                      text_color=(Colors.PRIMARY, Colors.PRIMARY_LIGHT), cursor="hand2").pack(pady=(6, 0))

        self.file_frame = ctk.CTkFrame(self.drop_frame, fg_color="transparent")
        self.file_frame.grid(row=0, column=0, padx=24, pady=24, sticky="nsew")
        self.file_frame.grid_columnconfigure(0, weight=1)
        self.file_frame.grid_rowconfigure(2, weight=1)
        self.file_frame.grid_remove()

        file_card = ctk.CTkFrame(self.file_frame,
                                  fg_color=("#ffffff", Colors.CARD),
                                  corner_radius=14,
                                  border_width=1,
                                  border_color=("#dce6ef", Colors.BORDER))
        file_card.grid(row=0, column=0, padx=4, pady=(0, 12), sticky="ew")
        file_card.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(file_card, text=ICONS["pdf"], font=("Segoe UI", 36),
                      text_color=(Colors.PRIMARY, Colors.PRIMARY_LIGHT)).grid(
            row=0, column=0, rowspan=2, padx=20, pady=14)

        self.file_name_lbl = ctk.CTkLabel(file_card, text="", font=FONT_LARGE,
                                            anchor="w", justify="left",
                                            text_color=("#0f172a", Colors.TEXT))
        self.file_name_lbl.grid(row=0, column=1, padx=4, pady=(14, 2), sticky="w")

        self.file_info_lbl = ctk.CTkLabel(file_card, text="", font=FONT,
                                            text_color=("#64748b", Colors.TEXT_MUTED), anchor="w")
        self.file_info_lbl.grid(row=1, column=1, padx=4, pady=(0, 14), sticky="w")

        pw_frame = ctk.CTkFrame(self.file_frame,
                                 fg_color=("#ffffff", Colors.CARD),
                                 corner_radius=14,
                                 border_width=1,
                                 border_color=("#dce6ef", Colors.BORDER))
        pw_frame.grid(row=1, column=0, padx=4, pady=4, sticky="ew")
        pw_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(pw_frame, text=ICONS["key"], font=("Segoe UI", 24),
                      text_color=(Colors.PRIMARY, Colors.PRIMARY_LIGHT)).grid(
            row=0, column=0, padx=20, pady=16)

        pw_inner = ctk.CTkFrame(pw_frame, fg_color="transparent")
        pw_inner.grid(row=0, column=1, padx=4, pady=16, sticky="ew")
        pw_inner.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(pw_inner, text=tr("password"), font=FONT_BOLD,
                      anchor="w", text_color=("#0f172a", Colors.TEXT)
                      ).grid(row=0, column=0, sticky="w")

        entry_row = ctk.CTkFrame(pw_inner, fg_color="transparent")
        entry_row.grid(row=1, column=0, sticky="ew", pady=(6, 0))
        entry_row.grid_columnconfigure(0, weight=1)

        self.pw_var = ctk.StringVar()
        self.pw_entry = ctk.CTkEntry(entry_row, textvariable=self.pw_var,
                                       font=("Segoe UI", 14), height=44,
                                       corner_radius=10, show="\u2022",
                                       placeholder_text=tr("enter_password"),
                                       border_color=("#cbd5e1", Colors.BORDER_LIGHT),
                                       fg_color=("#f8fafc", "#0d0d20"),
                                       text_color=("#0f172a", Colors.TEXT))
        self.pw_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        self.show_pw_var = ctk.BooleanVar(value=False)
        self.show_pw_btn = ctk.CTkButton(entry_row, text=ICONS["eye"], width=42, height=42,
                                           font=("Segoe UI", 16),
                                           fg_color="transparent",
                                           hover_color=("#f1f5f9", Colors.SURFACE_ALT),
                                           text_color=("#64748b", Colors.TEXT_MUTED),
                                           corner_radius=10,
                                           command=self._toggle_password)
        self.show_pw_btn.grid(row=0, column=1)

        self.info_lbl = ctk.CTkLabel(self.file_frame, text="", font=FONT,
                                      text_color=("#64748b", Colors.TEXT_MUTED), anchor="w")
        self.info_lbl.grid(row=2, column=0, padx=4, pady=8, sticky="w")

        bot = ctk.CTkFrame(self, fg_color="transparent")
        bot.grid(row=3, column=0, padx=28, pady=(4, 24), sticky="ew")
        bot.grid_columnconfigure(0, weight=1)

        self.progress = ctk.CTkProgressBar(bot, height=6, corner_radius=3,
                                            progress_color=Colors.PRIMARY)
        self.progress.grid(row=0, column=0, padx=2, pady=8, sticky="ew")
        self.progress.set(0)

        self.unlock_btn = ctk.CTkButton(bot,
                                          text=f"  {tr('unlock_btn')}  {ICONS['unlock_icon']}",
                                          height=44,
                                          font=FONT_BOLD,
                                          fg_color=Colors.PRIMARY,
                                          hover_color=Colors.PRIMARY_HOVER,
                                          corner_radius=22,
                                          command=self.unlock_pdf, state="disabled")
        self.unlock_btn.grid(row=0, column=1, padx=8)

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
        self.empty_state.grid_remove()
        self.file_frame.grid()

        name = os.path.basename(path)
        total = get_page_count(path)
        encrypted = is_pdf_encrypted(path)

        self.file_name_lbl.configure(text=name)
        self.file_info_lbl.configure(text=f"{total} {tr('pages')}")

        if encrypted:
            self.status_lbl.configure(text=f"{ICONS['lock']} {tr('locked')}",
                                       text_color=Colors.DANGER)
            self.info_lbl.configure(text=tr("unlock_desc"))
            self.unlock_btn.configure(state="normal")
        else:
            self.status_lbl.configure(text=f"{ICONS['unlock_icon']} {tr('unlocked')}",
                                       text_color=Colors.SUCCESS)
            self.info_lbl.configure(text=tr("file_not_encrypted"))
            self.unlock_btn.configure(state="disabled")

        self.fn_lbl.configure(text=name)

    def _toggle_password(self):
        show = self.show_pw_var.get()
        self.show_pw_var.set(not show)
        self.pw_entry.configure(show="" if not show else "\u2022")
        self.show_pw_btn.configure(text=ICONS["eye"] if not show else ICONS["eye_off"])

    def handle_drop(self, paths):
        if paths:
            self.open_pdf(paths[0])

    def unlock_pdf(self):
        if not self.pdf_path:
            return

        password = self.pw_var.get()
        if not password:
            Toast.show(self, tr("enter_password"), "warning")
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

        self.unlock_btn.configure(state="disabled", text=tr("processing"))
        self.progress.set(0)
        self.progress.start()

        thread = threading.Thread(target=self._do, args=(self.pdf_path, password, out), daemon=True)
        thread.start()

    def _do(self, path, password, out):
        try:
            ok, msg = unlock_pdf(path, password, out)
            self.after(0, self._done, ok, msg)
        except Exception as e:
            self.after(0, self._done, False, str(e))

    def _done(self, ok, msg):
        self.progress.stop()
        self.progress.set(1)
        self.unlock_btn.configure(state="normal",
                                   text=f"  {tr('unlock_btn')}  {ICONS['unlock_icon']}")

        if ok:
            if msg == "not_encrypted":
                Toast.show(self, tr("file_not_encrypted"), "info")
            else:
                Toast.show(self, tr("success_unlock"), "success")
        else:
            if msg == "wrong_password":
                Toast.show(self, tr("wrong_password"), "error")
            else:
                Toast.show(self, msg, "error")

    def update_language(self):
        self.title.configure(text=tr("unlock"))
        self.desc.configure(text=tr("unlock_desc"))
        self.open_btn.configure(text=f"  {ICONS['folder']}  {tr('browse_pdf')}")
        self.unlock_btn.configure(text=f"  {tr('unlock_btn')}  {ICONS['unlock_icon']}")
        self.pw_entry.configure(placeholder_text=tr("enter_password"))
