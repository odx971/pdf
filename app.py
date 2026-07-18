import customtkinter as ctk
import tkinterdnd2
import tkinter as tk
import os
import sys
from PIL import Image
from theme import tr, Colors, ICONS, FONT, FONT_BOLD, FONT_SMALL, FONT_LARGE
from tabs.merge_tab import MergeTab
from tabs.split_tab import SplitTab
from tabs.car_tab import CarTab
from tabs.convert_tab import ConvertTab
from tabs.merge_images_tab import MergeImagesTab
from tabs.unlock_tab import UnlockTab
from widgets.toast import Toast


class SplashScreen(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.configure(fg_color="#0a0a0a")

        w, h = 460, 480
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

        main = ctk.CTkFrame(self, fg_color="#0a0a0a", corner_radius=0)
        main.pack(expand=True, fill="both", padx=40, pady=50)

        logo_canvas = tk.Canvas(main, width=110, height=110,
                                bg="#0a0a0a", highlightthickness=0)
        logo_canvas.pack(anchor="center", pady=(0, 0))

        r = 26
        for i in range(12):
            offset = i
            alpha_hex = format(max(0, 60 - i * 8), '02x')
            color = f"#{alpha_hex}0000"
            logo_canvas.create_oval(
                55 - 55 - offset, 55 - 55 - offset,
                55 + 55 + offset, 55 + 55 + offset,
                fill="", outline=color, width=2
            )

        self._draw_rounded_rect(logo_canvas, 0, 0, 110, 110, r, "#ff0000")
        self._draw_rounded_rect(logo_canvas, 1, 1, 109, 56, r, "#ff3333")
        self._draw_rounded_rect(logo_canvas, 1, 56, 109, 109, r, "#cc0000")
        self._draw_rounded_rect(logo_canvas, 0, 0, 110, 110, r, "", outline="")

        logo_canvas.create_text(55, 55, text="pdftool",
                                font=("Segoe UI", 18, "bold"),
                                fill="#ffffff")

        ctk.CTkLabel(main, text="PDF Toolbox",
                      font=("Segoe UI", 26, "bold"),
                      text_color="#ffffff").pack(anchor="center", pady=(20, 6))

        ctk.CTkLabel(main, text="Merge, Split, Convert & More",
                      font=("Segoe UI", 13),
                      text_color="#888888").pack(anchor="center", pady=(0, 4))

        ctk.CTkLabel(main, text="by odx",
                      font=("Segoe UI", 11),
                      text_color="#888888").pack(anchor="center", pady=(0, 0))

        bar_frame = ctk.CTkFrame(main, fg_color="#333333", height=3,
                                  corner_radius=2)
        bar_frame.pack(fill="x", padx=60, pady=(28, 0))
        bar_frame.pack_propagate(False)

        self._bar = ctk.CTkFrame(bar_frame, fg_color="#ff0000", height=3,
                                  corner_radius=2)
        self._bar.place(relx=0.0, rely=0.5, anchor="w", relwidth=0.35, relheight=1.0)
        self._bar_x = 0.0
        self._animate_bar()

    def _draw_rounded_rect(self, canvas, x1, y1, x2, y2, r, fill, outline=""):
        points = [
            x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
            x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
            x1, y2, x1, y2 - r, x1, y1 + r, x1, y1
        ]
        canvas.create_polygon(points, fill=fill, outline=outline, smooth=True)

    def _animate_bar(self):
        try:
            self._bar_x += 0.008
            if self._bar_x > 1.35:
                self._bar_x = -0.35
            self._bar.place(relx=self._bar_x, rely=0.5, anchor="w",
                            relwidth=0.35, relheight=1.0)
            self.after(16, self._animate_bar)
        except:
            pass


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.withdraw()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("PDF Toolbox")
        self.geometry("900x780")
        self.minsize(700, 640)

        self.configure(fg_color=("#F5F5F5", Colors.BG))

        ico = os.path.join(os.path.dirname(__file__), "app_icon.ico")
        if os.path.exists(ico):
            try:
                self.iconbitmap(ico)
            except:
                pass

        self._splash = SplashScreen(self)
        self.after(2200, self._build_main)

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def _build_main(self):
        try:
            self._splash.destroy()
        except:
            pass
        self._splash = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_header()
        self._build_content()
        self._build_bottom_nav()

        self.tabs = {
            "merge": MergeTab(self.content_frame),
            "split": SplitTab(self.content_frame),
            "car": CarTab(self.content_frame),
            "convert": ConvertTab(self.content_frame),
            "merge_images": MergeImagesTab(self.content_frame),
            "unlock": UnlockTab(self.content_frame),
        }

        for t in self.tabs.values():
            t.app_ref = self

        self.current_tab = None
        self.switch_tab("merge")
        self._setup_dnd()

        self.deiconify()

    def _build_header(self):
        hdr = ctk.CTkFrame(self, height=52, corner_radius=0,
                           fg_color=("#ffffff", Colors.SURFACE))
        hdr.grid(row=0, column=0, sticky="ew")
        hdr.grid_columnconfigure(0, weight=1)
        hdr.grid_propagate(False)

        ctk.CTkLabel(hdr, text="PDF Toolbox", font=("Segoe UI", 18, "bold"),
                      text_color=("#0f172a", Colors.TEXT)).pack(side="left", padx=20)

        actions = ctk.CTkFrame(hdr, fg_color="transparent")
        actions.pack(side="right", padx=12)

        self.reset_btn = ctk.CTkButton(actions, text=ICONS["reset"], width=36, height=36,
                                        font=("Segoe UI", 18),
                                        fg_color="transparent",
                                        hover_color=("#f0f0f0", Colors.SURFACE_ALT),
                                        text_color=("#64748b", Colors.TEXT_MUTED),
                                        corner_radius=10,
                                        command=self._reset_all)
        self.reset_btn.pack(side="right", padx=4)

        self.theme_sw = ctk.CTkSwitch(actions, text="", width=40, height=22,
                                       command=self.toggle_theme,
                                       progress_color=Colors.PRIMARY,
                                       button_color=Colors.PRIMARY,
                                       button_hover_color=Colors.PRIMARY_HOVER)
        self.theme_sw.pack(side="right", padx=4)
        self.theme_sw.select()

    def _build_content(self):
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self.content_frame.grid(row=1, column=0, sticky="nsew")
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

    def _build_bottom_nav(self):
        nav = ctk.CTkFrame(self, height=72, corner_radius=0,
                           fg_color=("#ffffff", Colors.SURFACE))
        nav.grid(row=2, column=0, sticky="ew")
        nav.grid_columnconfigure(tuple(range(6)), weight=1, uniform="nav")
        nav.grid_propagate(False)

        top_line = ctk.CTkFrame(nav, height=1, corner_radius=0,
                                fg_color=("#e0e0e0", Colors.BORDER))
        top_line.grid(row=0, column=0, columnspan=6, sticky="ew")

        self.nav_btns = {}
        items = [
            ("merge", ICONS["merge"], tr("merge")),
            ("split", ICONS["split"], tr("split")),
            ("car", ICONS["car"], tr("car")),
            ("convert", ICONS["convert"], tr("convert")),
            ("merge_images", ICONS["merge_images"], tr("merge_images")),
            ("unlock", ICONS["unlock"], tr("unlock")),
        ]

        for i, (key, icon, text) in enumerate(items):
            btn = ctk.CTkFrame(nav, fg_color="transparent", corner_radius=12)
            btn.grid(row=1, column=i, sticky="nsew", padx=3, pady=(4, 6))
            btn.grid_propagate(False)
            btn.bind("<Button-1>", lambda e, k=key: self.switch_tab(k))

            icon_lbl = ctk.CTkLabel(btn, text=icon, font=("Segoe UI", 20),
                                     text_color=("#94a3b8", Colors.TEXT_MUTED))
            icon_lbl.pack(anchor="center", pady=(4, 0))
            icon_lbl.bind("<Button-1>", lambda e, k=key: self.switch_tab(k))

            lbl = ctk.CTkLabel(btn, text=text, font=("Segoe UI", 9),
                                text_color=("#94a3b8", Colors.TEXT_MUTED))
            lbl.pack(anchor="center")
            lbl.bind("<Button-1>", lambda e, k=key: self.switch_tab(k))

            self.nav_btns[key] = (btn, icon_lbl, lbl)

    def switch_tab(self, key):
        if self.current_tab == key:
            return

        for k, (frame, icon_lbl, lbl) in self.nav_btns.items():
            if k == key:
                frame.configure(fg_color="#ff0000", corner_radius=12)
                icon_lbl.configure(text_color="#ffffff")
                lbl.configure(text_color="#ffffff")
            else:
                frame.configure(fg_color="transparent", corner_radius=12)
                icon_lbl.configure(text_color=("#888888", Colors.TEXT_MUTED))
                lbl.configure(text_color=("#888888", Colors.TEXT_MUTED))

        for k, t in self.tabs.items():
            if k == key:
                t.grid(row=0, column=0, sticky="nsew")
                t.lift()
            else:
                t.grid_remove()

        self.current_tab = key

    def toggle_theme(self):
        cur = ctk.get_appearance_mode()
        new = "Light" if cur == "Dark" else "Dark"
        ctk.set_appearance_mode(new)

    def _reset_all(self):
        for t in self.tabs.values():
            if hasattr(t, "clear_all"):
                t.clear_all()
            elif hasattr(t, "_clear"):
                t._clear()

    def _setup_dnd(self):
        try:
            tkinterdnd2.TkinterDnD._require(self)
            self.tk.call('tkdnd::drop_target', 'register', self._w, tkinterdnd2.DND_FILES)
            subst = '%A %a %b %C %c {%CST} {%CTT} %D %e {%L} {%m} {%ST} %T {%t} {%TT} %W %X %Y'
            drop_id = self._register(self._on_drop_raw)
            self.tk.call('bind', self._w, '<<Drop>>', f'{drop_id} {subst}')
        except Exception as e:
            print(f"DnD init error: {e}")

    def _on_drop_raw(self, *args):
        raw = args[7] if len(args) >= 8 else ""
        paths = []
        if raw:
            try:
                items = self.tk.splitlist(raw)
                paths = [str(p) for p in items]
            except:
                paths = [str(raw)]
        self._process_dropped_files(paths)
        return "COPY"

    def _process_dropped_files(self, paths):
        if not paths:
            return
        active = getattr(self, "current_tab", "merge")
        tab = self.tabs.get(active)
        if active == "merge" and hasattr(tab, "handle_drop"):
            tab.handle_drop(paths)
        elif active == "split" and hasattr(tab, "handle_drop"):
            pdfs = [p for p in paths if p.lower().endswith(".pdf")]
            if pdfs:
                tab.handle_drop(pdfs)
        elif active == "car" and hasattr(tab, "handle_drop"):
            imgs = [p for p in paths if any(p.lower().endswith(ext) for ext in (".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif"))]
            if imgs:
                tab.handle_drop(imgs)
        elif active == "convert" and hasattr(tab, "handle_drop"):
            pdfs = [p for p in paths if p.lower().endswith(".pdf")]
            if pdfs:
                tab.handle_drop(pdfs)
        elif active == "merge_images" and hasattr(tab, "handle_drop"):
            imgs = [p for p in paths if any(p.lower().endswith(ext) for ext in (".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif"))]
            if imgs:
                tab.handle_drop(imgs)
        elif active == "unlock" and hasattr(tab, "handle_drop"):
            pdfs = [p for p in paths if p.lower().endswith(".pdf")]
            if pdfs:
                tab.handle_drop(pdfs)
        else:
            pdfs = [p for p in paths if p.lower().endswith(".pdf")]
            if pdfs:
                self.tabs["merge"].handle_drop(pdfs)

    def on_close(self):
        self.quit()
        self.destroy()


if __name__ == "__main__":
    app = App()
    app.mainloop()
