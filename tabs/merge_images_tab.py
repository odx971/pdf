import customtkinter as ctk
import os
import threading
import tempfile
from tkinter import filedialog
from PIL import Image, ImageEnhance
from theme import tr, ICONS, FONT, FONT_BOLD, FONT_SMALL, FONT_LARGE, Colors
from widgets.name_dialog import NameDialog
from widgets.toast import Toast
from utils.image_ops import images_to_pdf


class ImageDropZone(ctk.CTkFrame):
    def __init__(self, master, title_key, on_load=None):
        super().__init__(master)
        self.title_key = title_key
        self.on_load = on_load
        self.file_path = None
        self.pil_image = None
        self._loaded = False

        self.configure(fg_color=("#ffffff", Colors.CARD), corner_radius=14,
                       border_width=1, border_color=("#dce6ef", Colors.BORDER))
        self.grid_propagate(False)

        self.title_lbl = ctk.CTkLabel(
            self, text=tr(title_key),
            font=FONT_BOLD,
            text_color=("#0f172a", Colors.TEXT)
        )
        self.title_lbl.pack(pady=(14, 6))

        self.drop_area = ctk.CTkFrame(
            self, fg_color="transparent",
            border_width=2, border_color=("#5eead4", Colors.BORDER),
            corner_radius=12
        )
        self.drop_area.pack(fill="both", padx=12, pady=2, expand=True)
        self.drop_area.grid_propagate(False)

        self.ph = ctk.CTkFrame(self.drop_area, fg_color="transparent")
        self.ph.place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(
            self.ph,
            text=ICONS["image"],
            font=("Segoe UI", 36),
            text_color=Colors.PRIMARY_LIGHT,
        ).pack()
        self.ph_text = ctk.CTkLabel(
            self.ph,
            text=tr("drop_image"),
            font=FONT_SMALL,
            text_color=("#64748b", Colors.TEXT_MUTED),
        )
        self.ph_text.pack()

        self.img_lbl = ctk.CTkLabel(self.drop_area, text="")

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(fill="x", padx=12, pady=(6, 14))

        ctk.CTkButton(
            btn_row,
            text=f"{ICONS['folder']} {tr('browse')}",
            command=self._browse,
            height=30,
            font=FONT_SMALL,
            corner_radius=18,
            fg_color="transparent",
            hover_color=("#f1f5f9", Colors.SURFACE_ALT),
            text_color=Colors.PRIMARY,
            border_width=1, border_color=Colors.PRIMARY,
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            btn_row,
            text=f"{ICONS['trash']} {tr('clear_all')}",
            command=self._clear,
            height=30,
            font=FONT_SMALL,
            corner_radius=18,
            fg_color="transparent",
            hover_color=("#fef2f2", "#2d1015"),
            text_color=("#ef4444", "#f87171"),
        ).pack(side="right", padx=2)

    def _browse(self):
        path = filedialog.askopenfilename(
            title=tr(self.title_key),
            filetypes=[("Images", "*.jpg *.jpeg *.png *.webp *.bmp *.gif")],
        )
        if path:
            self.load_image(path)

    def _clear(self):
        self.file_path = None
        self.pil_image = None
        self._loaded = False
        self.img_lbl.place_forget()
        self.ph.place(relx=0.5, rely=0.5, anchor="center")
        if self.on_load:
            self.on_load(None)

    def load_image(self, path):
        try:
            img = Image.open(path)
            self.file_path = path
            self.pil_image = img.copy()
            self._loaded = True

            thumb = img.copy()
            thumb.thumbnail((180, 140), Image.LANCZOS)
            ctk_img = ctk.CTkImage(
                light_image=thumb, dark_image=thumb, size=(thumb.width, thumb.height)
            )
            self.img_lbl.configure(image=ctk_img)
            self.ph.place_forget()
            self.img_lbl.place(relx=0.5, rely=0.5, anchor="center")

            if self.on_load:
                self.on_load(path)
        except Exception:
            pass

    def update_language(self):
        self.title_lbl.configure(text=tr(self.title_key))
        self.ph_text.configure(text=tr("drop_image"))


