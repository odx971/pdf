import customtkinter as ctk

LANGUAGES = {
    "ar": {
        "app_title": "PDF Toolbox",
        "merge": "دمج PDF",
        "merge_desc": "ادمج عدة ملفات PDF في ملف واحد",
        "split": "فك الدمج",
        "split_desc": "استخرج صفحات محددة من ملف PDF",
        "dark_mode": "داكن",
        "light_mode": "فاتح",
        "drop_here": "أسقط الملفات هنا",
        "drop_pdf": "أسقط ملفات PDF هنا",
        "drop_images": "أسقط الصور هنا",
        "browse": "تصفح",
        "browse_pdf": "اختر ملف PDF",
        "browse_images": "اختر صور",
        "clear_all": "حذف الكل",
        "file": "ملف",
        "files": "ملفات",
        "page": "صفحة",
        "pages": "صفحات",
        "select_pages": "اختيار الصفحات",
        "select_all": "اختيار الكل",
        "deselect_all": "إلغاء الكل",
        "confirm": "تأكيد",
        "cancel": "إلغاء",
        "delete": "حذف",
        "merge_btn": "دمج PDF",
        "split_btn": "فك الدمج",
        "extract_btn": "استخراج الصفحات",
        "export_btn": "تصدير PDF",
        "save_as": "حفظ باسم",
        "file_name": "اسم الملف",
        "pdf_name_hint": "أدخل اسم الملف",
        "processing": "جاري المعالجة...",
        "success": "تم بنجاح!",
        "success_merge": "تم دمج الملفات بنجاح",
        "success_extract": "تم استخراج الصفحات بنجاح",
        "success_export": "تم تصدير PDF بنجاح",
        "error": "خطأ",
        "no_files": "لم تقم بإضافة أي ملفات",
        "no_images": "لم تقم بإضافة أي صور",
        "no_pdf": "لم تختر أي صفحات لاستخراجها",
        "file_added": "تمت إضافة الملف",
        "page_count": "عدد الصفحات",
        "size": "الحجم",
        "page_size": "حجم الصفحة",
        "orientation": "الاتجاه",
        "portrait": "عمودي",
        "landscape": "أفقي",
        "margin": "الهامش",
        "output_type": "نوع الإخراج",
        "single_file": "ملف واحد",
        "separate_files": "ملف لكل صفحة",
        "output_folder": "مجلد الإخراج",
        "select_folder": "اختر مجلد",
        "up": "أعلى",
        "down": "أسفل",
        "all_pages": "كل الصفحات",
        "selected_pages": "صفحات محددة",
        "settings": "الإعدادات",
        "extract": "استخراج",
        "sort": "ترتيب",
        "loading": "جاري التحميل...",
        "mm": "مم",
        "auto": "تلقائي",
        "image_settings": "إعدادات الصفحة",
        "export_name": "اكتب اسم الملف للتصدير:",
        "yes": "نعم",
        "no": "لا",
        "confirm_overwrite": "الملف موجود مسبقاً. هل تريد استبداله؟",
        "ready": "جاهز",
        "or_browse": "أو اختر من الجهاز",
        "supported_images": "الصيغ المدعومة: JPG, PNG, WebP, BMP, GIF",
        "pages_selected": "صفحة محددة",
        "drag_active": "اترك الملف للإفلات",
        "car": "ملكية السيارة",
        "car_desc": "حوّل صور ملكية السيارة (أمامي + خلفي) إلى PDF مع تحسين الجودة",
        "car_front": "الصورة الأمامية",
        "car_back": "الصورة الخلفية",
        "drop_car": "أسقط صورة الملكية هنا",
        "enhancement": "تحسين الصورة",
        "enable_enhance": "تفعيل التحسين",
        "brightness": "السطوع",
        "contrast": "التباين",
        "sharpness": "الحدة",
        "upscale": "رفع الدقة",
        "upscale_off": "بدون",
        "preview": "معاينة",
        "no_images_car": "يرجى إضافة صورتي الملكية (أمامي + خلفي)",
        "success_car": "تم إنشاء PDF بنجاح",
        "car_doc_pdf": "ملكية السيارة",
        "convert": "تحويل",
        "convert_desc": "حوّل PDF إلى صور والعكس",
        "pdf_to_images": "PDF إلى صور",
        "images_to_pdf": "صور إلى PDF",
        "output_format": "صيغة الإخراج",
        "quality": "الجودة",
        "success_convert": "تم التحويل بنجاح",
        "no_pdf_selected": "لم تختر ملف PDF",
        "merge_images": "دمج الصور",
        "merge_images_desc": "ادمج صورتين في صفحة واحدة",
        "layout": "الترتيب",
        "horizontal": "أفقي",
        "vertical": "عمودي",
        "image1": "الصورة الأولى",
        "image2": "الصورة الثانية",
        "export_image": "تصدير كصورة",
        "success_merge_images": "تم دمج الصور بنجاح",
        "no_images_merge": "يرجى إضافة الصورتين",
        "drop_image": "أسقط الصورة هنا",
        "unlock": "إزالة كلمة المرور",
        "unlock_desc": "إزالة كلمة المرور من ملف PDF محمي",
        "unlock_btn": "إزالة القفل",
        "password": "كلمة المرور",
        "enter_password": "أدخل كلمة المرور",
        "show_password": "إظهار كلمة المرور",
        "wrong_password": "كلمة المرور غير صحيحة",
        "file_not_encrypted": "الملف غير محمي بكلمة مرور",
        "success_unlock": "تم إزالة كلمة المرور بنجاح",
        "locked": "محمي",
        "unlocked": "غير محمي",
        "tap_to_select": "أو اضغط للاختيار",
        "share": "مشاركة",
    },
    "en": {
        "app_title": "PDF Toolbox",
        "merge": "Merge PDF",
        "merge_desc": "Combine multiple PDF files into one",
        "split": "Split PDF",
        "split_desc": "Extract specific pages from a PDF",
        "dark_mode": "Dark",
        "light_mode": "Light",
        "drop_here": "Drop files here",
        "drop_pdf": "Drop PDF files here",
        "drop_images": "Drop images here",
        "browse": "Browse",
        "browse_pdf": "Select PDF File",
        "browse_images": "Select Images",
        "clear_all": "Clear All",
        "file": "File",
        "files": "Files",
        "page": "Page",
        "pages": "Pages",
        "select_pages": "Select Pages",
        "select_all": "Select All",
        "deselect_all": "Deselect All",
        "confirm": "Confirm",
        "cancel": "Cancel",
        "delete": "Delete",
        "merge_btn": "Merge PDF",
        "split_btn": "Split PDF",
        "extract_btn": "Extract Pages",
        "export_btn": "Export PDF",
        "save_as": "Save As",
        "file_name": "File Name",
        "pdf_name_hint": "Enter file name",
        "processing": "Processing...",
        "success": "Success!",
        "success_merge": "Files merged successfully",
        "success_extract": "Pages extracted successfully",
        "success_export": "PDF exported successfully",
        "error": "Error",
        "no_files": "No files added yet",
        "no_images": "No images added yet",
        "no_pdf": "No pages selected for extraction",
        "file_added": "File added",
        "page_count": "Pages",
        "size": "Size",
        "page_size": "Page Size",
        "orientation": "Orientation",
        "portrait": "Portrait",
        "landscape": "Landscape",
        "margin": "Margin",
        "output_type": "Output Type",
        "single_file": "Single file",
        "separate_files": "Separate files per page",
        "output_folder": "Output Folder",
        "select_folder": "Select Folder",
        "up": "Up",
        "down": "Down",
        "all_pages": "All Pages",
        "selected_pages": "Selected Pages",
        "settings": "Settings",
        "extract": "Extract",
        "sort": "Sort",
        "loading": "Loading...",
        "mm": "mm",
        "auto": "Auto",
        "image_settings": "Page Settings",
        "export_name": "Enter the file name for export:",
        "yes": "Yes",
        "no": "No",
        "confirm_overwrite": "File already exists. Do you want to overwrite?",
        "ready": "Ready",
        "or_browse": "or browse from your device",
        "supported_images": "Supported formats: JPG, PNG, WebP, BMP, GIF",
        "pages_selected": "page selected",
        "drag_active": "Release to drop files",
        "car": "Car Document",
        "car_desc": "Convert car ownership images to PDF with enhancement",
        "car_front": "Front Image",
        "car_back": "Back Image",
        "drop_car": "Drop ownership image here",
        "enhancement": "Image Enhancement",
        "enable_enhance": "Enable Enhancement",
        "brightness": "Brightness",
        "contrast": "Contrast",
        "sharpness": "Sharpness",
        "upscale": "Upscale",
        "upscale_off": "Off",
        "preview": "Preview",
        "no_images_car": "Please add both front and back images",
        "success_car": "PDF created successfully",
        "car_doc_pdf": "Car Document",
        "convert": "Convert",
        "convert_desc": "Convert PDF to images and vice versa",
        "pdf_to_images": "PDF to Images",
        "images_to_pdf": "Images to PDF",
        "output_format": "Output Format",
        "quality": "Quality",
        "success_convert": "Converted successfully",
        "no_pdf_selected": "No PDF selected",
        "merge_images": "Merge Images",
        "merge_images_desc": "Merge two images on one page",
        "layout": "Layout",
        "horizontal": "Horizontal",
        "vertical": "Vertical",
        "image1": "Image 1",
        "image2": "Image 2",
        "export_image": "Export as Image",
        "success_merge_images": "Images merged successfully",
        "no_images_merge": "Please add both images",
        "drop_image": "Drop image here",
        "unlock": "Remove Password",
        "unlock_desc": "Remove password protection from a PDF file",
        "unlock_btn": "Unlock PDF",
        "password": "Password",
        "enter_password": "Enter password",
        "show_password": "Show password",
        "wrong_password": "Wrong password",
        "file_not_encrypted": "File is not password-protected",
        "success_unlock": "Password removed successfully",
        "locked": "Locked",
        "unlocked": "Unlocked",
        "tap_to_select": "or tap to select",
        "share": "Share",
    },
}

