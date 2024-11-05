import tkinter as tk
import pymupdf
from PIL import Image, ImageTk
from PIL.ImageOps import expand
import os
from utils import *


class PageFrame(tk.Frame):
    def __init__(self, file, page, preview_image, frame_size=(100, 170)):
        super().__init__()
        self.preview_image = preview_image
        self.tk_img = None

        self.configure(borderwidth=1, relief="ridge", width=frame_size[0], height=frame_size[1])
        self.pack_propagate(False)

        self.header = tk.Frame(self)
        self.header.pack(side="top", fill="x")

        self.page_label = tk.Label(self.header, text=f"P.{page}", bg="yellow")
        self.page_label.pack(side="right")

        self.file_label = tk.Label(self.header, text=str(file), bg="red", anchor="w")
        self.file_label.pack(side="left", fill="x")

        self.image_frame = tk.Frame(self, bg="green")
        self.image_frame.pack(side="top", fill="both", expand=True)

        self.image_label = tk.Label(self.image_frame)
        self.image_label.pack(anchor="center")

        self.action_frame = tk.Frame(self, bg="blue")
        self.action_frame.pack(side="bottom", fill="x")

        self.delete_button = tk.Button(self.action_frame, text="DEL")
        self.delete_button.pack(side="left")

    def display_preview_image(self):
        img_frame_width = self.image_frame.winfo_width()
        img_frame_height = self.image_frame.winfo_height()
        print(img_frame_width, img_frame_height)

        resized_img = resize_to_fit(self.preview_image, max_width=img_frame_width, max_height=img_frame_height)
        self.tk_img = ImageTk.PhotoImage(resized_img)
        self.image_label.configure(image=self.tk_img)


class FillerFrame(tk.Frame):
    id = 0

    def __init__(self):
        super().__init__()
        self.configure(bg="grey")
        self.id = FillerFrame.id
        FillerFrame.id += 1

        self.add_button = tk.Button(self, text="+")
        self.add_button.pack(anchor="center", expand=True)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AdobeInGut")


        self.loaded_pdfs = []
        self.page_previews = []
        self.page_structure = []
        self.page_frames = []

    def load_pdf(self, file_path):
        pdf_obj = pymupdf.open(file_path)
        self.loaded_pdfs.append(pdf_obj)

        for i, page in enumerate(pdf_obj):

            # Create page preview image
            pix = page.get_pixmap()
            page_img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            self.page_structure.append({"file": os.path.basename(pdf_obj.name), "page": i, "preview": page_img})


    def display_pages(self):
        self.page_frames = []
        row = 0
        col = 0
        for page in self.page_structure:

            filler_frame = FillerFrame()
            filler_frame.grid(row=row, column=col, sticky="ns")
            page_frame = PageFrame(page["file"], page["page"], preview_image=page["preview"])
            page_frame.grid(row=row, column=col+1)
            self.page_frames.append(page_frame)

            col += 2

            if col >= 20:
                col = 0
                row += 1

        filler_frame = FillerFrame()
        filler_frame.grid(row=row, column=col, sticky="ns")

        self.update()
        for page_frame in self.page_frames:
            page_frame.display_preview_image()


if __name__ == '__main__':
    app = App()
    for i in range(1):
        app.load_pdf("files/editedByTeresa-Smartphone_Sensoren_zur_Stresserkennung-1.pdf")
    app.load_pdf("files/beispiel_rechnung.pdf")
    app.load_pdf("files/Vorschlag-Gutachten.pdf")
    app.display_pages()
    app.mainloop()