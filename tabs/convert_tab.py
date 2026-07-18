import customtkinter as ctk
import os
import threading
from tkinter import filedialog
from PIL import Image
import fitz
from theme import tr, ICONS, FONT, FONT_BOLD, FONT_SMALL, FONT_LARGE, Colors
from widgets.name_dialog import NameDialog
from widgets.toast import Toast
from utils.image_ops import images_to_pdf


class ConvertTab(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.app_ref = None
        self.pdf_path = None
        self.configure(fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build_header()
        self._build_mode_switcher()
        self._build_pdf_zone()
        self._build_settings()
        self._build_export()

    def _build_header(self):
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.grid(row=0, column=0, padx=28, pady=(28, 4), sticky="ew")

        row = ctk.CTkFrame(hdr, fg_color="transparent")
        row.pack(anchor="w")

        ctk.CTkLabel(row, text=ICONS["convert"], font=("Segoe UI", 28), text_color=Colors.PRIMARY).pack(side="left")
        self.header_title = ctk.CTkLabel(row, text=tr("convert"), font=FONT_LARGE, text_color=("#0f172a", Colors.TEXT))
        self.header_title.pack(side="left", padx=(10, 0))

        self.desc_lbl = ctk.CTkLabel(hdr, text=tr("convert_desc"), font=("Segoe UI", 12), text_color=("#64748b", Colors.TEXT_MUTED), anchor="w")
        self.desc_lbl.pack(anchor="w", padx=(38, 0), pady=(2, 0))

        accent = ctk.CTkFrame(hdr, height=3, fg_color=Colors.PRIMARY, corner_radius=2)
        accent.pack(fill="x", padx=0, pady=(10, 0))

    def _build_mode_switcher(self):
        sw = ctk.CTkFrame(self, fg_color="transparent")
        sw.grid(row=1, column=0, padx=28, pady=(12, 4), sticky="w")

        card = ctk.CTkFrame(sw, fg_color=("#ffffff", Colors.CARD), corner_radius=14, border_width=1, border_color=("#dce6ef", Colors.BORDER))
        card.pack(padx=0, pady=0)
        card.grid_columnconfigure(0, weight=1)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(padx=20, pady=14)

        self.mode_var = ctk.StringVar(value="pdf2img")
        modes = [
            ("pdf2img", tr("pdf_to_images")),
            ("img2pdf", tr("images_to_pdf")),
        ]
        for val, text in modes:
            rb = ctk.CTkRadioButton(inner, text=text, variable=self.mode_var, value=val,
                                     font=FONT, text_color=("#0f172a", Colors.TEXT),
                                     fg_color=Colors.PRIMARY, hover_color=Colors.PRIMARY_HOVER,
                                     border_color=("#cbd5e1", Colors.BORDER),
                                     border_width_unchecked=2,
                                     command=self._on_mode_change)
            rb.pack(side="left", padx=12)

    def _on_mode_change(self):
        if self.mode_var.get() == "pdf2img":
            self.pdf_frame.grid()
            self.img_list_frame.grid_remove()
        else:
            self.pdf_frame.grid_remove()
            self.img_list_frame.grid()

    def _build_pdf_zone(self):
        self.pdf_frame = ctk.CTkFrame(self, fg_color=("#ffffff", Colors.CARD), corner_radius=14, border_width=1, border_color=("#dce6ef", Colors.BORDER))
        self.pdf_frame.grid(row=2, column=0, padx=28, pady=8, sticky="nsew")
        self.pdf_frame.grid_columnconfigure(0, weight=1)
        self.pdf_frame.grid_rowconfigure(1, weight=1)

        self.pdf_drop_area = ctk.CTkFrame(self.pdf_frame, fg_color="transparent",
                                           border_width=2, border_color=("#5eead4", Colors.BORDER),
                                           corner_radius=12)
        self.pdf_drop_area.grid(row=0, column=0, padx=16, pady=(16, 8), sticky="ew")
        self.pdf_drop_area.grid_columnconfigure(0, weight=1)

        self.pdf_ph = ctk.CTkFrame(self.pdf_drop_area, fg_color="transparent")
        self.pdf_ph.pack(pady=24)
        ctk.CTkLabel(self.pdf_ph, text=ICONS["pdf"], font=("Segoe UI", 40),
                      text_color=("#94a3b8", Colors.TEXT_MUTED)).pack()
        ctk.CTkLabel(self.pdf_ph, text=tr("drop_pdf"), font=FONT,
                      text_color=("#64748b", Colors.TEXT_MUTED)).pack()
        ctk.CTkButton(self.pdf_ph, text=f"  {ICONS['folder']}  {tr('browse_pdf')}", command=self._browse_pdf,
                       font=FONT, corner_radius=20, height=38,
                       fg_color="transparent", border_color=Colors.PRIMARY, border_width=2,
                       hover_color=("#d4f0ee", Colors.SURFACE_ALT),
                       text_color=Colors.PRIMARY).pack(pady=8)

        self.pdf_info = ctk.CTkLabel(self.pdf_frame, text="", font=FONT,
                                      text_color=("#64748b", Colors.TEXT_MUTED))
        self.pdf_info.grid(row=1, column=0, padx=20, pady=4, sticky="w")

        self.img_list_frame = ctk.CTkFrame(self, fg_color=("#ffffff", Colors.CARD), corner_radius=14,
                                            border_width=1, border_color=("#dce6ef", Colors.BORDER))
        self.img_list_frame.grid(row=2, column=0, padx=28, pady=8, sticky="nsew")
        self.img_list_frame.grid_columnconfigure(0, weight=1)
        self.img_list_frame.grid_rowconfigure(0, weight=1)
        self.img_list_frame.grid_remove()

        self.img_list_box = ctk.CTkTextbox(self.img_list_frame, font=FONT,
                                            fg_color="transparent",
                                            corner_radius=8,
                                            text_color=("#0f172a", Colors.TEXT))
        self.img_list_box.grid(row=0, column=0, padx=12, pady=(12, 4), sticky="nsew")
        self.img_list_box.configure(state="disabled")

        btn_frame = ctk.CTkFrame(self.img_list_frame, fg_color="transparent")
        btn_frame.grid(row=1, column=0, pady=(4, 12))
        ctk.CTkButton(btn_frame, text=f"  {ICONS['folder']}  {tr('browse_images')}",
                       command=self._browse_images, height=38,
                       font=FONT, corner_radius=20,
                       fg_color="transparent", border_color=Colors.PRIMARY, border_width=2,
                       hover_color=("#d4f0ee", Colors.SURFACE_ALT),
                       text_color=Colors.PRIMARY).pack()

        self._imgs_for_pdf = []

    def _browse_pdf(self):
        path = filedialog.askopenfilename(title=tr("browse_pdf"),
                                           filetypes=[("PDF", "*.pdf")])
        if path:
            self._load_pdf(path)

    def _load_pdf(self, path):
        self.pdf_path = path
        try:
            doc = fitz.open(path)
            count = doc.page_count
            doc.close()
        except:
            count = 0
        name = os.path.basename(path)
        self.pdf_info.configure(text=f"{name}  \u2022  {count} {tr('pages')}")
        self.pdf_ph.pack_forget()
        pdf_lbl = ctk.CTkLabel(self.pdf_drop_area, text=f"{ICONS['pdf']}  {name}\n{count} {tr('pages')}",
                                font=("Segoe UI", 14), text_color=(Colors.PRIMARY, Colors.PRIMARY_LIGHT))
        pdf_lbl.pack(pady=28)
        self._pdf_display = pdf_lbl

    def handle_drop(self, paths):
        for p in paths:
            if p.lower().endswith(".pdf") and self.mode_var.get() == "pdf2img":
                self._load_pdf(p)
                return

    def _browse_images(self):
        files = filedialog.askopenfilenames(title=tr("browse_images"),
                                             filetypes=[("Images", "*.jpg *.jpeg *.png *.webp *.bmp *.gif")])
        exts = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif"}
        for f in files:
            if os.path.splitext(f)[1].lower() in exts:
                self._imgs_for_pdf.append(f)
        self._update_img_list()

    def _update_img_list(self):
        self.img_list_box.configure(state="normal")
        self.img_list_box.delete("1.0", "end")
        for i, p in enumerate(self._imgs_for_pdf, 1):
            self.img_list_box.insert("end", f"{i}. {os.path.basename(p)}\n")
        self.img_list_box.configure(state="disabled")

    def _build_settings(self):
        self.settings_frame = ctk.CTkFrame(self, fg_color=("#ffffff", Colors.CARD), corner_radius=14,
                                            border_width=1, border_color=("#dce6ef", Colors.BORDER))
        self.settings_frame.grid(row=3, column=0, padx=28, pady=8, sticky="ew")
        self.settings_frame.grid_columnconfigure(5, weight=1)

        ctk.CTkLabel(self.settings_frame, text=tr("settings"), font=FONT_BOLD,
                      text_color=("#0f172a", Colors.TEXT)
                      ).grid(row=0, column=0, padx=14, pady=12, sticky="w")

        ctk.CTkLabel(self.settings_frame, text=tr("output_format"), font=FONT,
                      text_color=("#64748b", Colors.TEXT_MUTED)
                      ).grid(row=0, column=1, padx=4)
        self.fmt_var = ctk.StringVar(value="PNG")
        ctk.CTkOptionMenu(self.settings_frame, variable=self.fmt_var,
                           values=["PNG", "JPEG", "WebP", "BMP", "TIFF"],
                           font=FONT, width=80,
                           fg_color=("#f1f5f9", Colors.SURFACE_ALT),
                           button_color=Colors.PRIMARY,
                           button_hover_color=Colors.PRIMARY_HOVER,
                           text_color=("#0f172a", Colors.TEXT)
                           ).grid(row=0, column=2, padx=4)

        ctk.CTkLabel(self.settings_frame, text="DPI", font=FONT,
                      text_color=("#64748b", Colors.TEXT_MUTED)
                      ).grid(row=0, column=3, padx=4)
        self.dpi_var = ctk.StringVar(value="200")
        ctk.CTkOptionMenu(self.settings_frame, variable=self.dpi_var,
                           values=["100", "150", "200", "300", "400", "600"],
                           font=FONT, width=70,
                           fg_color=("#f1f5f9", Colors.SURFACE_ALT),
                           button_color=Colors.PRIMARY,
                           button_hover_color=Colors.PRIMARY_HOVER,
                           text_color=("#0f172a", Colors.TEXT)
                           ).grid(row=0, column=4, padx=4)

        ctk.CTkLabel(self.settings_frame, text=tr("quality"), font=FONT,
                      text_color=("#64748b", Colors.TEXT_MUTED)
                      ).grid(row=0, column=5, padx=4, sticky="w")
        self.quality_var = ctk.StringVar(value="95")
        ctk.CTkOptionMenu(self.settings_frame, variable=self.quality_var,
                           values=["75", "85", "90", "95", "100"],
                           font=FONT, width=65,
                           fg_color=("#f1f5f9", Colors.SURFACE_ALT),
                           button_color=Colors.PRIMARY,
                           button_hover_color=Colors.PRIMARY_HOVER,
                           text_color=("#0f172a", Colors.TEXT)
                           ).grid(row=0, column=6, padx=4)

    def _build_export(self):
        bot = ctk.CTkFrame(self, fg_color="transparent")
        bot.grid(row=4, column=0, padx=28, pady=(6, 24), sticky="ew")
        bot.grid_columnconfigure(0, weight=1)

        self.progress = ctk.CTkProgressBar(bot, height=6, corner_radius=3,
                                            progress_color=Colors.PRIMARY)
        self.progress.grid(row=0, column=0, padx=2, pady=8, sticky="ew")
        self.progress.set(0)

        self.convert_btn = ctk.CTkButton(bot, text=f"  {tr('convert')}  {ICONS['convert']}",
                                           command=self._convert, height=44,
                                           font=FONT_BOLD, corner_radius=22,
                                           fg_color=Colors.PRIMARY, hover_color=Colors.PRIMARY_HOVER,
                                           text_color="#ffffff")
        self.convert_btn.grid(row=0, column=1, padx=8)

    def _convert(self):
        mode = self.mode_var.get()
        if mode == "pdf2img":
            self._convert_pdf_to_images()
        else:
            self._convert_images_to_pdf()

    def _convert_pdf_to_images(self):
        if not self.pdf_path:
            Toast.show(self, tr("no_pdf_selected"), "warning")
            return

        fmt = self.fmt_var.get().lower()
        dpi = int(self.dpi_var.get())
        quality = int(self.quality_var.get())

        out_dir = filedialog.askdirectory(title=tr("select_folder"))
        if not out_dir:
            return

        base = os.path.splitext(os.path.basename(self.pdf_path))[0]

        self.convert_btn.configure(state="disabled", text=tr("processing"))
        self.progress.start()

        def do():
            try:
                doc = fitz.open(self.pdf_path)
                total = doc.page_count
                save_kw = {"quality": quality} if fmt != "png" else {}
                ext = "jpg" if fmt == "jpeg" else fmt

                for i in range(total):
                    page = doc[i]
                    zoom = dpi / 72
                    mat = fitz.Matrix(zoom, zoom)
                    pix = page.get_pixmap(matrix=mat, alpha=False)
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    out_path = os.path.join(out_dir, f"{base}_page_{i+1}.{ext}")
                    img.save(out_path, fmt.upper(), **save_kw)
                    self.after(0, lambda v=(i+1)/total: self.progress.configure(value=v))

                doc.close()
                self.after(0, self._done, True, tr("success_convert"))
            except Exception as e:
                self.after(0, self._done, False, str(e))

        threading.Thread(target=do, daemon=True).start()

    def _convert_images_to_pdf(self):
        if not self._imgs_for_pdf:
            Toast.show(self, tr("no_images"), "warning")
            return

        dlg = NameDialog(self)
        name = dlg.get_result()
        if not name:
            return
        if not name.lower().endswith(".pdf"):
            name += ".pdf"

        out = filedialog.asksaveasfilename(title=tr("save_as"), defaultextension=".pdf",
                                            filetypes=[("PDF", "*.pdf")], initialfile=name)
        if not out:
            return

        self.convert_btn.configure(state="disabled", text=tr("processing"))
        self.progress.start()

        def do():
            try:
                images_to_pdf(self._imgs_for_pdf, out)
                self.after(0, self._done, True, tr("success_export"))
            except Exception as e:
                self.after(0, self._done, False, str(e))

        threading.Thread(target=do, daemon=True).start()

    def _done(self, ok, msg):
        self.progress.stop()
        self.progress.set(1)
        self.convert_btn.configure(state="normal", text=f"  {tr('convert')}  {ICONS['convert']}")
        if ok:
            Toast.show(self, msg, "success")
        else:
            Toast.show(self, msg, "error")

    def update_language(self):
        self.header_title.configure(text=tr("convert"))
        self.desc_lbl.configure(text=tr("convert_desc"))
        self.convert_btn.configure(text=f"  {tr('convert')}  {ICONS['convert']}")
