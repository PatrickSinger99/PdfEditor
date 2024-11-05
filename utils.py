from PIL import Image
import tkinter as tk


def resize_to_fit(image: Image.Image, max_width: int, max_height: int) -> Image.Image:
    # Get original dimensions
    original_width, original_height = image.size

    # Calculate the scaling factors
    width_ratio = max_width / original_width
    height_ratio = max_height / original_height

    # Choose the smallest scaling factor to ensure the image fits within the bounds
    scale_factor = min(width_ratio, height_ratio)

    # Calculate the new dimensions
    new_width = int(original_width * scale_factor)
    new_height = int(original_height * scale_factor)

    # Resize the image with the new dimensions
    resized_image = image.resize((new_width, new_height), 1)
    return resized_image


class ScrollableFrame(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resize_timer = None  # Prevents lagging by only rezizing content once mouse is let go after rezizing

        self.scrollable_canvas = tk.Canvas(self, bg=self.cget("bg"), highlightthickness=0, relief='ridge')

        # Frame inside canvas
        self.scrollable_frame = tk.Frame(self.scrollable_canvas, bg=self.scrollable_canvas.cget("bg"))
        self.scrollable_frame.pack(side="left")
        self.scrollable_frame.bind("<Configure>", lambda e: self.scrollable_canvas.configure(scrollregion=self.scrollable_canvas.bbox("all")))

        # Scrollbar for canvas
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.scrollable_canvas.yview, troughcolor=self.scrollable_canvas.cget("bg"))
        self.scrollbar.pack(side="right", fill="y")

        # Add a window with inner frame inside canvas. Link scrollbar to canvas
        self.scrollable_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.scrollable_canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollable_canvas.pack(side="bottom", fill="both", expand=True)

        # Bind scrollwheel to canvas to enable scrolling with mouse
        self.scrollable_frame.bind("<Enter>", lambda x: self.bind_canvas_to_mousewheel(self.scrollable_canvas))
        self.scrollable_frame.bind("<Leave>", lambda x: self.unbind_canvas_from_mousewheel(self.scrollable_canvas))

        # Bind canvas resize event to update the scrollable frame width
        self.scrollable_canvas.bind("<Configure>", self.on_canvas_configure)

    def bind_canvas_to_mousewheel(self, canvas):
        canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def unbind_canvas_from_mousewheel(self, canvas):
        canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        self.scrollable_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def on_canvas_configure(self, event):
        if self.resize_timer is not None:
            self.after_cancel(self.resize_timer)
        self.resize_timer = self.after(200, self.update_scrollable_frame_width, event.width)


    def update_scrollable_frame_width(self, width):
        self.scrollable_canvas.itemconfig(self.scrollable_canvas.create_window((0, 0), window=self.scrollable_frame,
                                                                               anchor="nw"), width=width)

        self.winfo_toplevel().display()