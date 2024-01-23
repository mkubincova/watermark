from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog
from tkinter import colorchooser
import os

ALLOWED_FILETYPES = [("PNG files", "*.png"), ("JPEG files", "*.jpg *.jpeg")]

class WatermarkApp:
    def __init__(self, root_window):
        self.root = root_window
        self.root.title("Watermark App")
        self.root.config(padx=50, pady=50)
        self.center_window()

        self.load_button = tk.Button(self.root, text="Load Image", command=self.load_image)
        self.load_button.grid(row=0, column=0, padx=10, pady=10)

        self.canvas = tk.Canvas(self.root, width=700, height=700, bg="black", highlightthickness=0, borderwidth=0)
        self.watermark = self.canvas.create_text(350, 350, anchor=tk.CENTER, text="YOUR WATERMARK", font=("Courier", 35, "bold"), fill="gray")
        self.canvas.grid(row=1, column=0, rowspan=20, pady=10, padx=10)

        self.watermark_label = tk.Label(text="Your watermark:")
        self.watermark_label.grid(row=1, column=1, sticky="W")
        self.watermark_input = tk.Entry()
        self.watermark_input.grid(row=2, column=1, sticky="NW")
        self.watermark_input.focus()
        self.watermark_input.bind('<KeyRelease>', self.on_input_change)

        self.font_size_label = tk.Label(text="Font size:")
        self.font_size_label.grid(row=3, column=1, sticky="W")
        self.font_size_input = tk.Entry()
        self.font_size_input.grid(row=4, column=1, sticky="NW")
        self.font_size_input.bind('<KeyRelease>', self.on_size_change)

        self.select_color_label = tk.Label(text="Watermark color:")
        self.select_color_label.grid(row=5, column=1, sticky="W")
        self.select_color_button = tk.Button(self.root, text='Select a Color', command=self.on_color_change)
        self.select_color_button.grid(row=6, column=1, sticky="NW")

        self.watermark_label = tk.Label(text="Alignment:")
        self.watermark_label.grid(row=7, column=1, sticky="W")
        self.options = {
            "center": {"x": 350, "y": 350, "anchor": "center"},
            "top left": {"x": 30, "y": 30, "anchor": "nw"},
            "top right": {"x": 670, "y": 30, "anchor": "ne"},
            "bottom left": {"x": 30, "y": 670, "anchor": "sw"},
            "bottom right": {"x": 670, "y": 670, "anchor": "se"},
        }
        self.position = tk.StringVar(self.root)
        self.position.set("center")  # default value
        self.position.trace("w", self.on_position_change)
        self.select_position = tk.OptionMenu(self.root, self.position, *self.options.keys())
        self.select_position.grid(row=8, column=1, sticky="NW")

        self.angle_label = tk.Label(text="Rotation angle (deg):")
        self.angle_label.grid(row=9, column=1, sticky="W")
        self.angle_input = tk.Entry()
        self.angle_input.grid(row=10, column=1, sticky="NW")
        self.angle_input.bind('<KeyRelease>', self.on_angle_change)

        self.save_button = tk.Button(self.root, text="Save Image", command=self.save_canvas)
        self.save_button.grid(row=11, column=1,  sticky="NW")

    def on_input_change(self, event):
        watermark_text = self.watermark_input.get()
        self.canvas.itemconfig(self.watermark, text=watermark_text)

    def on_color_change(self):
        color_code = tk.colorchooser.askcolor(title=r"Choose color")
        self.canvas.itemconfig(self.watermark, fill=color_code[1])

    def on_angle_change(self, event):
        angle = self.angle_input.get()
        if angle.isdigit():
            self.canvas.itemconfig(self.watermark, angle=float(angle))

    def on_size_change(self, event):
        size = self.font_size_input.get()
        if size.isdigit():
            self.canvas.itemconfig(self.watermark, font=("Courier", int(size), "bold"))

    def on_position_change(self, var, *args):
        position_name = self.root.getvar(var)
        position_vals = self.options[position_name]
        self.canvas.itemconfig(self.watermark, anchor=position_vals["anchor"])
        self.canvas.coords(self.watermark, position_vals["x"], position_vals["y"])

    def center_window(self):
        window_height = 1000
        window_width = 1000
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_cor = int((screen_width / 2) - (window_width / 2))
        y_cor = int((screen_height / 2) - (window_height / 2))
        self.root.geometry("{}x{}+{}+{}".format(window_width, window_height, x_cor, y_cor))

    def load_image(self):
        file_path = filedialog.askopenfilename(initialdir=os.path.join(os.path.expanduser("~"), "Desktop"), filetypes=ALLOWED_FILETYPES)

        if file_path:
            # Load the original image
            original_image = Image.open(file_path)

            # Resize the image to fit the canvas while maintaining proportions
            resized_image = self.resize_image(original_image, 700, 700)

            # Schedule the image update on the main Tkinter thread
            self.root.after(0, lambda: self.display_image(resized_image))

    def resize_image(self, image, target_width, target_height):
        # Calculate the aspect ratio
        aspect_ratio = image.width / image.height

        # Calculate the new dimensions while maintaining proportions
        if target_width / target_height > aspect_ratio:
            new_width = int(target_height * aspect_ratio)
            new_height = target_height
        else:
            new_width = target_width
            new_height = int(target_width / aspect_ratio)

        # Resize the image
        resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        return resized_image

    def display_image(self, image):
        # Convert the Pillow image to a PhotoImage object for display in Tkinter canvas
        tk_image = ImageTk.PhotoImage(image)
        # Update the canvas with the new image and place watermark on top
        self.canvas.config(width=image.width, height=image.height)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=tk_image)
        self.canvas.tag_raise(self.watermark)

        # Save a reference to the PhotoImage object to prevent it from being garbage collected
        self.canvas.image = tk_image

    def save_canvas(self):
        self.canvas.postscript(file="canvas_image.ps", colormode="color")

        # Ask the user for the destination file path
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=ALLOWED_FILETYPES)

        if file_path:
            # Open the PostScript file and save it as a PNG file at the chosen location
            image = Image.open("canvas_image.ps")
            image.save(file_path, format=file_path.split('.')[-1].upper())


if __name__ == "__main__":
    root = tk.Tk()
    app = WatermarkApp(root)
    root.mainloop()