current_lang = "ar"

def tr(key):
    return LANGUAGES[current_lang].get(key, key)

def set_language(lang):
    global current_lang
    if lang in LANGUAGES:
        current_lang = lang

def get_language():
    return current_lang


class Colors:
    PRIMARY = "#ff0000"
    PRIMARY_HOVER = "#cc0000"
    PRIMARY_LIGHT = "#ff4444"
    PRIMARY_GLOW = "#ff3333"
    ACCENT = "#ff4444"
    ACCENT_LIGHT = "#ff6666"

    SUCCESS = "#00c853"
    SUCCESS_LIGHT = "#69f0ae"
    DANGER = "#ff1744"
    DANGER_LIGHT = "#ff5252"
    WARNING = "#ffab00"
    INFO = "#ff4444"

    SURFACE = "#1a1a1a"
    SURFACE_ALT = "#2a2a2a"
    CARD = "#1a1a1a"
    CARD_HOVER = "#2a2a2a"
    BORDER = "#333333"
    BORDER_LIGHT = "#444444"
    TEXT = "#ffffff"
    TEXT_MUTED = "#888888"
    BG = "#0a0a0a"

    LIGHT_SURFACE = "#ffffff"
    LIGHT_SURFACE_ALT = "#e8e8e8"
    LIGHT_CARD = "#ffffff"
    LIGHT_CARD_HOVER = "#e8e8e8"
    LIGHT_BORDER = "#e0e0e0"
    LIGHT_TEXT = "#1a1a1a"
    LIGHT_TEXT_MUTED = "#666666"
    LIGHT_BG = "#f5f5f5"

    SIDEBAR_DARK = "#0A0A0A"
    SIDEBAR_LIGHT = "#ffffff"

    OVERLAY = "#0A0A0A"

    @classmethod
    def set_theme(cls, mode):
        if mode == "Dark":
            ctk.set_appearance_mode("dark")
        else:
            ctk.set_appearance_mode("light")