class MergeImagesTab(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.app_ref = None
        self.configure(fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self._live_preview_after = None

        self._build_header()
        self._build_drop_zones()
        self._build_settings()
        self._build_preview()
        self._build_export()

    def _build_header(self):
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.grid(row=0, column=0, padx=28, pady=(28, 4), sticky="ew")

        row = ctk.CTkFrame(hdr, fg_color="transparent")
        row.pack(anchor="w")

        ctk.CTkLabel(
            row,
            text=ICONS["merge_images"],
            font=("Segoe UI", 28),
            text_color=Colors.PRIMARY,
        ).pack(side="left")
        self.header_title = ctk.CTkLabel(
            row, text=tr("merge_images"), font=FONT_LARGE,
            text_color=("#0f172a", Colors.TEXT)
        )
        self.header_title.pack(side="left", padx=(10, 0))

        self.desc_lbl = ctk.CTkLabel(
            hdr,
            text=tr("merge_images_desc"),
            font=("Segoe UI", 12),
            text_color=("#64748b", Colors.TEXT_MUTED),
            anchor="w",
        )
        self.desc_lbl.pack(anchor="w", padx=(38, 0), pady=(2, 0))

        accent = ctk.CTkFrame(hdr, height=3, fg_color=Colors.PRIMARY, corner_radius=2)
        accent.pack(fill="x", padx=0, pady=(10, 0))

    def _build_drop_zones(self):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.grid(row=1, column=0, padx=24, pady=4, sticky="ew")
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=1)
        container.grid_rowconfigure(0, weight=1)

        self.img1_zone = ImageDropZone(
            container, "image1", on_load=lambda p: self._on_zone_loaded()
        )
        self.img1_zone.grid(row=0, column=0, padx=(0, 8), pady=4, sticky="nsew")

        self.img2_zone = ImageDropZone(
            container, "image2", on_load=lambda p: self._on_zone_loaded()
        )
        self.img2_zone.grid(row=0, column=1, padx=(8, 0), pady=4, sticky="nsew")

    def _on_zone_loaded(self):
        self._update_live_preview()

    def _build_settings(self):
        settings = ctk.CTkFrame(
            self,
            fg_color=("#ffffff", Colors.CARD),
            corner_radius=14,
            border_width=1,
            border_color=("#dce6ef", Colors.BORDER),
        )
        settings.grid(row=2, column=0, padx=24, pady=6, sticky="ew")
        settings.grid_columnconfigure(3, weight=1)

        ctk.CTkLabel(
            settings, text=tr("layout"), font=FONT_BOLD,
            text_color=("#0f172a", Colors.TEXT)
        ).grid(row=0, column=0, padx=14, pady=10, sticky="w")

        self.layout_var = ctk.StringVar(value="horizontal")
        ctk.CTkRadioButton(
            settings,
            text=tr("horizontal"),
            variable=self.layout_var,
            value="horizontal",
            font=FONT,
            fg_color=Colors.PRIMARY,
            hover_color=Colors.PRIMARY_HOVER,
            text_color=("#0f172a", Colors.TEXT),
            command=self._debounced_live_preview,
        ).grid(row=0, column=1, padx=4)
        ctk.CTkRadioButton(
            settings,
            text=tr("vertical"),
            variable=self.layout_var,
            value="vertical",
            font=FONT,
            fg_color=Colors.PRIMARY,
            hover_color=Colors.PRIMARY_HOVER,
            text_color=("#0f172a", Colors.TEXT),
            command=self._debounced_live_preview,
        ).grid(row=0, column=2, padx=12)

        ctk.CTkLabel(
            settings, text=tr("margin"), font=FONT,
            text_color=("#64748b", Colors.TEXT_MUTED)
        ).grid(row=0, column=3, padx=4, sticky="e")
        self.margin_var = ctk.StringVar(value="10")
        margin_menu = ctk.CTkOptionMenu(
            settings,
            variable=self.margin_var,
            values=["0", "5", "10", "15", "20", "30"],
            font=FONT_SMALL,
            width=60,
            fg_color=("#f0f4f8", Colors.SURFACE_ALT),
            button_color=Colors.PRIMARY,
            button_hover_color=Colors.PRIMARY_HOVER,
            command=lambda v: self._debounced_live_preview(),
        )
        margin_menu.grid(row=0, column=4, padx=4)

        for i in range(2):
            adj = ctk.CTkFrame(
                settings,
                fg_color="transparent",
            )
            adj.grid(row=1 + i, column=0, columnspan=5, padx=14, pady=4, sticky="ew")
            adj.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(
                adj,
                text=tr(f"image{i+1}"),
                font=FONT_SMALL,
                text_color=Colors.PRIMARY,
            ).grid(row=0, column=0, padx=8, pady=4)

    def _build_preview(self):
        self.preview_frame = ctk.CTkFrame(
            self,
            fg_color=("#ffffff", Colors.CARD),
            corner_radius=14,
            border_width=1,
            border_color=("#dce6ef", Colors.BORDER),
        )
        self.preview_frame.grid(row=3, column=0, padx=24, pady=6, sticky="nsew")
        self.preview_frame.grid_columnconfigure(0, weight=1)
        self.preview_frame.grid_rowconfigure(0, weight=1)

        self.preview_lbl = ctk.CTkLabel(
            self.preview_frame,
            text=tr("no_images_merge"),
            font=FONT,
            text_color=("#64748b", Colors.TEXT_MUTED),
        )
        self.preview_lbl.place(relx=0.5, rely=0.5, anchor="center")
        self._preview_ctk_img = None

    def _debounced_live_preview(self):
        if self._live_preview_after:
            self.after_cancel(self._live_preview_after)
        self._live_preview_after = self.after(80, self._update_live_preview)

    def _update_live_preview(self):
        self._live_preview_after = None
        img1 = self.img1_zone.pil_image
        img2 = self.img2_zone.pil_image
        if not img1 or not img2:
            self.preview_lbl.configure(text=tr("no_images_merge"), image="")
            return

        merged = self._build_merged()
        pw = self.preview_frame.winfo_width() - 20 or 600
        ph = self.preview_frame.winfo_height() - 20 or 300
        merged.thumbnail((pw, ph), Image.LANCZOS)
        ctk_img = ctk.CTkImage(
            light_image=merged, dark_image=merged, size=(merged.width, merged.height)
        )
        self._preview_ctk_img = ctk_img
        self.preview_lbl.configure(image=ctk_img, text="")

    def _build_merged(self):
        img1 = self.img1_zone.pil_image.copy()
        img2 = self.img2_zone.pil_image.copy()
        margin = int(self.margin_var.get())

        if img1.mode in ("RGBA", "P"):
            img1 = img1.convert("RGB")
        if img2.mode in ("RGBA", "P"):
            img2 = img2.convert("RGB")

        if self.layout_var.get() == "horizontal":
            max_h = max(img1.height, img2.height)
            w1 = int(img1.width * max_h / img1.height)
            w2 = int(img2.width * max_h / img2.height)
            img1 = img1.resize((w1, max_h), Image.LANCZOS)
            img2 = img2.resize((w2, max_h), Image.LANCZOS)
            total_w = w1 + w2 + margin * 3
            total_h = max_h + margin * 2
            canvas = Image.new("RGB", (total_w, total_h), (255, 255, 255))
            canvas.paste(img1, (margin, margin))
            canvas.paste(img2, (margin * 2 + w1, margin))
        else:
            max_w = max(img1.width, img2.width)
            h1 = int(img1.height * max_w / img1.width)
            h2 = int(img2.height * max_w / img2.width)
            img1 = img1.resize((max_w, h1), Image.LANCZOS)
            img2 = img2.resize((max_w, h2), Image.LANCZOS)
            total_w = max_w + margin * 2
            total_h = h1 + h2 + margin * 3
            canvas = Image.new("RGB", (total_w, total_h), (255, 255, 255))
            canvas.paste(img1, (margin, margin))
            canvas.paste(img2, (margin, margin * 2 + h1))

        return canvas

    def _build_export(self):
        bot = ctk.CTkFrame(self, fg_color="transparent")
        bot.grid(row=4, column=0, padx=24, pady=(6, 20), sticky="ew")
        bot.grid_columnconfigure(0, weight=1)

        self.export_pdf_btn = ctk.CTkButton(
            bot,
            text=tr("export_btn") + "  " + ICONS["pdf"],
            command=self._export_pdf,
            height=44,
            font=FONT_BOLD,
            fg_color=Colors.PRIMARY,
            hover_color=Colors.PRIMARY_HOVER,
            text_color="#ffffff",
            corner_radius=22,
        )
        self.export_pdf_btn.pack(side="right", padx=4)

        self.export_img_btn = ctk.CTkButton(
            bot,
            text=tr("export_image") + "  " + ICONS["image"],
            command=self._export_image,
            height=44,
            font=FONT_BOLD,
            fg_color=Colors.SUCCESS,
            hover_color="#059669",
            text_color="#ffffff",
            corner_radius=18,
        )
        self.export_img_btn.pack(side="right", padx=4)

    def handle_drop(self, paths):
        for p in paths:
            ext = os.path.splitext(p)[1].lower()
            if ext in (".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif"):
                if not self.img1_zone.file_path:
                    self.img1_zone.load_image(p)
                    break
                elif not self.img2_zone.file_path:
                    self.img2_zone.load_image(p)
                    break

    def _export_pdf(self):
        if not self._check_images():
            return

        merged = self._build_merged()
        nd = NameDialog(
            self, title=tr("export_btn"), prompt=tr("export_name"), initial="merged"
        )
        nd.wait_window()
        name = nd.result
        if not name:
            return
        if not name.lower().endswith(".pdf"):
            name += ".pdf"

        out = filedialog.asksaveasfilename(
            title=tr("save_as"),
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")],
            initialfile=name,
        )
        if not out:
            return

        def do():
            try:
                fd, tmp = tempfile.mkstemp(suffix=".jpg")
                os.close(fd)
                merged.save(tmp, "JPEG", quality=95)
                images_to_pdf([tmp], out)
                os.remove(tmp)
                self.after(
                    0, lambda: Toast.show(self, tr("success_merge_images"), "success")
                )
            except Exception as e:
                self.after(
                    0, lambda: Toast.show(self, f"{tr('error')}: {e}", "error")
                )

        threading.Thread(target=do, daemon=True).start()

    def _export_image(self):
        if not self._check_images():
            return

        merged = self._build_merged()
        out = filedialog.asksaveasfilename(
            title=tr("save_as"),
            defaultextension=".png",
            filetypes=[
                ("PNG", "*.png"),
                ("JPEG", "*.jpg"),
                ("WebP", "*.webp"),
                ("BMP", "*.bmp"),
            ],
        )
        if not out:
            return

        def do():
            try:
                merged.save(out)
                self.after(
                    0, lambda: Toast.show(self, tr("success_merge_images"), "success")
                )
            except Exception as e:
                self.after(
                    0, lambda: Toast.show(self, f"{tr('error')}: {e}", "error")
                )

        threading.Thread(target=do, daemon=True).start()

    def _check_images(self):
        if not self.img1_zone.pil_image or not self.img2_zone.pil_image:
            Toast.show(self, tr("no_images_merge"), "warning")
            return False
        return True

    def update_language(self):
        self.header_title.configure(text=tr("merge_images"))
        self.desc_lbl.configure(text=tr("merge_images_desc"))
        self.img1_zone.update_language()
        self.img2_zone.update_language()
        self.export_pdf_btn.configure(text=tr("export_btn") + "  " + ICONS["pdf"])
        self.export_img_btn.configure(
            text=tr("export_image") + "  " + ICONS["image"]
        )
