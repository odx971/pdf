from PIL import Image
import io
import os
from reportlab.lib.pagesizes import A4, A3, letter, legal
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas as rl_canvas

PAGE_SIZE_MAP = {
    "A4": A4,
    "A3": A3,
    "Letter": letter,
    "Legal": legal,
}


def images_to_pdf(image_paths, output_path, page_size="A4", orientation="portrait", margin=10):
    if not image_paths:
        return

    if page_size != "Auto" and page_size in PAGE_SIZE_MAP:
        pw, ph = PAGE_SIZE_MAP[page_size]
        if orientation == "landscape":
            pw, ph = ph, pw
    else:
        first = Image.open(image_paths[0])
        pw, ph = first.size
        first.close()

    c = rl_canvas.Canvas(output_path, pagesize=(pw, ph))
    margin_pts = margin * 2.83465

    for img_path in image_paths:
        img = Image.open(img_path)
        if img.mode in ("RGBA", "P", "PA"):
            img = img.convert("RGB")
        img_w, img_h = img.size

        avail_w = pw - 2 * margin_pts
        avail_h = ph - 2 * margin_pts
        scale = min(avail_w / img_w, avail_h / img_h)
        draw_w = img_w * scale
        draw_h = img_h * scale
        x = (pw - draw_w) / 2
        y = (ph - draw_h) / 2

        c.drawImage(ImageReader(img), x, y, width=draw_w, height=draw_h, preserveAspectRatio=True)
        img.close()
        c.showPage()

    c.save()
