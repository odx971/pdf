import customtkinter as ctk
from theme import tr, FONT, FONT_BOLD, FONT_SMALL, ICONS, Colors


class NameDialog(ctk.CTkToplevel):
    def __init__(self, parent, title=tr("export_name"), hint=tr("pdf_name_hint"), prompt=None, initial=""):
        super().__init__(parent)
        self.result = None

        self.overrideredirect(True)
        self.attributes("-topmost", True)

        parent.update_idletasks()
        p_x = parent.winfo_rootx()
        p_y = parent.winfo_rooty()
        p_w = parent.winfo_width()
        p_h = parent.winfo_height()
        d_w, d_h = 440, 210
        x = p_x + (p_w - d_w) // 2
        y = p_y + (p_h - d_h) // 2
        self.geometry(f"{d_w}x{d_h}+{x}+{y}")

        self.configure(fg_color=("#ffffff", Colors.CARD))

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent", height=40)
        header.grid(row=0, column=0, padx=20, pady=(16, 0), sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(header, text=title, font=FONT_BOLD,
                      anchor="w", text_color=("#0f172a", Colors.TEXT)
                      ).pack(side="left")

        close_btn = ctk.CTkButton(header, text=ICONS["close"], width=30, height=30,
                                   font=("Segoe UI", 14),
                                   fg_color="transparent",
                                   hover_color=("#f1f5f9", Colors.SURFACE_ALT),
                                   text_color=("#64748b", Colors.TEXT_MUTED),
                                   corner_radius=8,
                                   command=self.cancel)
        close_btn.pack(side="right")

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.grid(row=1, column=0, padx=20, pady=8, sticky="nsew")
        body.grid_rowconfigure(1, weight=1)
        body.grid_columnconfigure(0, weight=1)

        self.name_var = ctk.StringVar(value=initial)
        self.entry = ctk.CTkEntry(body, textvariable=self.name_var,
                                   font=("Segoe UI", 14),
                                   placeholder_text=hint or prompt,
                                   height=44,
                                   corner_radius=10,
                                   border_color=("#cbd5e1", Colors.BORDER_LIGHT),
                                   fg_color=("#f8fafc", "#0d0d20"),
                                   text_color=("#0f172a", Colors.TEXT))
        self.entry.grid(row=0, column=0, padx=4, pady=4, sticky="ew")
        self.entry.focus_set()
        self.entry.bind("<Return>", lambda e: self.confirm())
        self.entry.bind("<Escape>", lambda e: self.cancel())

        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.grid(row=2, column=0, padx=20, pady=(0, 14), sticky="ew")
        footer.grid_columnconfigure(0, weight=1)

        cancel_btn = ctk.CTkButton(footer, text=tr("cancel"), width=90, height=36,
                                    font=FONT,
                                    fg_color="transparent",
                                    hover_color=("#f1f5f9", Colors.SURFACE_ALT),
                                    text_color=("#64748b", Colors.TEXT_MUTED),
                                    corner_radius=20,
                                    command=self.cancel)
        cancel_btn.pack(side="right", padx=4)

        confirm_btn = ctk.CTkButton(footer, text=tr("confirm"), width=110, height=36,
                                     font=FONT_BOLD,
                                     fg_color=Colors.PRIMARY,
                                     hover_color=Colors.PRIMARY_HOVER,
                                     corner_radius=20,
                                     command=self.confirm)
        confirm_btn.pack(side="right", padx=4)

        self.transient(parent)
        self.grab_set()

    def confirm(self):
        self.result = self.name_var.get().strip()
        if self.result:
            self.destroy()

    def cancel(self):
        self.result = None
        self.destroy()

    def get_result(self):
        self.wait_window()
        return self.result
