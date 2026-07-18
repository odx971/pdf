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


def enhance_image(img, brightness=1.0, contrast=1.0, sharpness=1.0, upscale=1):
    if brightness != 1.0:
        img = ImageEnhance.Brightness(img).enhance(brightness)
    if contrast != 1.0:
        img = ImageEnhance.Contrast(img).enhance(contrast)
    if sharpness != 1.0:
        img = ImageEnhance.Sharpness(img).enhance(sharpness)
    if upscale > 1:
        w, h = img.size
        img = img.resize((w * upscale, h * upscale), Image.LANCZOS)
    return img


class CarDropZone(ctk.CTkFrame):
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
        ctk.CTkLabel(self.ph, text=ICONS["image"], font=("Segoe UI", 36),
                      text_color=Colors.PRIMARY_LIGHT).pack()
        self.ph_text = ctk.CTkLabel(
            self.ph, text=tr("drop_car"),
            font=FONT_SMALL,
            text_color=("#64748b", Colors.TEXT_MUTED)
        )
        self.ph_text.pack()

        self.img_lbl = ctk.CTkLabel(self.drop_area, text="")

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(fill="x", padx=12, pady=(6, 14))

        ctk.CTkButton(
            btn_row, text=f"{ICONS['folder']} {tr('browse')}",
            command=self._browse,
            height=30, font=FONT_SMALL,
            fg_color="transparent",
            hover_color=("#f1f5f9", Colors.SURFACE_ALT),
            text_color=Colors.PRIMARY,
            border_width=1, border_color=Colors.PRIMARY,
            corner_radius=18
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            btn_row, text=f"{ICONS['trash']} {tr('clear_all')}",
            command=self._clear,
            height=30, font=FONT_SMALL,
            fg_color="transparent",
            hover_color=("#fef2f2", "#2d1015"),
            text_color=("#ef4444", "#f87171"),
            corner_radius=18
        ).pack(side="right", padx=2)

    def _browse(self):
        path = filedialog.askopenfilename(
            title=tr(self.title_key),
            filetypes=[("Images", "*.jpg *.jpeg *.png *.webp *.bmp *.gif")]
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
            thumb.thumbnail((260, 180), Image.LANCZOS)
            ctk_img = ctk.CTkImage(light_image=thumb, dark_image=thumb,
                                    size=(thumb.width, thumb.height))
            self.img_lbl.configure(image=ctk_img)
            self.ph.place_forget()
            self.img_lbl.place(relx=0.5, rely=0.5, anchor="center")

            if self.on_load:
                self.on_load(path)
        except Exception:
            pass

    def update_language(self):
        self.title_lbl.configure(text=tr(self.title_key))
        self.ph_text.configure(text=tr("drop_car"))


class CarTab(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.app_ref = None
        self.configure(fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._live_preview_after = None

        self._build_header()
        self._build_drop_zones()
        self._build_enhancement()
        self._build_export()

    def _build_header(self):
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.grid(row=0, column=0, padx=28, pady=(28, 4), sticky="ew")

        row = ctk.CTkFrame(hdr, fg_color="transparent")
        row.pack(anchor="w")

        ctk.CTkLabel(row, text=ICONS["car"], font=("Segoe UI", 28),
                     text_color=Colors.PRIMARY).pack(side="left")
        self.header_title = ctk.CTkLabel(row, text=tr("car"), font=FONT_LARGE,
                                         text_color=("#0f172a", Colors.TEXT))
        self.header_title.pack(side="left", padx=(10, 0))

        self.desc_lbl = ctk.CTkLabel(hdr, text=tr("car_desc"), font=("Segoe UI", 12),
                                     text_color=("#64748b", Colors.TEXT_MUTED), anchor="w")
        self.desc_lbl.pack(anchor="w", padx=(38, 0), pady=(2, 0))

        accent = ctk.CTkFrame(hdr, height=3, fg_color=Colors.PRIMARY, corner_radius=2)
        accent.pack(fill="x", padx=0, pady=(10, 0))

    def _build_drop_zones(self):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.grid(row=1, column=0, padx=24, pady=8, sticky="nsew")
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=1)
        container.grid_rowconfigure(0, weight=1)

        self.front_zone = CarDropZone(container, "car_front", on_load=lambda p: self._on_zone_loaded("front", p))
        self.front_zone.grid(row=0, column=0, padx=(0, 8), pady=4, sticky="nsew")

        self.back_zone = CarDropZone(container, "car_back", on_load=lambda p: self._on_zone_loaded("back", p))
        self.back_zone.grid(row=0, column=1, padx=(8, 0), pady=4, sticky="nsew")

    def _on_zone_loaded(self, zone, path):
        self._update_live_preview()

    def _get_preview_source(self):
        img = self.front_zone.pil_image or self.back_zone.pil_image
        return img

    def _build_enhancement(self):
        self.enhance_frame = ctk.CTkFrame(
            self, fg_color=("#ffffff", Colors.CARD), corner_radius=14,
            border_width=1, border_color=("#dce6ef", Colors.BORDER)
        )
        self.enhance_frame.grid(row=2, column=0, padx=24, pady=6, sticky="ew")
        self.enhance_frame.grid_columnconfigure(0, weight=1)

        self.enhance_title = ctk.CTkLabel(
            self.enhance_frame, text=f"{ICONS['settings']} {tr('enhancement')}",
            font=FONT_BOLD,
            text_color=("#0f172a", Colors.TEXT)
        )
        self.enhance_title.grid(row=0, column=0, padx=16, pady=(14, 4), sticky="w")

        self.enhance_sw = ctk.CTkSwitch(
            self.enhance_frame, text=tr("enable_enhance"),
            command=self._toggle_enhance,
            progress_color=Colors.PRIMARY,
            button_color=Colors.PRIMARY,
            font=FONT_SMALL
        )
        self.enhance_sw.grid(row=0, column=1, padx=16, pady=(14, 4), sticky="e")
        self.enhance_sw.select()

        self.live_preview_frame = ctk.CTkFrame(
            self.enhance_frame,
            fg_color="transparent",
            corner_radius=12, height=160,
            border_width=1, border_color=("#5eead4", Colors.BORDER)
        )
        self.live_preview_frame.grid(row=1, column=0, columnspan=2, padx=16, pady=(4, 4), sticky="ew")
        self.live_preview_frame.grid_propagate(False)

        self.live_preview_lbl = ctk.CTkLabel(
            self.live_preview_frame, text="",
            font=FONT_SMALL,
            text_color=("#64748b", Colors.TEXT_MUTED)
        )
        self.live_preview_lbl.place(relx=0.5, rely=0.5, anchor="center")
        self._live_ctk_img = None

        self.enhance_body = ctk.CTkFrame(self.enhance_frame, fg_color="transparent")
        self.enhance_body.grid(row=2, column=0, columnspan=2, padx=16, pady=(2, 10), sticky="ew")
        self.enhance_body.grid_columnconfigure(1, weight=1)

        self.slider_labels = {}
        self.sliders = {}
        for i, key in enumerate(["brightness", "contrast", "sharpness"]):
            lbl = ctk.CTkLabel(
                self.enhance_body, text=tr(key),
                font=FONT_SMALL, width=80,
                text_color=("#0f172a", Colors.TEXT)
            )
            lbl.grid(row=i, column=0, padx=(0, 8), pady=4, sticky="w")
            self.slider_labels[key] = lbl
            var = ctk.DoubleVar(value=1.0)
            sl = ctk.CTkSlider(
                self.enhance_body,
                from_=0.0, to=2.0 if key != "sharpness" else 3.0,
                variable=var, number_of_steps=100,
                progress_color=Colors.PRIMARY,
                button_color=Colors.PRIMARY,
                button_hover_color=Colors.PRIMARY_HOVER
            )
            sl.grid(row=i, column=1, padx=4, pady=4, sticky="ew")
            val = ctk.CTkLabel(
                self.enhance_body, text="1.00",
                font=FONT_SMALL, width=40,
                text_color=("#64748b", Colors.TEXT_MUTED)
            )
            val.grid(row=i, column=2, padx=(4, 0), pady=4)
            sl.configure(command=lambda v, k=key, l=val: (l.configure(text=f"{v:.2f}"),
                                                           self._debounced_live_preview()))
            self.sliders[key] = (sl, val, var)

        self.upscale_lbl = ctk.CTkLabel(
            self.enhance_body, text=tr("upscale"),
            font=FONT_SMALL, width=80,
            text_color=("#0f172a", Colors.TEXT)
        )
        self.upscale_lbl.grid(row=3, column=0, padx=(0, 8), pady=4, sticky="w")

        self.upscale_var = ctk.IntVar(value=1)
        rb_frame = ctk.CTkFrame(self.enhance_body, fg_color="transparent")
        rb_frame.grid(row=3, column=1, columnspan=2, padx=4, pady=4, sticky="w")
        self.upscale_rbs = []
        for val, lbl_key in [(1, "upscale_off"), (2, "\u00d72"), (3, "\u00d73")]:
            rb = ctk.CTkRadioButton(
                rb_frame, text=lbl_key, variable=self.upscale_var, value=val,
                font=FONT_SMALL,
                fg_color=Colors.PRIMARY,
                hover_color=Colors.PRIMARY_HOVER,
                text_color=("#0f172a", Colors.TEXT),
                command=self._debounced_live_preview
            )
            rb.pack(side="left", padx=8)
            self.upscale_rbs.append(rb)

        self.preview_btn = ctk.CTkButton(
            self.enhance_body,
            text=f"{ICONS['eye']} {tr('preview')}",
            command=self._preview, height=30,
            font=FONT_SMALL,
            fg_color="transparent",
            hover_color=("#f1f5f9", Colors.SURFACE_ALT),
            text_color=("#64748b", Colors.TEXT_MUTED),
            corner_radius=18
        )
        self.preview_btn.grid(row=4, column=0, columnspan=3, pady=(8, 0))

    def _toggle_enhance(self):
        state = "normal" if self.enhance_sw.get() else "disabled"
        for child in self.enhance_body.winfo_children():
            try:
                child.configure(state=state)
            except:
                pass
        self.preview_btn.configure(state="normal")
        self._update_live_preview()

    def _debounced_live_preview(self):
        if self._live_preview_after:
            self.after_cancel(self._live_preview_after)
        self._live_preview_after = self.after(80, self._update_live_preview)

    def _update_live_preview(self):
        self._live_preview_after = None
        src = self._get_preview_source()
        if not src:
            self.live_preview_lbl.configure(text=tr("no_images_car"), image="")
            return

        params = self._get_enhance_params()
        preview = enhance_image(src.copy(), brightness=params["brightness"],
                                 contrast=params["contrast"], sharpness=params["sharpness"],
                                 upscale=1)
        pw, ph = self.live_preview_frame.winfo_width(), self.live_preview_frame.winfo_height()
        if pw < 50:
            pw = 400
            ph = 160
        preview.thumbnail((pw - 20, ph - 16), Image.LANCZOS)
        ctk_img = ctk.CTkImage(light_image=preview, dark_image=preview,
                                size=(preview.width, preview.height))
        self._live_ctk_img = ctk_img
        self.live_preview_lbl.configure(image=ctk_img, text="")

    def _build_export(self):
        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.grid(row=3, column=0, padx=24, pady=(10, 24), sticky="ew")

        self.status_lbl = ctk.CTkLabel(
            bottom, text="",
            font=FONT_SMALL,
            text_color=Colors.SUCCESS
        )
        self.status_lbl.pack(pady=(0, 6))

        self.export_btn = ctk.CTkButton(
            bottom,
            text=f"{ICONS['arrow_right']} {tr('export_btn')}",
            command=self._export_pdf, height=44,
            font=FONT_BOLD,
            fg_color=Colors.PRIMARY,
            hover_color=Colors.PRIMARY_HOVER,
            text_color="#ffffff",
            corner_radius=22
        )
        self.export_btn.pack(fill="x", ipady=2)

    def handle_drop(self, paths):
        if not paths:
            return
        for p in paths:
            ext = os.path.splitext(p)[1].lower()
            if ext in (".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif"):
                if not self.front_zone.file_path:
                    self.front_zone.load_image(p)
                    break
                elif not self.back_zone.file_path:
                    self.back_zone.load_image(p)
                    break

    def _get_enhance_params(self):
        if not self.enhance_sw.get():
            return {"brightness": 1.0, "contrast": 1.0, "sharpness": 1.0, "upscale": 1}
        return {
            "brightness": self.sliders["brightness"][2].get(),
            "contrast": self.sliders["contrast"][2].get(),
            "sharpness": self.sliders["sharpness"][2].get(),
            "upscale": self.upscale_var.get(),
        }

    def _preview(self):
        src = self._get_preview_source()
        if not src:
            if self.app_ref:
                Toast(self.app_ref, tr("no_images_car"), "warning")
            return

        side = "front" if self.front_zone.pil_image else "back"
        params = self._get_enhance_params()
        enhanced = enhance_image(src.copy(), **params)

        pw = ctk.CTkToplevel(self)
        pw.title(f"{tr('preview')} - {side}")
        pw.geometry("700x600")
        pw.minsize(400, 400)
        pw.transient(self.winfo_toplevel())

        w, h = enhanced.size
        max_sz = 680, 560
        scale = min(max_sz[0] / w, max_sz[1] / h)
        display = enhanced.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
        ctk_img = ctk.CTkImage(light_image=display, dark_image=display,
                                size=(display.width, display.height))

        ctk.CTkLabel(pw, text="", image=ctk_img).pack(expand=True, fill="both", padx=10, pady=10)

        pw.grab_set()

    def _export_pdf(self):
        front_img = self.front_zone.pil_image
        back_img = self.back_zone.pil_image

        if not front_img or not back_img:
            if self.app_ref:
                Toast(self.app_ref, tr("no_images_car"), "warning")
            return

        params = self._get_enhance_params()

        nd = NameDialog(self, title=tr("export_btn"), prompt=tr("export_name"),
                         initial=tr("car_doc_pdf"))
        nd.wait_window()
        name = nd.result
        if not name:
            return
        if not name.lower().endswith(".pdf"):
            name += ".pdf"

        out = filedialog.asksaveasfilename(title=tr("save_as"), defaultextension=".pdf",
                                            filetypes=[("PDF files", "*.pdf")], initialfile=name)
        if not out:
            return

        def do_export(output_path):
            temp_files = []
            try:
                for img in (front_img, back_img):
                    enhanced = enhance_image(img.copy(), **params)
                    if enhanced.mode in ("RGBA", "P"):
                        enhanced = enhanced.convert("RGB")
                    fd, path = tempfile.mkstemp(suffix=".jpg")
                    os.close(fd)
                    enhanced.save(path, "JPEG", quality=95)
                    temp_files.append(path)

                images_to_pdf(temp_files, output_path, page_size="A4", margin=15)

                if self.app_ref:
                    Toast(self.app_ref, tr("success_car"), "success")
                self.status_lbl.configure(text=f"{ICONS['check']} {output_path}")
            except Exception as e:
                if self.app_ref:
                    Toast(self.app_ref, f"{tr('error')}: {e}", "error")
            finally:
                for tf in temp_files:
                    try:
                        os.remove(tf)
                    except:
                        pass

        threading.Thread(target=do_export, args=(out,), daemon=True).start()

    def update_language(self):
        self.header_title.configure(text=tr("car"))
        self.desc_lbl.configure(text=tr("car_desc"))
        self.front_zone.update_language()
        self.back_zone.update_language()
        self.enhance_title.configure(text=f"{ICONS['settings']} {tr('enhancement')}")
        self.enhance_sw.configure(text=tr("enable_enhance"))
        for key, lbl in self.slider_labels.items():
            lbl.configure(text=tr(key))
        self.upscale_lbl.configure(text=tr("upscale"))
        for i, rb in enumerate(self.upscale_rbs):
            texts = [tr("upscale_off"), "\u00d72", "\u00d73"]
            if i < len(texts):
                rb.configure(text=texts[i])
        self.preview_btn.configure(text=f"{ICONS['eye']} {tr('preview')}")
        self.export_btn.configure(text=f"{ICONS['arrow_right']} {tr('export_btn')}")
