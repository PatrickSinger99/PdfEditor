import tkinter as tk
from idlelib.textview import ViewFrame

import pymupdf
from PIL import Image, ImageTk
from PIL.ImageOps import expand
import os
from utils import *
from pdf_handler import PdfHandler
from tkinter.font import Font
from tkinter import filedialog


class PageFrame(tk.Frame):
    def __init__(self, *args, element, **kwargs):
        super().__init__(*args, **kwargs)

        self.element = element
        self.app = self.winfo_toplevel()
        self.tk_img = None

        self.pdf_name = self.app.handler.loaded_pdfs[self.element.page_objects[0].pdf_id]["name"]
        self.original_page = self.element.page_objects[0].original_index

        self.configure(width=160, height=200)
        self.pack_propagate(False)

        """ADD AREA"""
        self.add_frame = tk.Frame(self, bg=self.master.cget("bg"))
        self.add_frame.pack(side="left", fill="y")

        self.add_pdf_button = tk.Button(self.add_frame, text="+", font=Font(size=16), relief="flat", bd=0, fg="grey",
                                        bg=self.add_frame.cget("bg"), cursor="hand2",
                                        activebackground="grey")
        self.add_pdf_button.pack(anchor="center", expand=True, fill="both")

        self.add_pdf_button.bind("<Enter>", lambda e: self.add_pdf_button.configure(bg="light grey"))
        self.add_pdf_button.bind("<Leave>", lambda e: self.add_pdf_button.configure(bg=self.add_frame.cget("bg")))

        """PAGE DISPLAY AREA"""
        self.page_frame = tk.Frame(self, bg=self.cget("bg"))
        self.page_frame.pack(side="right", fill="both", expand=True)

        self.header = tk.Frame(self.page_frame, bg="light grey")
        self.header.pack(side="top", fill="x")

        self.page_label = tk.Label(self.header, text=f"P.{self.original_page}", bg=self.header.cget("bg"), fg="#2D2D2D")
        self.page_label.pack(side="right")

        self.file_label = tk.Label(self.header, text=self.pdf_name, bg=self.header.cget("bg"), anchor="w", fg="#2D2D2D")
        self.file_label.pack(side="left", fill="x")

        self.image_frame = tk.Frame(self.page_frame, bg=self.page_frame.cget("bg"))
        self.image_frame.pack(side="top", fill="both", expand=True)

        self.image_label = tk.Label(self.image_frame, text="Loading...", bg=self.image_frame.cget("bg"), fg="grey")
        self.image_label.pack(anchor="center")

    def display_preview_image(self):
        # Create image if it has not been done in a previous display call
        if self.tk_img is None:
            img_frame_width = self.image_frame.winfo_width()
            img_frame_height = self.image_frame.winfo_height()

            pix = self.element.page_objects[0].obj.get_pixmap()
            page_img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            resized_img = resize_to_fit(page_img, max_width=img_frame_width, max_height=img_frame_height)
            self.tk_img = ImageTk.PhotoImage(resized_img)

            self.image_label.configure(image=self.tk_img)


class CollapsedFrame(tk.Frame):
    def __init__(self, *args, element, **kwargs):
        super().__init__(*args, **kwargs)

        self.element = element
        self.app = self.winfo_toplevel()

        self.configure(width=140, height=160)
        self.pack_propagate(False)

        self.expand_button = tk.Button(self, text="expand", command=self.on_expand)
        self.expand_button.pack()

    def on_expand(self):
        new_elements = self.app.handler.expand_element(self.element.id)

        for elem in new_elements:
            self.app.add_page_frame(elem)

        self.app.display()

    def display_preview_image(self):
        pass


class App(tk.Tk):
    col = {
        "header": "#CC4B4C",
        "body": "#E9E9E0",
        "footer": "grey",
        "page_element": "white",
        "collapsed_element": "grey",
    }

    def __init__(self):
        super().__init__()
        self.title("AdobeInGut")
        self.geometry("1000x600")
        self.handler = PdfHandler()
        self.view_frames = {}

        """HEADER"""
        self.header = tk.Frame(self, bg=App.col["header"])
        self.header.pack(side="top", fill="x")

        # Program Title Label
        tk.Label(self.header, bg=self.header.cget("bg"), text="Title", font=Font(size=11)).pack(side="left")

        # BUTTON: Add pdf file
        self.add_pdf_button = tk.Button(self.header, text="Add PDF", command=self.on_add_new_pdf)
        self.add_pdf_button.pack(side="right")

        """BODY"""
        self.body = tk.Frame(self, bg=App.col["body"])
        self.body.pack(side="top", fill="both", expand=True)

        # Scrollable frame
        self.scrollable_frame = ScrollableFrame(self.body, bg=self.body.cget("bg"))
        self.scrollable_frame.pack(fill="both", expand=True)
        self.view = self.scrollable_frame.scrollable_frame  # Content is added to self.view

        """FOOTER"""
        self.footer = tk.Frame(self, bg=App.col["footer"])
        self.footer.pack(side="bottom", fill="x")

        # FRAME: Button Frame
        self.action_button_frame = tk.Frame(self.footer, bg=self.footer.cget("bg"))
        self.action_button_frame.pack(side="right", padx=2, pady=2)

        # BUTTON: Export to pdf
        self.export_button = tk.Button(self.action_button_frame, text="Create PDF")
        self.export_button.pack()

    def on_add_new_pdf(self, debug_filepath=None, collapsed_load=True):

        # Debug filepath overwrites filedialog
        if debug_filepath is not None:
            file_path = debug_filepath
        else:
            # Open a file dialog to allow the user to choose a PDF file
            file_path = filedialog.askopenfilename(
                title="Select a PDF file",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
            )

        # Check if the user selected a file (i.e., the file path is not empty)
        if file_path:
            new_elements = self.handler.add_pdf_file(file_path, collaped_load=collapsed_load)

            for elem in new_elements:
                if not elem.collapsed:
                    self.add_page_frame(elem)
                else:
                    self.add_collapsed_frame(elem)

            # Display changes
            if not debug_filepath:
                self.display()

    def add_page_frame(self, element):
        self.view_frames[element.id] = PageFrame(self.view, element=element,
                                                 bg=App.col["page_element"])

    def add_collapsed_frame(self, element):
        self.view_frames[element.id] = CollapsedFrame(self.view, element=element,
                                                      bg=App.col["collapsed_element"])

    def display(self):
        for element in self.view.winfo_children():
            element.grid_forget()

        # Determine current view size
        self.update()
        view_elem_width = 160  # TODO TEMP
        elements_per_row = int(self.view.winfo_width()/view_elem_width)

        for i, element in enumerate(self.handler.get_structure()):
            element_frame = self.view_frames[element.id]
            element_frame.grid(row=int(i/elements_per_row), column=i % elements_per_row, pady=4)

        self.update()
        for element in self.view.winfo_children():
            element.display_preview_image()


if __name__ == '__main__':
    app = App()

    app.on_add_new_pdf("files/aub.pdf")
    app.on_add_new_pdf("files/Android_iOS.pdf")
    app.on_add_new_pdf("files/master_krankmeldung_verlängerungsantrag.pdf", collapsed_load=False)


    app.mainloop()
