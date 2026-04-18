
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageOps
import pytesseract
from pdf2image import convert_from_path
import sys
import os

def get_resource_path(relative_path):
    """ Dastur EXE bo'lganda fayllar yo'lini aniqlash """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# Tesseract yo'lini dinamik qilish
tess_path = get_resource_path(r'Tesseract-OCR\tesseract.exe')
pytesseract.pytesseract.tesseract_cmd = tess_path


class OCRApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Dastur oynasi sozlamalari
        self.title("KO'P TILLI MATN EXTRACTOR")
        self.iconbitmap(get_resource_path("unnamed.ico"))
        self.width = 1150
        self.height = 750

        # Oynani ekranning markaziga joylashtirish
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (self.width // 2)
        y = (screen_height // 2) - (self.height // 2)
        self.geometry(f"{self.width}x{self.height}+{x}+{y}")

        # Dizayn mavzusi
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Grid tizimi
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Yon panel (Sidebar) - Stil berilgan ---
        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=15, fg_color="#1a1c1e")
        self.sidebar.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")

        self.logo_label = ctk.CTkLabel(self.sidebar, text="💎 PRO\n VERSION",
                                       font=ctk.CTkFont(size=24, weight="bold", family="Arial"))
        self.logo_label.pack(pady=30, padx=20)

        # Tugmalar uchun umumiy dizayn
        btn_style = {"height": 40, "corner_radius": 10, "font": ("Segoe UI", 13, "bold")}

        self.btn_open = ctk.CTkButton(self.sidebar, text="📁 Faylni tanlash",
                                      fg_color="#3498db", hover_color="#2980b9",
                                      command=self.open_file, **btn_style)
        self.btn_open.pack(pady=12, padx=20, fill="x")

        self.btn_save = ctk.CTkButton(self.sidebar, text="💾 Matnni saqlash",
                                      fg_color="transparent", border_width=2, border_color="#3498db",
                                      command=self.save_text, **btn_style)
        self.btn_save.pack(pady=12, padx=20, fill="x")

        # Til tanlash bo'limi
        self.lang_label = ctk.CTkLabel(self.sidebar, text="🌐 Tilni tanlang:", text_color="#95a5a6")
        self.lang_label.pack(pady=(30, 0))

        self.languages = {
            "O'zbek (Lotin)": "uzb", "O'zbek (Krill)": "uzb_cyrl", "Rus tili": "rus",
            "Ingliz tili": "eng", "Xitoy (Soddalashgan)": "chi_sim", "Kores tili": "kor",
            "Yapon tili": "jpn", "Turk tili": "tur", "Arab tili": "ara",
            "Fors tili": "fas", "Hind tili": "hin", "Fransuz tili": "fra",
            "Nemis tili": "deu", "Qozoq tili": "kaz", "Tojik tili": "tgk", "Afg'on (Pushtu)": "pus"
        }

        self.lang_option = ctk.CTkOptionMenu(self.sidebar, values=list(self.languages.keys()),
                                             fg_color="#2c3e50", button_color="#34495e",
                                             dropdown_hover_color="#3498db")
        self.lang_option.pack(pady=10, padx=20, fill="x")
        self.lang_option.set("O'zbek (Lotin)")

        self.info_label = ctk.CTkLabel(self.sidebar, text="• Holat: Tayyor", text_color="#2ecc71")
        self.info_label.pack(side="bottom", pady=30)

        # --- Asosiy matn maydoni - Dizayn ---
        self.text_frame = ctk.CTkFrame(self, corner_radius=15)
        self.text_frame.grid(row=0, column=1, padx=(0, 15), pady=15, sticky="nsew")
        self.text_frame.grid_columnconfigure(0, weight=1)
        self.text_frame.grid_rowconfigure(0, weight=1)

        self.textbox = ctk.CTkTextbox(self.text_frame, font=("Consolas", 15),
                                      border_width=2, border_color="#2c3e50",
                                      fg_color="#0d1117", text_color="#e6edf3")
        self.textbox.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")

        # --- O'ng taraf Boshqaruv Paneli (Floating style) ---
        self.right_panel = ctk.CTkFrame(self, width=160, fg_color="transparent")
        self.right_panel.grid(row=0, column=2, padx=15, pady=15, sticky="ns")

        self.btn_copy = ctk.CTkButton(self.right_panel, text="📋 Nusxa olish",
                                      fg_color="#27ae60", hover_color="#219150",
                                      command=self.copy_to_clipboard, **btn_style)
        self.btn_copy.pack(pady=10, fill="x")

        self.btn_clear = ctk.CTkButton(self.right_panel, text="🗑️ Tozalash",
                                       fg_color="#c0392b", hover_color="#a93226",
                                       command=self.clear_text, **btn_style)
        self.btn_clear.pack(pady=10, fill="x")

    def show_message(self, title, message, icon="info"):
        """Modal oynani markazda ochish uchun yordamchi funksiya"""
        # Standart messagebox Windowsda avtomatik markazda ochiladi,
        # lekin biz uni dastur oynasiga bog'lab qo'yamiz
        if icon == "error":
            messagebox.showerror(title, message, parent=self)
        elif icon == "warning":
            messagebox.showwarning(title, message, parent=self)
        else:
            messagebox.showinfo(title, message, parent=self)

    def copy_to_clipboard(self):
        text = self.textbox.get("1.0", "end-1c")
        if text.strip():
            self.clipboard_clear()
            self.clipboard_append(text)
            self.show_message("Tayyor", "Matn nusxalandi!")
        else:
            self.show_message("Xato", "Nusxa olish uchun matn mavjud emas!", "warning")

    def clear_text(self):
        if messagebox.askyesno("Tasdiqlash", "Matnni o'chirishni xohlaysizmi?", parent=self):
            self.textbox.delete("1.0", "end")
            self.info_label.configure(text="• Tozalandi", text_color="#95a5a6")

    def open_file(self):
        file_path = filedialog.askopenfilename(
            parent=self,
            filetypes=[("Hamma fayllar", "*.png *.jpg *.jpeg *.pdf *.bmp *.tiff")]
        )

        if not file_path:
            return

        self.info_label.configure(text="• Ishlanmoqda...", text_color="#f1c40f")
        self.update_idletasks()

        try:
            tess_lang = self.languages[self.lang_option.get()]
            extracted_text = ""

            if file_path.lower().endswith('.pdf'):
                pages = convert_from_path(file_path, 300)
                for i, page in enumerate(pages):
                    processed = ImageOps.autocontrast(page.convert('L'))
                    extracted_text += f"\n--- Sahifa {i + 1} ---\n" + pytesseract.image_to_string(processed,
                                                                                                  lang=tess_lang)
            else:
                img = ImageOps.autocontrast(Image.open(file_path).convert('L'))
                extracted_text = pytesseract.image_to_string(img, lang=tess_lang)

            self.textbox.delete("1.0", "end")
            self.textbox.insert("1.0", extracted_text)
            self.info_label.configure(text="• Muvaffaqiyatli!", text_color="#2ecc71")

        except Exception as e:
            self.show_message("Xato", f"Xatolik yuz berdi: {str(e)}", "error")
            self.info_label.configure(text="• Xato yuz berdi", text_color="#e74c3c")

    def save_text(self):
        text = self.textbox.get("1.0", "end-1c")
        if not text.strip():
            self.show_message("Ogohlantirish", "Saqlash uchun matn yo'q!", "warning")
            return

        save_path = filedialog.asksaveasfilename(parent=self, defaultextension=".txt",
                                                 filetypes=[("Text files", "*.txt")])
        if save_path:
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(text)
            self.show_message("Tayyor", "Fayl saqlandi!")


if __name__ == "__main__":
    app = OCRApp()
    app.mainloop()