ICONS = {
    "logo": "PDF",
    "merge": "🔗",
    "split": "📑",
    "car": "🚗",
    "convert": "🔄",
    "merge_images": "🖼️",
    "unlock": "🔓",
    "pdf": "📄",
    "folder": "📁",
    "image": "📷",
    "lock": "🔒",
    "unlock_icon": "🔓",
    "key": "🔑",
    "eye": "👁️",
    "eye_off": "👁️‍🗨️",
    "close": "✕",
    "up": "▲",
    "down": "▼",
    "check": "✓",
    "arrow_right": "→",
    "plus": "+",
    "trash": "🗑️",
    "settings": "⚙️",
    "sun": "☀️",
    "moon": "🌙",
    "globe": "🌐",
    "share": "📤",
    "pages": "📃",
    "reset": "↺",
}


SECTION_ICON_COLORS = {
    "merge": {"bg": ("#ff0000", "#ff0000"), "glow": "#ff0000"},
    "split": {"bg": ("#ff6600", "#ff6600"), "glow": "#ff6600"},
    "unlock": {"bg": ("#00c853", "#00c853"), "glow": "#00c853"},
    "convert": {"bg": ("#3b82f6", "#3b82f6"), "glow": "#3b82f6"},
    "car": {"bg": ("#3b82f6", "#3b82f6"), "glow": "#3b82f6"},
    "merge_images": {"bg": ("#ec4899", "#ec4899"), "glow": "#ec4899"},
}

PAGE_SIZES = {
    "A4": (595, 842),
    "A3": (842, 1191),
    "Letter": (612, 792),
    "Legal": (612, 1008),
    "Auto": None,
}

FONT = ("Segoe UI", 13)
FONT_BOLD = ("Segoe UI", 13, "bold")
FONT_SMALL = ("Segoe UI", 11)
FONT_LARGE = ("Segoe UI", 20, "bold")
FONT_TITLE = ("Segoe UI", 28, "bold")
FONT_HUGE = ("Segoe UI", 36, "bold")
