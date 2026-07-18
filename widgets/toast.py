import customtkinter as ctk


class Toast:
    _active = []

    @classmethod
    def show(cls, master, message, type="info", duration=3000):
        for t in cls._active[:]:
            try:
                t.destroy()
            except:
                pass
        cls._active.clear()

        colors = {
            "success": ("#10b981", "#052e16"),
            "error": ("#ef4444", "#450a0a"),
            "info": ("#06b6d4", "#0c1929"),
            "warning": ("#f59e0b", "#451a03"),
        }
        accent_bg, bg = colors.get(type, colors["info"])

        toast = ctk.CTkToplevel(master)
        toast.overrideredirect(True)
        toast.attributes("-topmost", True)
        toast.configure(fg_color=bg)

        toast.update_idletasks()
        m_x = master.winfo_rootx()
        m_y = master.winfo_rooty()
        m_w = master.winfo_width()
        x = m_x + m_w - 400
        y = m_y + 24

        toast.geometry(f"380x56+{x}+{y}")

        frame = ctk.CTkFrame(toast, fg_color=bg, corner_radius=12)
        frame.pack(fill="both", expand=True, padx=1, pady=1)

        indicator = ctk.CTkFrame(frame, width=4, fg_color=accent_bg, corner_radius=2)
        indicator.pack(side="left", fill="y", padx=(0, 10))

        icon_map = {
            "success": "✓",
            "error": "✕",
            "info": "ℹ",
            "warning": "⚠",
        }
        icon = icon_map.get(type, "")

        ctk.CTkLabel(frame, text=icon, font=("Segoe UI", 18, "bold"),
                      text_color=accent_bg, width=28).pack(side="left", padx=(0, 8))
        ctk.CTkLabel(frame, text=message, font=("Segoe UI", 13),
                      text_color=("#f1f5f9", "#f1f5f9"),
                      wraplength=260, justify="left").pack(side="left", fill="x", expand=True)

        cls._active.append(toast)
        toast.after(duration, lambda t=toast: cls._destroy(t))
        return toast

    @classmethod
    def _destroy(cls, toast):
        try:
            toast.destroy()
        except:
            pass
        if toast in cls._active:
            cls._active.remove(toast)
