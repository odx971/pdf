import fitz
from PIL import Image
import io
import os


def merge_pdfs(file_paths, page_selections, output_path):
    doc = fitz.open()
    for i, path in enumerate(file_paths):
        src = fitz.open(path)
        pages = page_selections[i] if (page_selections and i < len(page_selections) and page_selections[i]) else list(range(src.page_count))
        for p in pages:
            doc.insert_pdf(src, from_page=p, to_page=p)
        src.close()
    doc.save(output_path, deflate=True, garbage=3)
    doc.close()


def extract_pages_single(pdf_path, page_numbers, output_path):
    doc = fitz.open(pdf_path)
    new_doc = fitz.open()
    for p in page_numbers:
        new_doc.insert_pdf(doc, from_page=p, to_page=p)
    new_doc.save(output_path, deflate=True, garbage=3)
    new_doc.close()
    doc.close()


def extract_pages_multiple(pdf_path, page_numbers, output_dir, base_name):
    doc = fitz.open(pdf_path)
    paths = []
    for p in page_numbers:
        new_doc = fitz.open()
        new_doc.insert_pdf(doc, from_page=p, to_page=p)
        out_path = os.path.join(output_dir, f"{base_name}_page_{p+1}.pdf")
        new_doc.save(out_path, deflate=True, garbage=3)
        new_doc.close()
        paths.append(out_path)
    doc.close()
    return paths


def get_page_count(pdf_path):
    doc = fitz.open(pdf_path)
    count = doc.page_count
    doc.close()
    return count


def get_page_thumbnail(pdf_path, page_num, max_size=(160, 220)):
    doc = fitz.open(pdf_path)
    page = doc[page_num]
    mat = fitz.Matrix(0.4, 0.4)
    pix = page.get_pixmap(matrix=mat)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    img.thumbnail(max_size, Image.LANCZOS)
    doc.close()
    return img


def get_all_page_thumbnails(pdf_path, max_size=(160, 220)):
    doc = fitz.open(pdf_path)
    thumbnails = []
    for i in range(doc.page_count):
        page = doc[i]
        mat = fitz.Matrix(0.4, 0.4)
        pix = page.get_pixmap(matrix=mat)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        img.thumbnail(max_size, Image.LANCZOS)
        thumbnails.append(img)
    doc.close()
    return thumbnails


def unlock_pdf(pdf_path, password, output_path):
    doc = fitz.open(pdf_path)
    if not doc.is_encrypted:
        doc.save(output_path, garbage=3, deflate=True)
        doc.close()
        return True, "not_encrypted"
    result = doc.authenticate(password)
    if result == 0:
        doc.close()
        return False, "wrong_password"
    doc.save(output_path, garbage=3, deflate=True)
    doc.close()
    return True, "success"


def is_pdf_encrypted(pdf_path):
    doc = fitz.open(pdf_path)
    encrypted = doc.is_encrypted
    doc.close()
    return encrypted
