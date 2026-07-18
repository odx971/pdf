import customtkinter as ctk
from PIL import Image
import fitz
from theme import tr, ICONS, FONT, FONT_BOLD, FONT_SMALL, Colors
from utils.pdf_ops import get_page_thumbnail


class PageSelectorDialog(ctk.CTkToplevel):
    def __init__(self, parent, pdf_path):
        super().__init__(parent)
        self.pdf_path = pdf_path
        self.selected_pages = []
        self.confirmed = False

        doc = fitz.open(pdf_path)
        self.total_pages = doc.page_count
        doc.close()

        fn = pdf_path.replace("\\", "/").split("/")[-1]
        self.title(f"{tr('select_pages')} - {fn}")
        self.geometry("800x620")
        self.minsize(620, 420)
        self.transient(parent)
        self.grab_set()

        self.configure(fg_color=("#f1f5f9", Colors.BG))

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        top = ctk.CTkFrame(self, fg_color=("#ffffff", Colors.CARD), corner_radius=0,
                           border_width=1, border_color=("#dce6ef", Colors.BORDER))
        top.grid(row=0, column=0, padx=0, pady=0, sticky="ew")
        top.grid_columnconfigure(0, weight=1)

        inner_top = ctk.CTkFrame(top, fg_color="transparent")
        inner_top.grid(row=0, column=0, padx=20, pady=(16, 12), sticky="ew")
        inner_top.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(inner_top, text=f"{fn}  \u00b7  {self.total_pages} {tr('pages')}",
                      font=("Segoe UI", 15, "bold"), anchor="w",
                      text_color=("#0f172a", Colors.TEXT)).grid(row=0, column=0, sticky="w")

        btn_f = ctk.CTkFrame(inner_top, fg_color="transparent")
        btn_f.grid(row=0, column=1)

        self.sel_all_btn = ctk.CTkButton(btn_f, text=tr("select_all"), width=90, height=30,
                                           font=FONT_SMALL,
                                           fg_color="transparent",
                                           hover_color=("#f1f5f9", Colors.SURFACE_ALT),
                                           text_color=(Colors.PRIMARY, Colors.PRIMARY_LIGHT),
                                           corner_radius=18,
                                           command=self.select_all)
        self.sel_all_btn.pack(side="left", padx=3)

        self.dsel_btn = ctk.CTkButton(btn_f, text=tr("deselect_all"), width=90, height=30,
                                        font=FONT_SMALL,
                                        fg_color="transparent",
                                        hover_color=("#f1f5f9", Colors.SURFACE_ALT),
                                        text_color=("#64748b", Colors.TEXT_MUTED),
                                        corner_radius=18,
                                        command=self.deselect_all)
        self.dsel_btn.pack(side="left", padx=3)

        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.grid(row=1, column=0, padx=16, pady=8, sticky="nsew")

        self.checkboxes = []
        self.loading = ctk.CTkLabel(self.scroll, text=tr("loading"),
                                     font=FONT, text_color=("#64748b", Colors.TEXT_MUTED))
        self.loading.pack(pady=40)

        bot = ctk.CTkFrame(self, fg_color=("#ffffff", Colors.CARD), corner_radius=0,
                           border_width=1, border_color=("#dce6ef", Colors.BORDER))
        bot.grid(row=2, column=0, padx=0, pady=0, sticky="ew")
        bot.grid_columnconfigure(0, weight=1)

        inner_bot = ctk.CTkFrame(bot, fg_color="transparent")
        inner_bot.grid(row=0, column=0, padx=20, pady=(10, 14), sticky="ew")
        inner_bot.grid_columnconfigure(0, weight=1)

        self.cnt_lbl = ctk.CTkLabel(inner_bot, text=f"{self.total_pages} / {self.total_pages} {tr('pages_selected')}",
                                     font=FONT_SMALL, text_color=("#64748b", Colors.TEXT_MUTED))
        self.cnt_lbl.grid(row=0, column=0, sticky="w")

        ctk.CTkButton(inner_bot, text=tr("cancel"), width=90, height=34,
                        font=FONT,
                        fg_color="transparent",
                        hover_color=("#f1f5f9", Colors.SURFACE_ALT),
                        text_color=("#64748b", Colors.TEXT_MUTED),
                        corner_radius=20,
                        command=self.cancel).grid(row=0, column=1, padx=4)

        ctk.CTkButton(inner_bot, text=tr("confirm"), width=110, height=34,
                        font=FONT_BOLD,
                        fg_color=Colors.PRIMARY,
                        hover_color=Colors.PRIMARY_HOVER,
                        corner_radius=20,
                        command=self.confirm_selection).grid(row=0, column=2, padx=4)

        self.after(100, self.load_thumbnails)

    def load_thumbnails(self):
        self.loading.destroy()
        max_w = self.scroll.winfo_width() - 28
        cols = max(2, min(5, max_w // 150))
        for i in range(cols):
            self.scroll.grid_columnconfigure(i, weight=1, uniform="pg")

        doc = fitz.open(self.pdf_path)
        for i in range(self.total_pages):
            r = i // cols
            c = i % cols

            card = ctk.CTkFrame(self.scroll, fg_color=("#ffffff", Colors.CARD),
                                 corner_radius=10, height=185,
                                 border_width=1, border_color=("#dce6ef", Colors.BORDER))
            card.grid(row=r, column=c, padx=4, pady=4, sticky="nsew")
            card.grid_propagate(False)
            card.grid_columnconfigure(0, weight=1)

            var = ctk.BooleanVar(value=True)
            cb = ctk.CTkCheckBox(card, text=f"{tr('page')} {i+1}", variable=var,
                                  font=FONT_SMALL,
                                  fg_color=Colors.PRIMARY,
                                  hover_color=Colors.PRIMARY_HOVER,
                                  text_color=("#0f172a", Colors.TEXT),
                                  command=lambda v=var: self.update_count())
            cb.grid(row=0, column=0, padx=8, pady=(6, 0), sticky="w")
            self.checkboxes.append(var)

            img_lbl = ctk.CTkLabel(card, text="", width=120, height=140)
            img_lbl.grid(row=1, column=0, padx=4, pady=(0, 4))

            try:
                img = get_page_thumbnail(self.pdf_path, i)
                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(img.width, img.height))
                img_lbl.configure(image=ctk_img, text="")
            except:
                img_lbl.configure(text=f"{tr('page')} {i+1}")
        doc.close()

    def update_count(self):
        c = sum(1 for cb in self.checkboxes if cb.get())
        self.cnt_lbl.configure(text=f"{c} / {self.total_pages} {tr('pages_selected')}")

    def select_all(self):
        for cb in self.checkboxes:
            cb.set(True)
        self.update_count()

    def deselect_all(self):
        for cb in self.checkboxes:
            cb.set(False)
        self.update_count()

    def confirm_selection(self):
        self.selected_pages = [i for i, cb in enumerate(self.checkboxes) if cb.get()]
        self.confirmed = True
        self.destroy()

    def cancel(self):
        self.confirmed = False
        self.destroy()

    def get_result(self):
        if self.confirmed:
            return self.selected_pages
        return None
